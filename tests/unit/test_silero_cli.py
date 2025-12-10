from pathlib import Path

import pytest

from src.cli import silero_tts
from src.synthesis.interface import SynthesisResult
from src.synthesis.silero import SileroSynthesis


def _clear_env(monkeypatch):
    for key in [
        "SILERO_VOICE",
        "SILERO_MODEL_ID",
        "SILERO_SPEAKER",
        "SILERO_LANGUAGE",
        "SILERO_FORMAT",
        "SILERO_OUTPUT_DIR",
        "SILERO_SAMPLE_RATE",
        "SILERO_DEVICE",
        "SILERO_MAX_LENGTH",
        "SILERO_MODEL_PATH",
        "SILERO_CACHE_DIR",
        "SILERO_METRICS_FILE",
    ]:
        monkeypatch.delenv(key, raising=False)


def test_cli_text_ok(monkeypatch, tmp_path, capsys):
    _clear_env(monkeypatch)
    out = tmp_path / "out.wav"

    def fake_synth(self, text, prefix, out_path):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(b"audio")
        return SynthesisResult(path=out_path, duration_seconds=1.0, synth_ms=2.0, model_load_ms=3.0, audio_format="wav")

    monkeypatch.setattr(silero_tts.SileroSynthesis, "synth", fake_synth)
    rc = silero_tts.main(["--text", "hello", "--out", str(out)])
    assert rc == 0
    assert out.exists()


def test_cli_text_file_and_length(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    out = tmp_path / "out.mp3"
    text_file = tmp_path / "text.txt"
    text_file.write_text("hi", encoding="utf-8")

    def fake_synth(self, text, prefix, out_path):
        out_path.write_bytes(b"audio")
        return SynthesisResult(path=out_path, duration_seconds=1.0, synth_ms=2.0, model_load_ms=None, audio_format="mp3")

    monkeypatch.setattr(silero_tts.SileroSynthesis, "synth", fake_synth)
    rc = silero_tts.main(["--text-file", str(text_file), "--out", str(out), "--format", "mp3"])
    assert rc == 0
    assert out.exists()

    long_text = "x" * 2001
    text_file.write_text(long_text, encoding="utf-8")
    rc_long = silero_tts.main(["--text-file", str(text_file), "--out", str(out)])
    assert rc_long == 2


def test_silero_synth_saves_and_metrics(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    dummy_audio = [0.1] * 16000

    class DummyModel:
        def to(self, device):
            return self

        def apply_tts(self, text: str, speaker: str, sample_rate: int):
            return dummy_audio

    cfg = silero_tts.load_config()
    synth = SileroSynthesis(cfg.silero)
    synth._model = DummyModel()  # bypass real load
    out = tmp_path / "out.wav"
    result = synth.synth("hello", None, out)
    assert result.path.exists()
    assert result.duration_seconds > 0


def test_cli_missing_config_file(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    missing_cfg = tmp_path / "absent.env"
    out = tmp_path / "out.wav"
    rc = silero_tts.main(["--text", "hi", "--out", str(out), "--config", str(missing_cfg)])
    assert rc == 3
    assert not out.exists()


def test_cli_unwritable_output_dir(monkeypatch, tmp_path):
    _clear_env(monkeypatch)
    blocker = tmp_path / "file"
    blocker.write_text("content", encoding="utf-8")
    out = blocker / "nested" / "out.wav"
    rc = silero_tts.main(["--text", "hi", "--out", str(out)])
    assert rc == 4
    assert not out.exists()

