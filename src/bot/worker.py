import tempfile
import traceback
from pathlib import Path
from typing import Set

from telegram import Message, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from src.bot.prefix import build_prefix
from src.bot.text_preprocess import preprocess_text
from src.bot.validators import MAX_LEN, extract_incoming
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
        incoming_text = preprocess_text(incoming.text)
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
                    self.log.info(
                        "synth ok chat=%s mid=%s %s",
                        incoming.chat_id,
                        incoming.message_id,
                        metrics_line,
                    )
                    try:
                        if bot:
                            await bot.send_voice(
                                chat_id=incoming.chat_id,
                                voice=out_path.open("rb"),
                                caption=None,
                                reply_to_message_id=incoming.message_id,
                            )
                        else:
                            await message.reply_voice(
                                voice=out_path.open("rb"),
                                caption=None,
                                reply_to_message_id=incoming.message_id,
                            )
                        self.queue.update_status(job, JobStatus.SENT)
                    except BadRequest as br_exc_voice:
                        self.log.warning("Voice send failed: %s", br_exc_voice)
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


