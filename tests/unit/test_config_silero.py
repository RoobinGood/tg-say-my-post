from pathlib import Path

import pytest

from src.utils import config as config_module


def _clear_env(monkeypatch):
    for key in [
        "SILERO_VOICE",
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


def test_load_config_from_file(tmp_path, monkeypatch):
    _clear_env(monkeypatch)
    env_file = tmp_path / ".env"
    out_dir = tmp_path / "out"
    env_file.write_text(
        "\n".join(
            [
                "SILERO_MODEL_ID=v5_ru",
                "SILERO_SPEAKER=test_speaker",
                "SILERO_LANGUAGE=en",
                "SILERO_FORMAT=mp3",
                f"SILERO_OUTPUT_DIR={out_dir}",
                "SILERO_SAMPLE_RATE=22050",
                "SILERO_DEVICE=cpu",
                "SILERO_MAX_LENGTH=1200",
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
    env_file.write_text("SILERO_FORMAT=flac", encoding="utf-8")
    with pytest.raises(ValueError):
        config_module.load_config(env_file)


def test_load_config_with_metrics_file(tmp_path, monkeypatch):
    _clear_env(monkeypatch)
    metrics_file = tmp_path / "metrics" / "silero.log"
    monkeypatch.setenv("SILERO_METRICS_FILE", str(metrics_file))
    cfg = config_module.load_config()
    assert cfg.silero.metrics_path == metrics_file.resolve()
    assert metrics_file.parent.exists()

