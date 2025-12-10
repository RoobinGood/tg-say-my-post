import os
from dataclasses import dataclass
from pathlib import Path
from typing import Set

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    bot_token: str
    whitelist: Set[int]
    debug: bool
    audio_stub_path: Path
    log_level: str


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


def load_config() -> Config:
    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(project_root / ".env")
    default_audio = project_root / "src" / "audio" / "example.mp3"
    bot_token = os.getenv("BOT_TOKEN", "")
    whitelist = _parse_whitelist(os.getenv("WHITELIST"))
    debug = _parse_bool(os.getenv("DEBUG"), False)
    audio_stub_path = Path(os.getenv("AUDIO_STUB_PATH", str(default_audio))).resolve()
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    return Config(
        bot_token=bot_token,
        whitelist=whitelist,
        debug=debug,
        audio_stub_path=audio_stub_path,
        log_level=log_level,
    )



