from pathlib import Path

import pytest

from src.synthesis.vosk import VoskSynthesis
from src.utils.config import TTSConfig, VoskConfig


@pytest.mark.skipif(
    not Path.home().joinpath(".cache", "vosk").exists(),
    reason="Vosk model cache not found - model will download on first run",
)
def test_vosk_synthesis_basic(tmp_path):
    config = VoskConfig(
        model_name="vosk-model-tts-ru-0.9-multi",
        speaker_id=2,
        audio_format="wav",
        cache_dir=Path.home() / ".cache" / "vosk",
        metrics_path=None,
    )
    tts_config = TTSConfig(
        engine=None,  # type: ignore[arg-type]
        model="vosk-model-tts-ru-0.9-multi",
        text_limit=1000,
        cache_dir=Path.home() / ".cache" / "vosk",
        model_url=None,
        model_config_url=None,
        model_checksum=None,
        model_size=None,
        speaker_id=2,
        length_scale=None,
        noise_scale=None,
        noise_w_scale=None,
        audio_format="wav",
        metrics_path=None,
    )
    synth = VoskSynthesis(config, tts_config)
    out_path = tmp_path / "test.wav"
    result = synth.synth("Привет мир", None, out_path)

    assert result.path.exists()
    assert result.duration_seconds > 0
    assert result.synth_ms > 0
    assert result.audio_format == "wav"


def test_vosk_synthesis_empty_text(tmp_path):
    config = VoskConfig(
        model_name="vosk-model-tts-ru-0.9-multi",
        speaker_id=0,
        audio_format="wav",
        cache_dir=tmp_path,
        metrics_path=None,
    )
    tts_config = TTSConfig(
        engine=None,  # type: ignore[arg-type]
        model="vosk-model-tts-ru-0.9-multi",
        text_limit=1000,
        cache_dir=tmp_path,
        model_url=None,
        model_config_url=None,
        model_checksum=None,
        model_size=None,
        speaker_id=0,
        length_scale=None,
        noise_scale=None,
        noise_w_scale=None,
        audio_format="wav",
        metrics_path=None,
    )
    synth = VoskSynthesis(config, tts_config)
    out_path = tmp_path / "test.wav"

    with pytest.raises(ValueError, match="empty text"):
        synth.synth("", None, out_path)


def test_vosk_synthesis_text_too_long(tmp_path):
    config = VoskConfig(
        model_name="vosk-model-tts-ru-0.9-multi",
        speaker_id=0,
        audio_format="wav",
        cache_dir=tmp_path,
        metrics_path=None,
    )
    tts_config = TTSConfig(
        engine=None,  # type: ignore[arg-type]
        model="vosk-model-tts-ru-0.9-multi",
        text_limit=10,
        cache_dir=tmp_path,
        model_url=None,
        model_config_url=None,
        model_checksum=None,
        model_size=None,
        speaker_id=0,
        length_scale=None,
        noise_scale=None,
        noise_w_scale=None,
        audio_format="wav",
        metrics_path=None,
    )
    synth = VoskSynthesis(config, tts_config)
    out_path = tmp_path / "test.wav"

    with pytest.raises(ValueError, match="text too long"):
        synth.synth("a" * 20, None, out_path)

