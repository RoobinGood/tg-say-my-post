import argparse
import sys
from dataclasses import replace
from pathlib import Path

from src.synthesis.piper import PiperSynthesis
from src.utils.config import Config, load_config
from src.utils.logging import format_metrics, get_logger, setup_logging


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Piper TTS CLI")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="Text to voice (<=text limit)")
    group.add_argument("--text-file", help="Path to file with text")
    parser.add_argument("--out", required=True, help="Output audio path")
    parser.add_argument("--model", help="Override model id (e.g., ru_RU-natasha-medium)")
    parser.add_argument("--speaker-id", type=int, help="Override speaker id for multi-speaker models")
    parser.add_argument("--length-scale", type=float, help="Length scale override")
    parser.add_argument("--noise-scale", type=float, help="Noise scale override")
    parser.add_argument("--noise-w-scale", type=float, help="Noise w scale override")
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
    base = load_config(Path(args.config)) if args.config else load_config()
    piper_cfg = base.piper
    tts_cfg = base.tts
    if args.model:
        piper_cfg = replace(piper_cfg, model=args.model)
        tts_cfg = replace(tts_cfg, model=args.model)
    if args.speaker_id is not None:
        piper_cfg = replace(piper_cfg, speaker_id=args.speaker_id)
        tts_cfg = replace(tts_cfg, speaker_id=args.speaker_id)
    if args.length_scale is not None:
        piper_cfg = replace(piper_cfg, length_scale=args.length_scale)
        tts_cfg = replace(tts_cfg, length_scale=args.length_scale)
    if args.noise_scale is not None:
        piper_cfg = replace(piper_cfg, noise_scale=args.noise_scale)
        tts_cfg = replace(tts_cfg, noise_scale=args.noise_scale)
    if args.noise_w_scale is not None:
        piper_cfg = replace(piper_cfg, noise_w_scale=args.noise_w_scale)
        tts_cfg = replace(tts_cfg, noise_w_scale=args.noise_w_scale)
    if args.format:
        piper_cfg = replace(piper_cfg, audio_format=args.format)
        tts_cfg = replace(tts_cfg, audio_format=args.format)
    return replace(base, piper=piper_cfg, tts=tts_cfg)


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

        synth = PiperSynthesis(config.piper, config.tts)
        result = synth.synth(text, args.prefix, out_path)
        metrics_line = format_metrics(
            "piper_tts",
            load_ms=result.model_load_ms,
            synth_ms=result.synth_ms,
            duration_seconds=result.duration_seconds,
        )
        log.info("piper synth ok path=%s %s", result.path, metrics_line)
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


