import time
from dataclasses import replace

import pytest

from src.synthesis.silero import SileroSynthesis
from src.utils.config import load_config


def test_silero_perf_smoke(monkeypatch, tmp_path):
    metrics_file = tmp_path / "metrics.log"

    class DummyModel:
        def to(self, device):
            return self

        def apply_tts(self, text: str, speaker: str, sample_rate: int):
            return [0.0] * sample_rate

    def fake_ensure(self: SileroSynthesis):
        if self._model is not None:
            return
        self._model = DummyModel()
        self._model_load_ms = 5.0

    monkeypatch.setattr(SileroSynthesis, "_ensure_model", fake_ensure)
    env_file = tmp_path / ".env"
    env_file.write_text("LLM_ENABLED=false\nTTS_MODEL=v5_ru\n", encoding="utf-8")

    cfg = load_config(env_file)
    silero_cfg = replace(
        cfg.silero,
        output_dir=tmp_path,
        metrics_path=metrics_file,
        audio_format="wav",
        sample_rate=48000,
    )
    synth = SileroSynthesis(silero_cfg)
    start = time.perf_counter()
    result = synth.synth("speed check", None, tmp_path / "perf")
    elapsed = time.perf_counter() - start

    assert elapsed < 8
    assert result.synth_ms < 8000
    assert result.duration_seconds <= 2
    assert result.path.exists()
    assert metrics_file.exists()


