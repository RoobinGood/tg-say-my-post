from pathlib import Path

import pytest

from src.cli import silero_tts
from src.synthesis.interface import SynthesisResult
from src.synthesis.silero import SileroSynthesis
from src.utils.config import load_config


def _clear_env(monkeypatch):
    for key in [
        "TTS_MODEL",
        "TTS_ENGINE",
        "TTS_TEXT_LIMIT",
        "TTS_CACHE_DIR",
        "TTS_MODEL_URL",
        "TTS_MODEL_CONFIG_URL",
        "TTS_MODEL_CHECKSUM",
        "TTS_MODEL_SIZE",
        "TTS_SPEAKER_ID",
        "TTS_SPEAKER",
        "TTS_LANGUAGE",
        "TTS_SAMPLE_RATE",
        "TTS_DEVICE",
        "TTS_AUDIO_FORMAT",
        "TTS_MODEL_PATH",
        "TTS_OUTPUT_DIR",
        "TTS_METRICS_FILE",
    ]:
        monkeypatch.delenv(key, raising=False)
    monkeypatch.delenv("LLM_ENABLED", raising=False)
    monkeypatch.setenv("LLM_ENABLED", "false")


def test_cli_text_ok(monkeypatch, tmp_path, capsys):
    _clear_env(monkeypatch)
    monkeypatch.setenv("TTS_MODEL", "v5_ru")
    env_file = tmp_path / ".env"
    env_file.write_text("LLM_ENABLED=false\nTTS_MODEL=v5_ru\n", encoding="utf-8")
    out = tmp_path / "out.wav"

    def fake_synth(self, text, prefix, out_path):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(b"audio")
        return SynthesisResult(path=out_path, duration_seconds=1.0, synth_ms=2.0, model_load_ms=3.0, audio_format="wav")

    monkeypatch.setattr(silero_tts.SileroSynthesis, "synth", fake_synth)
    rc = silero_tts.main(["--text", "hello", "--out", str(out), "--config", str(env_file)])
    assert rc == 0
    assert out.exists()


def test_cli_text_file_and_length(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    monkeypatch.setenv("TTS_MODEL", "v5_ru")
    env_file = tmp_path / ".env"
    env_file.write_text("LLM_ENABLED=false\nTTS_MODEL=v5_ru\n", encoding="utf-8")
    out = tmp_path / "out.mp3"
    text_file = tmp_path / "text.txt"
    text_file.write_text("hi", encoding="utf-8")

    def fake_synth(self, text, prefix, out_path):
        out_path.write_bytes(b"audio")
        return SynthesisResult(path=out_path, duration_seconds=1.0, synth_ms=2.0, model_load_ms=None, audio_format="mp3")

    monkeypatch.setattr(silero_tts.SileroSynthesis, "synth", fake_synth)
    rc = silero_tts.main(["--text-file", str(text_file), "--out", str(out), "--format", "mp3", "--config", str(env_file)])
    assert rc == 0
    assert out.exists()

    long_text = "x" * 2001
    text_file.write_text(long_text, encoding="utf-8")
    rc_long = silero_tts.main(["--text-file", str(text_file), "--out", str(out), "--config", str(env_file)])
    assert rc_long == 2


def test_silero_synth_saves_and_metrics(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    monkeypatch.setenv("TTS_MODEL", "v5_ru")
    env_file = tmp_path / ".env"
    env_file.write_text("LLM_ENABLED=false\nTTS_MODEL=v5_ru\n", encoding="utf-8")
    dummy_audio = [0.1] * 16000

    class DummyModel:
        def to(self, device):
            return self

        def apply_tts(self, text: str, speaker: str, sample_rate: int):
            return dummy_audio

    cfg = load_config(env_file)
    synth = SileroSynthesis(cfg.silero)
    synth._model = DummyModel()  # bypass real load
    out = tmp_path / "out.wav"
    result = synth.synth("hello", None, out)
    assert result.path.exists()
    assert result.duration_seconds > 0


def test_cli_missing_config_file(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    monkeypatch.setenv("TTS_MODEL", "v5_ru")
    missing_cfg = tmp_path / "absent.env"
    out = tmp_path / "out.wav"
    rc = silero_tts.main(["--text", "hi", "--out", str(out), "--config", str(missing_cfg)])
    assert rc == 3
    assert not out.exists()


def test_cli_unwritable_output_dir(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    monkeypatch.setenv("TTS_MODEL", "v5_ru")
    env_file = tmp_path / ".env"
    env_file.write_text("LLM_ENABLED=false\nTTS_MODEL=v5_ru\n", encoding="utf-8")
    blocker = tmp_path / "file"
    blocker.write_text("content", encoding="utf-8")
    out = blocker / "nested" / "out.wav"
    rc = silero_tts.main(["--text", "hi", "--out", str(out), "--config", str(env_file)])
    assert rc == 4
    assert not out.exists()

