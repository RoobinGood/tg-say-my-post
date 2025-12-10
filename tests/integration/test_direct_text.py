import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.bot.worker import Worker
from src.synthesis.stub import StubSynthesis
from src.utils.queue import InMemoryQueue


class DummyBot:
    def __init__(self):
        self.voice_calls = []
        self.text_calls = []

    async def send_voice(self, chat_id, voice, caption=None, reply_to_message_id=None):
        self.voice_calls.append(reply_to_message_id)
        data = voice.read()
        assert data
        voice.close()

    async def send_message(self, chat_id, text):
        self.text_calls.append(text)


class DummyMessage:
    def __init__(self, text: str):
        self.text = text
        self.message_id = 1
        self.chat_id = 42
        self.forward_from = None
        self.forward_from_chat = None
        self.from_user = SimpleNamespace(full_name="Tester")


@pytest.mark.asyncio
async def test_direct_text_flow(tmp_path: Path):
    stub_audio = tmp_path / "example.mp3"
    stub_audio.write_bytes(b"ID3stub")

    synth = StubSynthesis(stub_audio)
    queue = InMemoryQueue()
    worker = Worker(queue, synth)
    bot = DummyBot()

    msg = DummyMessage("hello")
    update = SimpleNamespace(effective_message=msg)
    context = SimpleNamespace(bot=bot)

    await worker.handle_message(update, context)

    assert bot.voice_calls == [1]
    assert bot.text_calls == []
    assert queue.is_empty(msg.chat_id)


