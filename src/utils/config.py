import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Set

from src.synthesis.types import TTSEngine

from dotenv import load_dotenv


@dataclass(frozen=True)
class TTSConfig:
    engine: TTSEngine
    model: str
    text_limit: int
    cache_dir: Path
    model_url: Optional[str]
    model_config_url: Optional[str]
    model_checksum: Optional[str]
    model_size: Optional[int]
    speaker_id: Optional[int]
    length_scale: Optional[float]
    noise_scale: Optional[float]
    noise_w_scale: Optional[float]
    audio_format: str
    metrics_path: Optional[Path]


@dataclass(frozen=True)
class PiperConfig:
    model: str
    cache_dir: Path
    model_url: Optional[str]
    model_config_url: Optional[str]
    model_checksum: Optional[str]
    model_size: Optional[int]
    speaker_id: Optional[int]
    length_scale: Optional[float]
    noise_scale: Optional[float]
    noise_w_scale: Optional[float]
    audio_format: str
    metrics_path: Optional[Path]
    use_cuda: bool = False


@dataclass(frozen=True)
class VoskConfig:
    model_name: str
    speaker_id: int
    audio_format: str
    cache_dir: Path
    metrics_path: Optional[Path]


@dataclass(frozen=True)
class Config:
    bot_token: str
    whitelist: Set[int]
    debug: bool
    audio_stub_path: Path
    log_level: str
    tts: TTSConfig
    silero: "SileroConfig"
    piper: PiperConfig
    vosk: VoskConfig


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


def _parse_int(value: str | None, default: int | None, *, minimum: int | None = None) -> int | None:
    if value is None or value.strip() == "":
        result = default
    else:
        try:
            result = int(value)
        except ValueError:
            result = default
    if result is not None and minimum is not None and result < minimum:
        result = default
    return result


def _parse_float(value: str | None) -> Optional[float]:
    if value is None or value.strip() == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


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


def _validate_piper_config(cfg: PiperConfig) -> PiperConfig:
    allowed_formats = {"wav", "mp3"}
    if cfg.audio_format not in allowed_formats:
        raise ValueError(f"Unsupported format: {cfg.audio_format}")
    if cfg.cache_dir:
        cfg.cache_dir.mkdir(parents=True, exist_ok=True)
    if cfg.metrics_path:
        cfg.metrics_path.parent.mkdir(parents=True, exist_ok=True)
    return cfg


