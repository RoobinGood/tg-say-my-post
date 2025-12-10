import os
from datetime import datetime, timezone
from typing import Optional, Tuple

from telegram import Message, Update

from src.bot.models import IncomingItem, SourceType

DEFAULT_MAX_LEN = 2000
CONFIG_MAX_LEN = int(os.getenv("TTS_TEXT_LIMIT", DEFAULT_MAX_LEN))
MAX_LEN = CONFIG_MAX_LEN


def _has_attachment(message: Message) -> bool:
    return bool(getattr(message, "effective_attachment", None))


def _get_sender_name(message: Message) -> Optional[str]:
    forward_from = getattr(message, "forward_from", None)
    if forward_from:
        return forward_from.full_name
    forward_origin = getattr(message, "forward_origin", None)
    if forward_origin:
        sender_user = getattr(forward_origin, "sender_user", None)
        if sender_user:
            return sender_user.full_name
        sender_name = getattr(forward_origin, "sender_name", None)
        if sender_name:
            return sender_name
    from_user = getattr(message, "from_user", None)
    return from_user.full_name if from_user else None


def _get_channel_title(message: Message) -> Optional[str]:
    forward_from_chat = getattr(message, "forward_from_chat", None)
    if forward_from_chat:
        return forward_from_chat.title
    forward_origin = getattr(message, "forward_origin", None)
    if forward_origin:
        chat = getattr(forward_origin, "chat", None)
        if chat:
            return getattr(chat, "title", None)
    return None


def extract_incoming(update: Update, *, max_len: int = MAX_LEN) -> Tuple[Optional[IncomingItem], Optional[str]]:
    message: Optional[Message] = getattr(update, "effective_message", None)
    if message is None:
        return None, "озвучивать нечего"

    raw_text = getattr(message, "text", None)
    raw_caption = getattr(message, "caption", None)
    text = (raw_text or raw_caption or "").strip()

    if not text:
        if _has_attachment(message):
            return None, "не могу озвучить этот формат, пришлите текст"
        return None, "озвучивать нечего"
    if len(text) > max_len:
        return None, f"текст превышает {max_len} символов"

    forward_from = getattr(message, "forward_from", None)
    forward_from_chat = getattr(message, "forward_from_chat", None)
    forward_origin = getattr(message, "forward_origin", None)

    if forward_from:
        source_type = SourceType.FORWARDED_USER
    elif forward_from_chat:
        source_type = SourceType.FORWARDED_CHANNEL
    elif forward_origin:
        if getattr(forward_origin, "sender_user", None) or getattr(forward_origin, "sender_name", None):
            source_type = SourceType.FORWARDED_USER
        elif getattr(forward_origin, "chat", None):
            source_type = SourceType.FORWARDED_CHANNEL
        else:
            source_type = SourceType.DIRECT
    else:
        source_type = SourceType.DIRECT

    incoming = IncomingItem(
        message_id=message.message_id,
        chat_id=message.chat_id,
        text=text,
        source_type=source_type,
        sender_name=_get_sender_name(message),
        channel_title=_get_channel_title(message),
        created_at=datetime.now(timezone.utc),
    )
    return incoming, None


