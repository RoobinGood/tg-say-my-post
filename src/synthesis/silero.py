import importlib.util
import tempfile
from pathlib import Path
import sys

import numpy as np
import soundfile as sf
import torch
from pydub import AudioSegment

from src.synthesis.interface import SynthesisProvider, SynthesisResult
from src.utils.config import SileroConfig
from src.utils.logging import get_logger, log_metrics, measure_ms


class SileroSynthesis(SynthesisProvider):
    def __init__(self, config: SileroConfig) -> None:
        self.config = config
        self.log = get_logger(__name__)
        self._model = None
        self._model_load_ms: float | None = None
        self._active_model_id = config.model_id
        self._active_speaker = config.speaker

    def _ensure_model(self) -> None:
        if self._model is not None:
            return
        start_ms = measure_ms()
        repo_dir = Path(self.config.model_path) if self.config.model_path else Path(torch.hub.get_dir()) / "snakers4_silero-models_master"
        if not repo_dir.exists():
            raise FileNotFoundError(f"Silero repo cache not found at {repo_dir}. Run once with torch.hub to download.")

        original_path = list(sys.path)
        original_modules = {name: sys.modules.get(name) for name in ["src", "src.silero", "silero"]}
        try:
            project_root = Path(__file__).resolve().parents[2]
            project_src = project_root / "src"
            filtered = [
                p
                for p in original_path
                if Path(p).resolve() not in {project_root, project_src} and p != ""
            ]
            sys.path = [str(repo_dir / "src")] + filtered
            for name in ["src", "src.silero", "silero"]:
                sys.modules.pop(name, None)

            module = importlib.import_module("silero.silero")
            silero_tts = getattr(module, "silero_tts")
            model_id = self.config.model_id
            model_tuple = silero_tts(language=self.config.language, speaker=model_id)
            if not isinstance(model_tuple, tuple):
                raise ValueError("silero_tts returned unexpected result")
            model = model_tuple[0]
            self._active_model_id = model_id
        finally:
            sys.path = original_path
            for name, module in original_modules.items():
                if module is not None:
                    sys.modules[name] = module
        device = torch.device(self.config.device)
        moved = model.to(device) if hasattr(model, "to") else model
        self._model = moved if moved is not None else model
        self._model_load_ms = measure_ms() - start_ms
        self.log.info(
            "silero model loaded id=%s speaker=%s load_ms=%.1f",
            self._active_model_id,
            self._active_speaker,
            self._model_load_ms,
        )

    def synth(self, text: str, prefix: str | None, out_path: Path) -> SynthesisResult:
        if not text.strip():
            raise ValueError("empty text")
        full_text = f"{prefix}. {text}" if prefix else text
        if len(full_text) > self.config.max_length:
            raise ValueError("text too long")

        self._ensure_model()
        assert self._model is not None
        start_ms = measure_ms()
        allowed_rates = {8000, 24000, 48000}
        sample_rate = self.config.sample_rate if self.config.sample_rate in allowed_rates else 48000
        speaker = self._active_speaker
        available_speakers = getattr(self._model, "speakers", None)
        if available_speakers and speaker not in available_speakers:
            speaker = available_speakers[0]
            self.log.warning("speaker %s not available in model %s, fallback to %s", self._active_speaker, self._active_model_id, speaker)
        audio = self._model.apply_tts(
            text=full_text,
            speaker=speaker,
            sample_rate=sample_rate,
        )
        synth_ms = measure_ms() - start_ms
        out_path = out_path.with_suffix(f".{self.config.audio_format}")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        audio_np = audio.cpu().numpy() if isinstance(audio, torch.Tensor) else np.array(audio)
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
            "silero_tts",
            load_ms=self._model_load_ms,
            synth_ms=synth_ms,
            duration_seconds=duration_seconds,
            metrics_file=self.config.metrics_path,
        )
        return result


