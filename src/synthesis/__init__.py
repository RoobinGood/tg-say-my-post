from src.synthesis.interface import SynthesisProvider, SynthesisResult
from src.synthesis.silero import SileroSynthesis
from src.synthesis.stub import StubSynthesis
from src.utils.config import Config


def create_synth(config: Config, provider: str = "silero") -> SynthesisProvider:
    if provider == "silero":
        return SileroSynthesis(config.silero)
    if provider == "stub":
        return StubSynthesis(config.audio_stub_path)
    raise ValueError(f"Unknown synthesis provider: {provider}")


__all__ = ["SynthesisProvider", "SynthesisResult", "SileroSynthesis", "StubSynthesis", "create_synth"]


