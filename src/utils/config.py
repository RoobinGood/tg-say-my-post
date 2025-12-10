import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Set

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    bot_token: str
    whitelist: Set[int]
    debug: bool
    audio_stub_path: Path
    log_level: str
    silero: "SileroConfig"


@dataclass(frozen=True)
class SileroConfig:
    model_id: str
    speaker: str
    language: str
    sample_rate: int
    audio_format: str
    output_dir: Path
    device: str
    model_path: Optional[Path]
    cache_dir: Optional[Path]
    max_length: int
    metrics_path: Optional[Path]


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_whitelist(value: str | None) -> Set[int]:
    if not value:
        return set()
    ids: Set[int] = set()
    for raw in value.split(","):
        raw = raw.strip()
        if not raw:
            continue
        try:
            ids.add(int(raw))
        except ValueError:
            continue
    return ids


def _parse_int(value: str | None, default: int, *, minimum: int | None = None) -> int:
    if value is None or value.strip() == "":
        result = default
    else:
        try:
            result = int(value)
        except ValueError:
            result = default
    if minimum is not None and result < minimum:
        result = default
    return result


def _validate_silero_config(cfg: SileroConfig) -> SileroConfig:
    allowed_formats = {"wav", "mp3"}
    if cfg.audio_format not in allowed_formats:
        raise ValueError(f"Unsupported format: {cfg.audio_format}")
    if cfg.device not in {"cpu", "cuda"}:
        raise ValueError(f"Unsupported device: {cfg.device}")
    output_dir = cfg.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    if cfg.model_path and not cfg.model_path.exists():
        raise FileNotFoundError(f"Silero model path not found: {cfg.model_path}")
    if cfg.cache_dir:
        cfg.cache_dir.mkdir(parents=True, exist_ok=True)
    if cfg.metrics_path:
        cfg.metrics_path.parent.mkdir(parents=True, exist_ok=True)
    return cfg


def _load_env(config_path: Path | None, project_root: Path) -> None:
    if config_path:
        load_dotenv(config_path, override=True)
    else:
        load_dotenv(project_root / ".env", override=True)


def load_config(config_path: Path | None = None) -> Config:
    project_root = Path(__file__).resolve().parents[2]
    _load_env(config_path, project_root)
    default_audio = project_root / "src" / "audio" / "example.mp3"
    bot_token = os.getenv("BOT_TOKEN", "")
    whitelist = _parse_whitelist(os.getenv("WHITELIST"))
    debug = _parse_bool(os.getenv("DEBUG"), False)
    audio_stub_path = Path(os.getenv("AUDIO_STUB_PATH", str(default_audio))).resolve()
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    silero_model_id = os.getenv("SILERO_MODEL_ID", "v5_ru")
    silero_speaker = os.getenv("SILERO_SPEAKER", "aidar")
    silero_language = os.getenv("SILERO_LANGUAGE", "ru")
    silero_sample_rate = _parse_int(os.getenv("SILERO_SAMPLE_RATE"), 48000, minimum=8000)
    silero_format = os.getenv("SILERO_FORMAT", "wav").lower()
    silero_output_dir = Path(os.getenv("SILERO_OUTPUT_DIR", str(project_root / "out"))).resolve()
    silero_device = os.getenv("SILERO_DEVICE", "cpu").lower()
    silero_model_path_raw = os.getenv("SILERO_MODEL_PATH")
    silero_model_path = Path(silero_model_path_raw).resolve() if silero_model_path_raw else None
    silero_cache_dir_raw = os.getenv("SILERO_CACHE_DIR")
    silero_cache_dir = Path(silero_cache_dir_raw).resolve() if silero_cache_dir_raw else None
    silero_max_length = _parse_int(os.getenv("SILERO_MAX_LENGTH"), 1000, minimum=1)
    silero_metrics_raw = os.getenv("SILERO_METRICS_FILE")
    silero_metrics_path = Path(silero_metrics_raw).resolve() if silero_metrics_raw else None

    silero_cfg = _validate_silero_config(
        SileroConfig(
            model_id=silero_model_id,
            speaker=silero_speaker,
            language=silero_language,
            sample_rate=silero_sample_rate,
            audio_format=silero_format,
            output_dir=silero_output_dir,
            device=silero_device,
            model_path=silero_model_path,
            cache_dir=silero_cache_dir,
            max_length=silero_max_length,
            metrics_path=silero_metrics_path,
        )
    )

    return Config(
        bot_token=bot_token,
        whitelist=whitelist,
        debug=debug,
        audio_stub_path=audio_stub_path,
        log_level=log_level,
        silero=silero_cfg,
    )



