from types import SimpleNamespace

from src.bot.models import IncomingItem, SourceType
from src.bot.prefix import build_prefix


def make_item(source_type: SourceType, sender=None, channel=None):
    return IncomingItem(
        message_id=1,
        chat_id=1,
        text="hi",
        source_type=source_type,
        sender_name=sender,
        channel_title=channel,
    )


def test_prefix_forwarded_user_with_name():
    item = make_item(SourceType.FORWARDED_USER, sender="Alice")
    assert build_prefix(item) == "сообщение от пользователя Alice"


def test_prefix_forwarded_channel_with_title():
    item = make_item(SourceType.FORWARDED_CHANNEL, channel="News")
    assert build_prefix(item) == "пост из канала News"


def test_prefix_forwarded_user_no_name():
    item = make_item(SourceType.FORWARDED_USER, sender=None)
    assert build_prefix(item) is None


def test_prefix_direct():
    item = make_item(SourceType.DIRECT)
    assert build_prefix(item) is None


