import hashlib
import tempfile
import urllib.request
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import soundfile as sf
from pydub import AudioSegment

from src.synthesis.interface import SynthesisProvider, SynthesisResult
from src.utils.config import PiperConfig, TTSConfig
from src.utils.logging import get_logger, log_metrics, measure_ms

try:
    from piper.voice import PiperVoice, SynthesisConfig as PiperSynthesisConfig
except Exception as exc:  # noqa: BLE001
    raise ImportError("piper-tts is required for PiperSynthesis") from exc


class PiperSynthesis(SynthesisProvider):
    def __init__(self, config: PiperConfig, tts_config: TTSConfig) -> None:
        self.config = config
        self.tts_config = tts_config
        self.log = get_logger(__name__)
        self._voice: Optional[PiperVoice] = None
        self._model_load_ms: float | None = None
        self.metrics_label = "piper_tts"

    def _model_paths(self) -> tuple[Path, Path]:
        base_dir = self.config.cache_dir
        base_dir.mkdir(parents=True, exist_ok=True)
        model_name = self.config.model
        model_path = base_dir / f"{model_name}.onnx"
        config_path = base_dir / f"{model_name}.onnx.json"
        return model_path, config_path

    def _download_file(self, url: str, dest: Path, expected_checksum: Optional[str], expected_size: Optional[int]) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = dest.parent / f"{dest.name}.download"
        try:
            with urllib.request.urlopen(url) as resp:  # noqa: S310
                data = resp.read()
            if expected_size is not None and len(data) != expected_size:
                raise ValueError(f"size mismatch for {url}: expected {expected_size}, got {len(data)}")
            if expected_checksum:
                sha = hashlib.sha256(data).hexdigest()
                if sha != expected_checksum:
                    raise ValueError(f"checksum mismatch for {url}")
            tmp_path.write_bytes(data)
            tmp_path.replace(dest)
        finally:
            tmp_path.unlink(missing_ok=True)  # type: ignore[arg-type]

    def _ensure_voice(self) -> None:
        if self._voice is not None:
            return

        start_ms = measure_ms()
        model_path, config_path = self._model_paths()
        if not model_path.exists() or not config_path.exists():
            if not self.config.model_url:
                raise FileNotFoundError(f"piper model not found and no download url provided for {self.config.model}")
            cfg_url = self.config.model_config_url or f"{self.config.model_url}.json"
            self.log.info("downloading piper model from %s", self.config.model_url)
            self._download_file(self.config.model_url, model_path, self.config.model_checksum, self.config.model_size)
            self._download_file(cfg_url, config_path, None, None)

        self._voice = PiperVoice.load(
            model_path=model_path,
            config_path=config_path,
            use_cuda=self.config.use_cuda,
        )
        self._model_load_ms = measure_ms() - start_ms
        self.log.info(
            "piper model loaded name=%s load_ms=%.1f sample_rate=%s speakers=%s",
            self.config.model,
            self._model_load_ms,
            self._voice.config.sample_rate if self._voice else "unknown",
            self._voice.config.num_speakers if self._voice else "unknown",
        )

    def _build_syn_config(self) -> PiperSynthesisConfig:
        return PiperSynthesisConfig(
            speaker_id=self.config.speaker_id,
            length_scale=self.config.length_scale,
            noise_scale=self.config.noise_scale,
            noise_w_scale=self.config.noise_w_scale,
            normalize_audio=True,
            volume=1.0,
        )

    def synth(self, text: str, prefix: str | None, out_path: Path) -> SynthesisResult:
        if not text.strip():
            raise ValueError("empty text")
        full_text = f"{prefix}. {text}" if prefix else text
        if len(full_text) > self.tts_config.text_limit:
            raise ValueError("text too long")

        self._ensure_voice()
        assert self._voice is not None

        start_ms = measure_ms()
        try:
            syn_cfg = self._build_syn_config()
            chunks: Iterable = self._voice.synthesize(full_text, syn_config=syn_cfg)  # type: ignore[arg-type]
            audio_arrays: list[np.ndarray] = []
            sample_rate = self._voice.config.sample_rate
            for chunk in chunks:
                audio_arrays.append(chunk.audio_float_array)
        except Exception as exc:  # noqa: BLE001
            raise OSError(f"piper synthesis failed: {exc}") from exc

        if not audio_arrays:
            raise OSError("piper returned no audio")

        audio_np = np.concatenate(audio_arrays)
        out_path = out_path.with_suffix(f".{self.config.audio_format}")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if self.config.audio_format == "wav":
            sf.write(out_path, audio_np, sample_rate)
        else:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = Path(tmp.name)
            try:
                sf.write(tmp_path, audio_np, sample_rate)
                audio_seg = AudioSegment.from_wav(tmp_path)
                audio_seg.export(out_path, format="mp3")
            finally:
                tmp_path.unlink(missing_ok=True)  # type: ignore[arg-type]

        synth_ms = measure_ms() - start_ms
        duration_seconds = float(len(audio_np) / sample_rate) if sample_rate else 0.0
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


__all__ = ["PiperSynthesis"]

