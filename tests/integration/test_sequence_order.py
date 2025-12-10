from pathlib import Path
from types import SimpleNamespace

import pytest

from src.bot.worker import Worker
from src.utils.queue import InMemoryQueue


class FakeSynth:
    def __init__(self, stub: Path):
        self.stub = stub

    def synth(self, text: str, prefix: str | None, out_path: Path) -> Path:
        out_path.write_bytes(self.stub.read_bytes())
        return out_path


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
    def __init__(self, text: str, message_id: int):
        self.text = text
        self.message_id = message_id
        self.chat_id = 42
        self.forward_from = None
        self.forward_from_chat = None
        self.from_user = SimpleNamespace(full_name="Tester")


@pytest.mark.asyncio
async def test_sequence_order(tmp_path: Path):
    stub_audio = tmp_path / "example.mp3"
    stub_audio.write_bytes(b"ID3stub")
    synth = FakeSynth(stub_audio)
    queue = InMemoryQueue()
    worker = Worker(queue, synth)
    bot = DummyBot()

    contexts = []
    for idx in range(1, 6):
        msg = DummyMessage(f"m{idx}", message_id=idx)
        update = SimpleNamespace(effective_message=msg)
        context = SimpleNamespace(bot=bot)
        await worker.handle_message(update, context)
        contexts.append(context)

    assert bot.voice_calls == [1, 2, 3, 4, 5]
    assert queue.is_empty(42)


