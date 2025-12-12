from enum import Enum


class TTSEngine(str, Enum):
    SILERO = "silero"
    PIPER = "piper"
    VOSK = "vosk"
    STUB = "stub"


__all__ = ["TTSEngine"]

