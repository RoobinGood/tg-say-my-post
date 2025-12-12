import argparse
import sys
from dataclasses import replace
from pathlib import Path

from src.synthesis.vosk import VoskSynthesis
from src.utils.config import Config, load_config
from src.utils.logging import format_metrics, get_logger, setup_logging


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Vosk TTS CLI")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Text to voice (<=max length)")
    group.add_argument("--text-file", help="Path to file with text")
    parser.add_argument("--out", required=True, help="Output audio path")
    parser.add_argument("--model", help="Override model name (e.g., vosk-model-tts-ru-0.9-multi)")
    parser.add_argument("--speaker-id", type=int, help="Override speaker_id (0-4)")
    parser.add_argument("--format", choices=["wav", "mp3"], help="Override audio format")
    parser.add_argument("--config", help="Optional path to .env-style config file")
    parser.add_argument("--prefix", help="Optional spoken prefix")
    return parser.parse_args(argv)


def _read_text(args: argparse.Namespace) -> str:
    if args.text:
        return args.text
    if args.text_file:
        path = Path(args.text_file)
        return path.read_text(encoding="utf-8")
    raise ValueError("text is required")


def _build_config(args: argparse.Namespace) -> Config:
    if args.config:
        cfg_path = Path(args.config)
        if not cfg_path.exists():
            raise FileNotFoundError(f"config file not found: {cfg_path}")
        base = load_config(cfg_path)
    else:
        base = load_config()
    vosk_cfg = base.vosk
    if args.model:
        vosk_cfg = replace(vosk_cfg, model_name=args.model)
    if args.speaker_id is not None:
        vosk_cfg = replace(vosk_cfg, speaker_id=args.speaker_id)
    if args.format:
        vosk_cfg = replace(vosk_cfg, audio_format=args.format)
    return replace(base, vosk=vosk_cfg)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        config = _build_config(args)
        setup_logging(config.log_level)
        log = get_logger(__name__)

        out_path = Path(args.out)
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as exc:  # noqa: BLE001
            raise OSError(f"cannot prepare output dir {out_path.parent}: {exc}") from exc

        text = _read_text(args).strip()
        if not text:
            raise ValueError("empty text")
        if len(text) > config.tts.text_limit:
            raise ValueError("text too long")

        synth = VoskSynthesis(config.vosk, config.tts)
        result = synth.synth(text, args.prefix, out_path)
        metrics_line = format_metrics(
            "vosk_tts",
            load_ms=result.model_load_ms,
            synth_ms=result.synth_ms,
            duration_seconds=result.duration_seconds,
        )
        log.info("vosk synth ok path=%s %s", result.path, metrics_line)
        return 0
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 3
    except OSError as exc:
        print(exc, file=sys.stderr)
        return 4


if __name__ == "__main__":
    sys.exit(main())



