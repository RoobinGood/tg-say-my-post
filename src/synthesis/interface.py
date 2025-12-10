from pathlib import Path
from typing import Protocol


class SynthesisProvider(Protocol):
    def synth(self, text: str, prefix: str | None, out_path: Path) -> Path:
        ...



