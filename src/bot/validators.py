from datetime import datetime, timezone
from typing import Optional, Tuple

from telegram import Message, Update

from src.bot.models import IncomingItem, SourceType

MAX_LEN = 2000


def _get_sender_name(message: Message) -> Optional[str]:
    forward_from = getattr(message, "forward_from", None)
    if forward_from:
        return forward_from.full_name
    from_user = getattr(message, "from_user", None)
    return from_user.full_name if from_user else None


def _get_channel_title(message: Message) -> Optional[str]:
    forward_from_chat = getattr(message, "forward_from_chat", None)
    if forward_from_chat:
        return forward_from_chat.title
    return None


def extract_incoming(update: Update) -> Tuple[Optional[IncomingItem], Optional[str]]:
    message: Optional[Message] = getattr(update, "effective_message", None)
    if message is None:
        return None, "озвучивать нечего"

    text = (getattr(message, "text", "") or "").strip()
    if not text:
        return None, "озвучивать нечего"
    if len(text) > MAX_LEN:
        return None, "текст превышает 2000 символов"

    forward_from = getattr(message, "forward_from", None)
    forward_from_chat = getattr(message, "forward_from_chat", None)

    if forward_from:
        source_type = SourceType.FORWARDED_USER
    elif forward_from_chat:
        source_type = SourceType.FORWARDED_CHANNEL
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