def _validate_vosk_config(cfg: VoskConfig) -> VoskConfig:
    allowed_formats = {"wav", "mp3"}
    if cfg.audio_format not in allowed_formats:
        raise ValueError(f"Unsupported format: {cfg.audio_format}")
    if not cfg.model_name:
        raise ValueError("Vosk model_name cannot be empty")
    if cfg.speaker_id < 0 or cfg.speaker_id > 4:
        raise ValueError(f"speaker_id must be in range 0-4, got {cfg.speaker_id}")
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

    # Common TTS settings
    tts_engine_raw = os.getenv("TTS_ENGINE", "silero").lower()
    try:
        tts_engine = TTSEngine(tts_engine_raw)
    except ValueError:
        raise ValueError(f"Unsupported TTS engine: {tts_engine_raw}")

    silero_max_env = _parse_int(os.getenv("SILERO_MAX_LENGTH"), None, minimum=1)

    tts_model = os.getenv("TTS_MODEL", "").strip() or os.getenv("SILERO_MODEL_ID", "").strip()
    if not tts_model:
        raise ValueError("TTS_MODEL is required")

    tts_text_limit = _parse_int(os.getenv("TTS_TEXT_LIMIT"), silero_max_env or 1000, minimum=1) or 1000
    tts_cache_dir = Path(os.getenv("TTS_CACHE_DIR") or os.getenv("SILERO_CACHE_DIR") or str(project_root / "out" / "tts_cache")).resolve()
    tts_model_url = os.getenv("TTS_MODEL_URL")
    tts_model_config_url = os.getenv("TTS_MODEL_CONFIG_URL")
    tts_checksum = os.getenv("TTS_MODEL_CHECKSUM")
    tts_size = _parse_int(os.getenv("TTS_MODEL_SIZE"), None, minimum=1)  # type: ignore[arg-type]
    tts_speaker_id = _parse_int(os.getenv("TTS_SPEAKER_ID") or os.getenv("SILERO_SPEAKER_ID"), None, minimum=0)  # type: ignore[arg-type]
    tts_length_scale = _parse_float(os.getenv("TTS_LENGTH_SCALE"))
    tts_noise_scale = _parse_float(os.getenv("TTS_NOISE_SCALE"))
    tts_noise_w_scale = _parse_float(os.getenv("TTS_NOISE_W_SCALE"))
    tts_format = (os.getenv("TTS_AUDIO_FORMAT") or os.getenv("SILERO_FORMAT") or "wav").lower()
    tts_sample_rate = _parse_int(os.getenv("TTS_SAMPLE_RATE") or os.getenv("SILERO_SAMPLE_RATE"), 48000, minimum=8000) or 48000
    tts_speaker = os.getenv("TTS_SPEAKER") or os.getenv("SILERO_SPEAKER") or "aidar"
    tts_language = os.getenv("TTS_LANGUAGE") or os.getenv("SILERO_LANGUAGE") or "ru"
    tts_device = (os.getenv("TTS_DEVICE") or os.getenv("SILERO_DEVICE") or "cpu").lower()
    tts_model_path_raw = os.getenv("TTS_MODEL_PATH") or os.getenv("SILERO_MODEL_PATH")
    tts_model_path = Path(tts_model_path_raw).resolve() if tts_model_path_raw else None
    tts_output_dir = Path(os.getenv("TTS_OUTPUT_DIR") or os.getenv("SILERO_OUTPUT_DIR") or str(project_root / "out")).resolve()
    tts_metrics_raw = os.getenv("TTS_METRICS_FILE") or os.getenv("SILERO_METRICS_FILE")
    tts_metrics_path = Path(tts_metrics_raw).resolve() if tts_metrics_raw else None

    tts_cfg = TTSConfig(
        engine=tts_engine,
        model=tts_model,
        text_limit=tts_text_limit,
        cache_dir=tts_cache_dir,
        model_url=tts_model_url,
        model_config_url=tts_model_config_url,
        model_checksum=tts_checksum,
        model_size=tts_size,
        speaker_id=tts_speaker_id,
        length_scale=tts_length_scale,
        noise_scale=tts_noise_scale,
        noise_w_scale=tts_noise_w_scale,
        audio_format=tts_format,
        metrics_path=tts_metrics_path,
    )

    silero_model_id = tts_model or "v5_ru"
    silero_speaker = tts_speaker
    silero_language = tts_language
    silero_sample_rate = tts_sample_rate
    silero_format = tts_format
    silero_output_dir = tts_output_dir
    silero_device = tts_device
    silero_model_path = tts_model_path
    silero_cache_dir = tts_cache_dir
    silero_max_length = tts_text_limit or 1000
    silero_metrics_path = tts_metrics_path

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

    piper_cfg = _validate_piper_config(
        PiperConfig(
            model=tts_model,
            cache_dir=tts_cache_dir,
            model_url=tts_model_url,
            model_config_url=tts_model_config_url,
            model_checksum=tts_checksum,
            model_size=tts_size,
            speaker_id=tts_speaker_id,
            length_scale=tts_length_scale,
            noise_scale=tts_noise_scale,
            noise_w_scale=tts_noise_w_scale,
            audio_format=tts_format,
            metrics_path=tts_metrics_path,
            use_cuda=os.getenv("TTS_USE_CUDA", "0").lower() in {"1", "true", "yes", "on"},
        )
    )

    vosk_model_name = tts_model or "vosk-model-tts-ru-0.9-multi"
    vosk_speaker_id = tts_speaker_id if tts_speaker_id is not None else 0
    vosk_format = tts_format
    vosk_cache_dir = tts_cache_dir
    vosk_metrics_path = tts_metrics_path

    vosk_cfg = _validate_vosk_config(
        VoskConfig(
            model_name=vosk_model_name,
            speaker_id=vosk_speaker_id,
            audio_format=vosk_format,
            cache_dir=vosk_cache_dir,
            metrics_path=vosk_metrics_path,
        )
    )

    return Config(
        bot_token=bot_token,
        whitelist=whitelist,
        debug=debug,
        audio_stub_path=audio_stub_path,
        log_level=log_level,
        tts=tts_cfg,
        silero=silero_cfg,
        piper=piper_cfg,
        vosk=vosk_cfg,
    )



