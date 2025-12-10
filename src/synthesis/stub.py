import shutil
from pathlib import Path

from pydub import AudioSegment

from src.utils.logging import get_logger


class StubSynthesis:
    def __init__(self, audio_stub_path: Path) -> None:
        self.audio_stub_path = audio_stub_path
        self.log = get_logger(__name__)

    def synth(self, text: str, prefix: str | None, out_path: Path) -> Path:
        if not text.strip():
            raise ValueError("empty text")
        if len(text) > 2000:
            raise ValueError("text too long")
        if not self.audio_stub_path.exists():
            raise FileNotFoundError(f"stub audio missing: {self.audio_stub_path}")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # Try to produce OGG/Opus for voice messages; fallback to raw copy if export fails.
        try:
            audio = AudioSegment.from_file(self.audio_stub_path)
            audio = audio.set_channels(1).set_frame_rate(48000)
            audio.export(out_path, format="ogg", codec="libopus")
            self.log.info("stub synth (ogg/opus) prefix=%s target=%s", prefix or "none", out_path)
        except Exception as exc:  # noqa: BLE001
            self.log.warning("ogg export failed, fallback copy: %s", exc)
            shutil.copyfile(self.audio_stub_path, out_path)
            self.log.info("stub synth (fallback copy) prefix=%s target=%s", prefix or "none", out_path)
        return out_path



