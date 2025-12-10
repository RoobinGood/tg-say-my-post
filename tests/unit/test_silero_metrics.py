import logging
from dataclasses import replace
from io import StringIO

import pytest

import src.synthesis.silero as silero
from src.synthesis.silero import SileroSynthesis
from src.utils.config import load_config
from src.utils.logging import format_metrics, log_metrics


def _fake_measure_ms_factory(values: list[float]):
    iterator = iter(values)

    def _next() -> float:
        return next(iterator)

    return _next


def test_log_metrics_formats_and_file_sink(tmp_path):
    stream = StringIO()
    logger = logging.getLogger("metrics-test")
    logger.handlers.clear()
    handler = logging.StreamHandler(stream)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    metrics_file = tmp_path / "metrics.log"
    message = log_metrics(
        logger,
        "silero_tts",
        load_ms=123.4,
        synth_ms=56.7,
        duration_seconds=1.234,
        metrics_file=metrics_file,
    )
    assert message == "metrics silero_tts load=123.4ms synth=56.7ms duration=1.234s"
    assert "metrics silero_tts load=123.4ms" in stream.getvalue()
    assert metrics_file.read_text(encoding="utf-8").strip() == message
    logger.removeHandler(handler)


def test_silero_synth_records_metrics(monkeypatch, tmp_path):
    metrics_file = tmp_path / "metrics" / "silero.log"
    fake_measure = _fake_measure_ms_factory([10, 30, 50, 90, 110, 150])
    monkeypatch.setattr(silero, "measure_ms", fake_measure)
    monkeypatch.setenv("TTS_MODEL", "v5_ru")
    monkeypatch.setenv("TTS_AUDIO_FORMAT", "wav")

    class DummyModel:
        def to(self, device):
            return self

        def apply_tts(self, text: str, speaker: str, sample_rate: int):
            return [0.0] * sample_rate

    def fake_ensure(self: SileroSynthesis):
        if self._model is not None:
            return
        start = silero.measure_ms()
        self._model = DummyModel()
        self._model_load_ms = silero.measure_ms() - start

    monkeypatch.setattr(SileroSynthesis, "_ensure_model", fake_ensure)

    base_cfg = load_config()
    silero_cfg = replace(
        base_cfg.silero,
        output_dir=tmp_path,
        metrics_path=metrics_file,
        audio_format="wav",
        sample_rate=48000,
    )
    synth = SileroSynthesis(silero_cfg)
    out = tmp_path / "audio"
    result_first = synth.synth("hello", None, out)
    result_second = synth.synth("world", None, out)

    assert result_first.model_load_ms == 20
    assert result_first.synth_ms == 40
    assert result_second.model_load_ms == 20
    assert result_second.synth_ms == 40
    assert result_first.duration_seconds > 0
    assert metrics_file.exists()
    lines = metrics_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert "load=20.0ms" in lines[0]
    assert "duration=" in lines[0]
    assert format_metrics(
        "silero_tts",
        load_ms=result_first.model_load_ms,
        synth_ms=result_first.synth_ms,
        duration_seconds=result_first.duration_seconds,
    ) in lines[0]


