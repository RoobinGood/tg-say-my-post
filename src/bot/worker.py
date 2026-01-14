import tempfile
import traceback
from pathlib import Path
from typing import Set

from telegram import InputFile, Message, Update
from telegram.error import BadRequest, TimedOut
from telegram.ext import ContextTypes

from src.bot.prefix import build_prefix
from src.bot.validators import MAX_LEN, extract_incoming
from src.preprocessing import preprocess_text
from src.synthesis.interface import SynthesisProvider
from src.utils.logging import format_metrics, get_logger, log_failure
from src.utils.queue import InMemoryQueue, JobStatus


class Worker:
    def __init__(self, queue: InMemoryQueue, synth: SynthesisProvider) -> None:
        self.queue = queue
        self.synth = synth
        self.processing: Set[int] = set()
        self.log = get_logger(__name__)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message = update.effective_message
        if message is None:
            return
        cfg = getattr(context, "bot_data", {}).get("config") if hasattr(context, "bot_data") else None
        text_limit = getattr(getattr(cfg, "tts", None), "text_limit", None)
        incoming, error = extract_incoming(update, max_len=text_limit or MAX_LEN)
        if error:
            await message.reply_text(error)
            return
        assert incoming is not None
        llm_config = getattr(cfg, "llm", None) if cfg else None
        incoming_text = await preprocess_text(incoming.text, llm_config)
        if not incoming_text.strip():
            await message.reply_text("озвучивать нечего")
            return
        incoming.text = incoming_text

        job_id = f"{incoming.chat_id}-{incoming.message_id}"
        self.queue.enqueue(incoming.chat_id, job_id, incoming)
        await self._drain(incoming.chat_id, message, context)

    async def _drain(self, chat_id: int, message: Message, context: ContextTypes.DEFAULT_TYPE) -> None:
        if chat_id in self.processing:
            return
        self.processing.add(chat_id)
        try:
            while (job := self.queue.next_job(chat_id)) is not None:
                self.queue.update_status(job, JobStatus.SYNTHESIZING)
                incoming = job.payload
                prefix = build_prefix(incoming)
                cfg = getattr(context, "bot_data", {}).get("config") if hasattr(context, "bot_data") else None
                llm_config = getattr(cfg, "llm", None) if cfg else None
                if prefix:
                    prefix = await preprocess_text(prefix, llm_config)
                out_path: Path | None = None
                self.log.info(
                    "processing job chat=%s mid=%s prefix=%s order=%s",
                    incoming.chat_id,
                    incoming.message_id,
                    prefix or "none",
                    job.order,
                )
                bot = getattr(context, "bot", None)
                try:
                    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
                        out_path = Path(tmp.name)
                    result = self.synth.synth(incoming.text, prefix, out_path)
                    out_path = result.path
                    label = getattr(self.synth, "metrics_label", self.synth.__class__.__name__.lower())
                    metrics_line = format_metrics(
                        label,
                        load_ms=result.model_load_ms,
                        synth_ms=result.synth_ms,
                        duration_seconds=result.duration_seconds,
                    )
                    file_size_mb = out_path.stat().st_size / (1024 * 1024) if out_path.exists() else 0.0
                    self.log.info(
                        "synth ok chat=%s mid=%s %s file_size_mb=%.2f",
                        incoming.chat_id,
                        incoming.message_id,
                        metrics_line,
                        file_size_mb,
                    )
                    try:
                        from src.utils.logging import measure_ms
                        send_start_ms = measure_ms()
                        self.log.info("starting voice send chat=%s mid=%s file_size_mb=%.2f", incoming.chat_id, incoming.message_id, file_size_mb)
                        timeout_kwargs = {}
                        if cfg:
                            timeout_kwargs = {
                                "read_timeout": float(getattr(cfg, "bot_read_timeout", 0) or 0),
                                "write_timeout": float(getattr(cfg, "bot_write_timeout", 0) or 0),
                                "connect_timeout": float(getattr(cfg, "bot_connect_timeout", 0) or 0),
                                "pool_timeout": float(getattr(cfg, "bot_pool_timeout", 0) or 0),
                            }
                        with out_path.open("rb") as voice_file:
                            voice_input = InputFile(voice_file, filename=out_path.name)
                            if bot:
                                await bot.send_voice(
                                    chat_id=incoming.chat_id,
                                    voice=voice_input,
                                    caption=None,
                                    reply_to_message_id=incoming.message_id,
                                    **timeout_kwargs,
                                )
                            else:
                                await message.reply_voice(
                                    voice=voice_input,
                                    caption=None,
                                    reply_to_message_id=incoming.message_id,
                                    **timeout_kwargs,
                                )
                        send_ms = measure_ms() - send_start_ms
                        self.log.info("voice send completed chat=%s mid=%s send_ms=%.1f", incoming.chat_id, incoming.message_id, send_ms)
                        self.queue.update_status(job, JobStatus.SENT)
                    except BadRequest as br_exc_voice:
                        self.log.warning("Voice send failed: %s file_size_mb=%.2f", br_exc_voice, file_size_mb)
                        text = (
                            "Не удалось отправить голос. "
                            "Разрешите боту голосовые: Settings → Privacy and Security → Voice messages "
                            "(включить для всех или добавить бота в исключения)."
                        )
                        if bot:
                            await bot.send_message(chat_id=incoming.chat_id, text=text)
                        else:
                            await message.reply_text(text)
                        self.queue.update_status(job, JobStatus.FAILED, error=str(br_exc_voice))
                    except TimedOut as timeout_exc:
                        self.log.warning(
                            "Voice send timed out: %s file_size_mb=%.2f duration=%.1fs",
                            timeout_exc,
                            file_size_mb,
                            result.duration_seconds,
                        )
                        if file_size_mb > 20:
                            text = f"Файл слишком большой ({file_size_mb:.1f} МБ). Telegram ограничивает голосовые сообщения до 20 МБ. Попробуйте сократить текст."
                        else:
                            text = f"Таймаут при отправке файла ({file_size_mb:.1f} МБ, {result.duration_seconds:.0f} сек). Попробуйте сократить текст или увеличьте BOT_WRITE_TIMEOUT/BOT_POOL_TIMEOUT."
                        if bot:
                            await bot.send_message(chat_id=incoming.chat_id, text=text)
                        else:
                            await message.reply_text(text)
                        self.queue.update_status(job, JobStatus.FAILED, error=str(timeout_exc))
                except Exception as exc:  # noqa: BLE001
                    self.log.exception("Failed to synth/send: %s", exc)
                    cfg = getattr(context, "bot_data", {}).get("config") if hasattr(context, "bot_data") else None
                    debug = bool(getattr(cfg, "debug", False))
                    metrics_path = getattr(getattr(cfg, "tts", None), "metrics_path", None) if cfg else None
                    trace = traceback.format_exc()
                    if isinstance(exc, FileNotFoundError):
                        base_text = "синтез недоступен: отсутствует модель или путь"
                    elif isinstance(exc, OSError):
                        base_text = "синтез недоступен: ошибка записи/чтения"
                    else:
                        base_text = "не удалось озвучить сообщение"
                    label = getattr(self.synth, "metrics_label", self.synth.__class__.__name__.lower())
                    log_failure(self.log, label, error=str(exc), metrics_file=metrics_path)
                    if bot:
                        text = base_text
                        if debug:
                            text = f"{text}\n\n{trace}"
                        await bot.send_message(chat_id=incoming.chat_id, text=text)
                    else:
                        text = base_text
                        if debug:
                            text = f"{text}\n\n{trace}"
                        await message.reply_text(text)
                    self.queue.update_status(job, JobStatus.FAILED, error=str(exc))
                finally:
                    if out_path:
                        try:
                            out_path.unlink(missing_ok=True)  # type: ignore[attr-defined]
                        except Exception:  # noqa: BLE001
                            pass
                self.queue.pop_job(chat_id)
        finally:
            self.processing.discard(chat_id)


