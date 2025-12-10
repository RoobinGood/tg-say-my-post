from types import SimpleNamespace

from src.bot.validators import MAX_LEN, extract_incoming
from src.utils.queue import InMemoryQueue


def make_message(
    text: str | None,
    *,
    caption: str | None = None,
    forward_from=None,
    forward_from_chat=None,
    attachment=None,
) -> SimpleNamespace:
    return SimpleNamespace(
        message_id=1,
        chat_id=123,
        text=text,
        caption=caption,
        forward_from=forward_from,
        forward_from_chat=forward_from_chat,
        effective_attachment=attachment,
        from_user=SimpleNamespace(full_name="User"),
    )


def make_update(msg: SimpleNamespace) -> SimpleNamespace:
    return SimpleNamespace(effective_message=msg)


def test_extract_incoming_ok():
    msg = make_message("hello")
    inc, err = extract_incoming(make_update(msg))
    assert err is None
    assert inc is not None
    assert inc.text == "hello"
    assert inc.chat_id == 123


def test_extract_incoming_empty():
    msg = make_message("   ")
    inc, err = extract_incoming(make_update(msg))
    assert inc is None
    assert err == "озвучивать нечего"


def test_extract_incoming_long():
    msg = make_message("a" * (MAX_LEN + 1))
    inc, err = extract_incoming(make_update(msg))
    assert inc is None
    assert err == "текст превышает 2000 символов"


def test_extract_incoming_caption_and_channel():
    channel = SimpleNamespace(title="News")
    msg = make_message(None, caption="latest update", forward_from_chat=channel)
    inc, err = extract_incoming(make_update(msg))
    assert err is None
    assert inc is not None
    assert inc.text == "latest update"
    assert inc.source_type.value == "forwarded_channel"
    assert inc.channel_title == "News"


def test_extract_incoming_attachment_only():
    msg = make_message(None, attachment="photo")
    inc, err = extract_incoming(make_update(msg))
    assert inc is None
    assert err == "не могу озвучить этот формат, пришлите текст"


def test_queue_ordering():
    q = InMemoryQueue()
    j1 = q.enqueue(chat_id=1, job_id="a", payload="p1")
    j2 = q.enqueue(chat_id=1, job_id="b", payload="p2")
    assert j1.order == 1
    assert j2.order == 2
    assert q.next_job(1).job_id == "a"
    q.pop_job(1)
    assert q.next_job(1).job_id == "b"


