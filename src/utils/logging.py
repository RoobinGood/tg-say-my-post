import logging
import time
from pathlib import Path
from typing import Any


def setup_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers[:]:
            root.removeHandler(handler)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(level.upper())
    # Silence noisy HTTP polling unless debug explicitly requested
    httpx_logger = logging.getLogger("httpx")
    if level.upper() != "DEBUG":
        httpx_logger.setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def measure_ms() -> float:
    return time.perf_counter() * 1000


def format_metrics(label: str, *, load_ms: float | None, synth_ms: float, duration_seconds: float) -> str:
    load_part = f"{load_ms:.1f}ms" if load_ms is not None else "n/a"
    return f"metrics {label} load={load_part} synth={synth_ms:.1f}ms duration={duration_seconds:.3f}s"


def log_metrics(
    logger: logging.Logger,
    label: str,
    *,
    load_ms: float | None,
    synth_ms: float,
    duration_seconds: float,
    metrics_file: Path | None = None,
) -> str:
    message = format_metrics(label, load_ms=load_ms, synth_ms=synth_ms, duration_seconds=duration_seconds)
    logger.info(message)
    if metrics_file is not None:
        metrics_file.parent.mkdir(parents=True, exist_ok=True)
        with metrics_file.open("a", encoding="utf-8") as handle:
            handle.write(message + "\n")
    return message



