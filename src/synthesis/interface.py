from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class SynthesisResult:
    path: Path
    duration_seconds: float
    synth_ms: float
    model_load_ms: float | None = None
    audio_format: str | None = None


class SynthesisProvider(Protocol):
    def synth(self, text: str, prefix: str | None, out_path: Path) -> SynthesisResult:
        ...

