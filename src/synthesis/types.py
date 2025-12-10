from enum import Enum


class TTSEngine(str, Enum):
    SILERO = "silero"
    PIPER = "piper"
    STUB = "stub"


__all__ = ["TTSEngine"]

