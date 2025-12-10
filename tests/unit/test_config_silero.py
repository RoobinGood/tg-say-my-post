from pathlib import Path

import pytest

from src.utils import config as config_module


def _clear_env(monkeypatch):
    for key in [
        "TTS_ENGINE",
        "TTS_MODEL",
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


def test_load_config_from_file(tmp_path, monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("TTS_MODEL", "v5_ru")
    monkeypatch.setenv("TTS_AUDIO_FORMAT", "mp3")
    monkeypatch.setenv("TTS_SPEAKER", "test_speaker")
    monkeypatch.setenv("TTS_LANGUAGE", "en")
    monkeypatch.setenv("TTS_SAMPLE_RATE", "22050")
    monkeypatch.setenv("TTS_OUTPUT_DIR", str(tmp_path / "out"))
    monkeypatch.setenv("TTS_TEXT_LIMIT", "1200")
    env_file = tmp_path / ".env"
    out_dir = tmp_path / "out"
    env_file.write_text(
        "\n".join(
            [
                "TTS_MODEL=v5_ru",
                "TTS_SPEAKER=test_speaker",
                "TTS_LANGUAGE=en",
                "TTS_AUDIO_FORMAT=mp3",
                f"TTS_OUTPUT_DIR={out_dir}",
                "TTS_SAMPLE_RATE=22050",
                "TTS_DEVICE=cpu",
                "TTS_TEXT_LIMIT=1200",
            ]
        ),
        encoding="utf-8",
    )
    cfg = config_module.load_config(env_file)
    assert cfg.silero.model_id == "v5_ru"
    assert cfg.silero.speaker == "test_speaker"
    assert cfg.silero.language == "en"
    assert cfg.silero.audio_format == "mp3"
    assert cfg.silero.sample_rate == 22050
    assert cfg.silero.output_dir == out_dir.resolve()
    assert cfg.silero.max_length == 1200
    assert out_dir.exists()
    assert cfg.silero.metrics_path is None


def test_load_config_invalid_format(tmp_path, monkeypatch):
    _clear_env(monkeypatch)
    env_file = tmp_path / ".env"
    env_file.write_text("TTS_AUDIO_FORMAT=flac", encoding="utf-8")
    with pytest.raises(ValueError):
        config_module.load_config(env_file)


def test_load_config_with_metrics_file(tmp_path, monkeypatch):
    _clear_env(monkeypatch)
    metrics_file = tmp_path / "metrics" / "silero.log"
    monkeypatch.setenv("TTS_MODEL", "v5_ru")
    monkeypatch.setenv("TTS_METRICS_FILE", str(metrics_file))
    cfg = config_module.load_config()
    assert cfg.silero.metrics_path == metrics_file.resolve()
    assert metrics_file.parent.exists()

