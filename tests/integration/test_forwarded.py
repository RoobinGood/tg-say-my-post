from pathlib import Path
from types import SimpleNamespace

import pytest

from src.bot.worker import Worker
from src.synthesis.interface import SynthesisResult
from src.utils.queue import InMemoryQueue


class FakeSynth:
    def __init__(self, stub: Path):
        self.stub = stub
        self.prefixes = []

    def synth(self, text: str, prefix: str | None, out_path: Path) -> SynthesisResult:
        self.prefixes.append(prefix)
        out_path.write_bytes(self.stub.read_bytes())
        return SynthesisResult(
            path=out_path,
            duration_seconds=0.5,
            synth_ms=1.0,
            model_load_ms=None,
            audio_format="ogg",
        )


class DummyBot:
    def __init__(self):
        self.voice_calls = []
        self.text_calls = []

    async def send_voice(self, chat_id, voice, caption=None, reply_to_message_id=None):
        self.voice_calls.append(reply_to_message_id)
        voice.read()
        voice.close()

    async def send_message(self, chat_id, text):
        self.text_calls.append(text)


class DummyMessage:
    def __init__(self, text: str, message_id: int, forwarded_user=None, forwarded_chat=None):
        self.text = text
        self.message_id = message_id
        self.chat_id = 42
        self.forward_from = forwarded_user
        self.forward_from_chat = forwarded_chat
        self.from_user = SimpleNamespace(full_name="Tester")
        self.reply_audio_called = 0
        self.reply_text_called = 0
        self.reply_audio_ids = []

    async def reply_audio(self, audio, caption=None, reply_to_message_id=None):
        self.reply_audio_called += 1
        self.reply_audio_ids.append(reply_to_message_id)
        audio.read()
        audio.close()

    async def reply_text(self, text: str):
        self.reply_text_called += 1


@pytest.mark.asyncio
async def test_forwarded_prefixes(tmp_path: Path):
    stub_audio = tmp_path / "example.mp3"
    stub_audio.write_bytes(b"ID3stub")
    synth = FakeSynth(stub_audio)
    queue = InMemoryQueue()
    worker = Worker(queue, synth)
    bot = DummyBot()

    user = SimpleNamespace(full_name="Alice")
    chan = SimpleNamespace(title="News")

    msg_user = DummyMessage("hello", message_id=1, forwarded_user=user)
    update_user = SimpleNamespace(effective_message=msg_user)
    context_user = SimpleNamespace(bot=bot)

    msg_chan = DummyMessage("world", message_id=2, forwarded_chat=chan)
    update_chan = SimpleNamespace(effective_message=msg_chan)
    context_chan = SimpleNamespace(bot=bot)

    await worker.handle_message(update_user, context_user)
    await worker.handle_message(update_chan, context_chan)

    assert synth.prefixes == [
        "сообщение от пользователя Alice",
        "пост из канала News",
    ]
    assert bot.voice_calls == [1, 2]
    assert queue.is_empty(msg_user.chat_id)


