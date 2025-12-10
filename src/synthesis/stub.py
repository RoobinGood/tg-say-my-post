import shutil
from pathlib import Path

from pydub import AudioSegment

from src.synthesis.interface import SynthesisResult
from src.utils.logging import get_logger, measure_ms


class StubSynthesis:
    def __init__(self, audio_stub_path: Path) -> None:
        self.audio_stub_path = audio_stub_path
        self.log = get_logger(__name__)

    def synth(self, text: str, prefix: str | None, out_path: Path) -> SynthesisResult:
        if not text.strip():
            raise ValueError("empty text")
        if len(text) > 2000:
            raise ValueError("text too long")
        if not self.audio_stub_path.exists():
            raise FileNotFoundError(f"stub audio missing: {self.audio_stub_path}")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # Try to produce OGG/Opus for voice messages; fallback to raw copy if export fails.
        start_ms = measure_ms()
        try:
            audio = AudioSegment.from_file(self.audio_stub_path)
            audio = audio.set_channels(1).set_frame_rate(48000)
            audio.export(out_path, format="ogg", codec="libopus")
            self.log.info("stub synth (ogg/opus) prefix=%s target=%s", prefix or "none", out_path)
        except Exception as exc:  # noqa: BLE001
            self.log.warning("ogg export failed, fallback copy: %s", exc)
            shutil.copyfile(self.audio_stub_path, out_path)
            self.log.info("stub synth (fallback copy) prefix=%s target=%s", prefix or "none", out_path)
        try:
            duration_seconds = AudioSegment.from_file(out_path).duration_seconds
        except Exception as exc:  # noqa: BLE001
            self.log.warning("duration read failed, assume zero: %s", exc)
            duration_seconds = 0.0
        synth_ms = measure_ms() - start_ms
        return SynthesisResult(
            path=out_path,
            duration_seconds=duration_seconds,
            synth_ms=synth_ms,
            model_load_ms=None,
            audio_format=out_path.suffix.lstrip(".").lower(),
        )



