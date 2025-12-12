import tempfile
from pathlib import Path
from typing import Optional

import soundfile as sf
from pydub import AudioSegment

from src.synthesis.interface import SynthesisProvider, SynthesisResult
from src.utils.config import TTSConfig, VoskConfig
from src.utils.logging import get_logger, log_metrics, measure_ms

try:
    from vosk_tts import Model, Synth
except Exception as exc:  # noqa: BLE001
    raise ImportError("vosk-tts is required for VoskSynthesis") from exc


class VoskSynthesis(SynthesisProvider):
    def __init__(self, config: VoskConfig, tts_config: TTSConfig) -> None:
        self.config = config
        self.tts_config = tts_config
        self.log = get_logger(__name__)
        self._model: Optional[Model] = None
        self._synth: Optional[Synth] = None
        self._model_load_ms: float | None = None
        self.metrics_label = "vosk_tts"

    def _ensure_model(self) -> None:
        if self._model is not None and self._synth is not None:
            return

        start_ms = measure_ms()
        self._model = Model(model_name=self.config.model_name)
        self._synth = Synth(self._model)
        self._model_load_ms = measure_ms() - start_ms
        self.log.info(
            "vosk model loaded name=%s speaker_id=%s load_ms=%.1f",
            self.config.model_name,
            self.config.speaker_id,
            self._model_load_ms,
        )

    def synth(self, text: str, prefix: str | None, out_path: Path) -> SynthesisResult:
        if not text.strip():
            raise ValueError("empty text")
        full_text = f"{prefix}. {text}" if prefix else text
        if len(full_text) > self.tts_config.text_limit:
            raise ValueError("text too long")

        self._ensure_model()
        assert self._model is not None
        assert self._synth is not None

        start_ms = measure_ms()
        try:
            synth_path = out_path.with_suffix(".wav")
            self._synth.synth(full_text, str(synth_path), speaker_id=self.config.speaker_id)
        except Exception as exc:  # noqa: BLE001
            raise OSError(f"vosk synthesis failed: {exc}") from exc

        if not synth_path.exists():
            raise OSError("vosk returned no audio file")

        out_path = out_path.with_suffix(f".{self.config.audio_format}")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        audio_data, sample_rate = sf.read(synth_path)
        duration_seconds = float(len(audio_data) / sample_rate) if sample_rate else 0.0

        if self.config.audio_format == "wav":
            synth_path.replace(out_path)
        else:
            try:
                audio_seg = AudioSegment.from_wav(synth_path)
                audio_seg.export(out_path, format="mp3")
            finally:
                synth_path.unlink(missing_ok=True)  # type: ignore[arg-type]

        synth_ms = measure_ms() - start_ms
        result = SynthesisResult(
            path=out_path,
            duration_seconds=duration_seconds,
            synth_ms=synth_ms,
            model_load_ms=self._model_load_ms,
            audio_format=self.config.audio_format,
        )
        log_metrics(
            self.log,
            self.metrics_label,
            load_ms=self._model_load_ms,
            synth_ms=synth_ms,
            duration_seconds=duration_seconds,
            metrics_file=self.config.metrics_path,
        )
        return result


__all__ = ["VoskSynthesis"]

