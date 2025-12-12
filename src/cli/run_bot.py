import os
import sys
import tempfile
from pathlib import Path

from telegram.ext import Application

from src.bot.handlers import setup_handlers
from src.bot.worker import Worker
from src.synthesis import create_synth
from src.utils.config import load_config
from src.utils.logging import get_logger, setup_logging
from src.utils.queue import InMemoryQueue


def main() -> int:
    config = load_config()
    setup_logging(config.log_level)
    log = get_logger(__name__)

    if not config.bot_token:
        log.error("BOT_TOKEN is required")
        return 1
    if not config.whitelist:
        log.error("WHITELIST is empty - access denied for everyone")
        return 1

    queue = InMemoryQueue()
    provider = os.getenv("SYNTH_PROVIDER") or os.getenv("TTS_ENGINE")
    synth = create_synth(config, provider=provider)
    active_engine = provider or config.tts.engine.value
    log.info("synthesis engine=%s model=%s", active_engine, config.tts.model)

    log.info("warming up synthesis engine...")
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            warmup_path = Path(tmp.name)
        try:
            result = synth.synth("тест", None, warmup_path)
            log.info(
                "warmup completed load_ms=%.1f synth_ms=%.1f duration=%.2fs",
                result.model_load_ms or 0.0,
                result.synth_ms,
                result.duration_seconds,
            )
        finally:
            warmup_path.unlink(missing_ok=True)  # type: ignore[arg-type]
    except Exception as exc:  # noqa: BLE001
        log.warning("warmup failed: %s (bot will continue)", exc)

    worker = Worker(queue=queue, synth=synth)

    app = Application.builder().token(config.bot_token).build()
    app.bot_data["config"] = config
    app.bot_data["worker"] = worker

    for handler in setup_handlers(worker):
        app.add_handler(handler)

    async def on_error(update, context):
        log.exception("Unhandled error", exc_info=context.error)
        if config.debug and update and update.effective_chat:
            trace = context.error
            try:
                import traceback

                trace_str = "".join(traceback.format_exception(None, context.error, context.error.__traceback__))
            except Exception:
                trace_str = str(trace)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ошибка:\n{trace_str}")

    log.info("Starting bot...")
    app.add_error_handler(on_error)
    app.run_polling(close_loop=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())


