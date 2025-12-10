from src.bot.models import IncomingItem, SourceType


def build_prefix(item: IncomingItem) -> str | None:
    if item.source_type == SourceType.FORWARDED_USER and item.sender_name:
        return f"сообщение от пользователя {item.sender_name}"
    if item.source_type == SourceType.FORWARDED_CHANNEL and item.channel_title:
        return f"пост из канала {item.channel_title}"
    if item.source_type in (SourceType.FORWARDED_USER, SourceType.FORWARDED_CHANNEL):
        return None
    return None


