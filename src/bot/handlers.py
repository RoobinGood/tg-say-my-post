from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

from src.bot.worker import Worker
from src.utils.config import Config
from src.utils.logging import get_logger


def is_allowed(user_id: int | None, whitelist: set[int]) -> bool:
    if not whitelist:
        return False
    if user_id is None:
        return False
    return user_id in whitelist


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cfg: Config = context.bot_data["config"]
    log = get_logger(__name__)
    if not is_allowed(update.effective_user.id if update.effective_user else None, cfg.whitelist):
        log.info("start denied for user=%s", update.effective_user.id if update.effective_user else None)
        return
    msg = (
        "Я озвучиваю текстовые сообщения и пересланные посты.\n"
        "- лимит 2000 символов\n"
        "- переслано от пользователя: скажу «сообщение от пользователя <имя>»\n"
        "- переслано из канала: скажу «пост из канала <название>»"
    )
    await update.message.reply_text(msg)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cfg: Config = context.bot_data["config"]
    worker: Worker = context.bot_data["worker"]
    log = get_logger(__name__)

    message = update.effective_message
    chat_id = update.effective_chat.id if update.effective_chat else None
    user_id = update.effective_user.id if update.effective_user else None
    msg_id = message.message_id if message else None
    has_text = False
    has_caption = False
    if message is not None:
        raw_text = getattr(message, "text", None)
        raw_caption = getattr(message, "caption", None)
        has_text = bool(raw_text and raw_text.strip())
        has_caption = bool(raw_caption and raw_caption.strip())
    msg_type_obj = getattr(message, "effective_attachment", None) if message is not None else None
    msg_type = msg_type_obj.__class__.__name__ if msg_type_obj is not None else ("text" if has_text else "unknown")
    log.info(
        "incoming update chat=%s user=%s mid=%s type=%s has_text=%s has_caption=%s",
        chat_id,
        user_id,
        msg_id,
        msg_type,
        has_text,
        has_caption,
    )

    if not is_allowed(user_id, cfg.whitelist):
        log.info("access denied for user=%s", user_id)
        return

    if not message:
        return
    await worker.handle_message(update, context)


def setup_handlers(worker: Worker) -> list:
    return [
        CommandHandler("start", start),
        MessageHandler(filters.ALL & ~filters.COMMAND, handle_message),
    ]


