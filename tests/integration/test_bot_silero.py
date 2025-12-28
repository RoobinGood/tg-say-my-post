from types import SimpleNamespace
from pathlib import Path

import pytest

from src.bot.worker import Worker
from src.synthesis.interface import SynthesisResult
from src.utils.config import load_config
from src.utils.queue import InMemoryQueue


class DummyBot:
    def __init__(self):
        self.voice_calls: list[int] = []
        self.text_calls: list[str] = []

    async def send_voice(self, chat_id, voice, caption=None, reply_to_message_id=None):
        self.voice_calls.append(reply_to_message_id)
        data = voice.read()
        assert data
        voice.close()

    async def send_message(self, chat_id, text):
        self.text_calls.append(text)


class DummyMessage:
    def __init__(self, text: str, chat_id: int = 42, message_id: int = 1):
        self.text = text
        self.chat_id = chat_id
        self.message_id = message_id
        self.forward_from = None
        self.forward_from_chat = None
        self.from_user = SimpleNamespace(full_name="Tester")


@pytest.mark.asyncio
async def test_bot_sends_voice_on_success(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("LLM_ENABLED=false\nTTS_MODEL=v5_ru\n", encoding="utf-8")
    cfg = load_config(env_file)
    queue = InMemoryQueue()

    class DummySynth:
        def synth(self, text, prefix, out_path: Path):
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(b"audio")
            return SynthesisResult(
                path=out_path,
                duration_seconds=1.0,
                synth_ms=2.0,
                model_load_ms=3.0,
                audio_format="ogg",
            )

    worker = Worker(queue, DummySynth())
    bot = DummyBot()
    msg = DummyMessage("hello")
    update = SimpleNamespace(effective_message=msg)
    context = SimpleNamespace(bot=bot, bot_data={"config": cfg})

    await worker.handle_message(update, context)

    assert bot.voice_calls == [msg.message_id]
    assert bot.text_calls == []
    assert queue.is_empty(msg.chat_id)


@pytest.mark.asyncio
async def test_bot_fallback_when_synth_fails(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("LLM_ENABLED=false\nTTS_MODEL=v5_ru\n", encoding="utf-8")
    cfg = load_config(env_file)
    queue = InMemoryQueue()

    class FailingSynth:
        def synth(self, text, prefix, out_path: Path):
            raise FileNotFoundError("missing model")

    worker = Worker(queue, FailingSynth())
    bot = DummyBot()
    msg = DummyMessage("fail")
    update = SimpleNamespace(effective_message=msg)
    context = SimpleNamespace(bot=bot, bot_data={"config": cfg})

    await worker.handle_message(update, context)

    assert bot.voice_calls == []
    assert bot.text_calls
    assert bot.text_calls[0].startswith("синтез недоступен")
    assert queue.is_empty(msg.chat_id)



