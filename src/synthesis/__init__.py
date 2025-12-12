from typing import TYPE_CHECKING

from src.synthesis.interface import SynthesisProvider, SynthesisResult
from src.synthesis.types import TTSEngine

if TYPE_CHECKING:
    from src.utils.config import Config


def create_synth(config: "Config", provider: str | None = None) -> SynthesisProvider:
    engine = provider or config.tts.engine.value
    if engine == TTSEngine.SILERO.value:
        from src.synthesis.silero import SileroSynthesis

        return SileroSynthesis(config.silero)
    if engine == TTSEngine.PIPER.value:
        from src.synthesis.piper import PiperSynthesis

        return PiperSynthesis(config.piper, config.tts)
    if engine == TTSEngine.VOSK.value:
        from src.synthesis.vosk import VoskSynthesis

        return VoskSynthesis(config.vosk, config.tts)
    if engine == TTSEngine.STUB.value:
        from src.synthesis.stub import StubSynthesis

        return StubSynthesis(config.audio_stub_path)
    raise ValueError(f"Unknown synthesis provider: {engine}")


__all__ = ["SynthesisProvider", "SynthesisResult", "create_synth", "TTSEngine"]



