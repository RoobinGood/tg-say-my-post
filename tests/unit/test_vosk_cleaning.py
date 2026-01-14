from pathlib import Path

from src.synthesis.vosk import VoskSynthesis
from src.utils.config import TTSConfig, VoskConfig


def _make_synth(tmp_path: Path) -> VoskSynthesis:
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
    return VoskSynthesis(config, tts_config)


def test_vosk_filter_normalizes_unicode_dashes(tmp_path: Path) -> None:
    synth = _make_synth(tmp_path)
    text = "Привет – мир — тест − ок"

    cleaned = synth._filter_unsupported_chars(text)

    assert "–" not in cleaned
    assert "—" not in cleaned
    assert "−" not in cleaned
    assert "-" in cleaned

