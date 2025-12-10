from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class SourceType(str, Enum):
    DIRECT = "direct"
    FORWARDED_USER = "forwarded_user"
    FORWARDED_CHANNEL = "forwarded_channel"


@dataclass
class IncomingItem:
    message_id: int
    chat_id: int
    text: str
    source_type: SourceType
    sender_name: Optional[str] = None
    channel_title: Optional[str] = None
    created_at: datetime = datetime.now(timezone.utc)


