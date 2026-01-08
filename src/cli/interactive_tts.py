import argparse
import asyncio
import os
import subprocess
import sys
import tempfile
import termios
import tty
from pathlib import Path

from src.preprocessing import preprocess_text
from src.synthesis import create_synth
from src.utils.config import Config, load_config
from src.utils.logging import format_metrics, get_logger, setup_logging



def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interactive TTS CLI")
    parser.add_argument(
        "--mode",
        choices=["file", "virtual_mic"],
        required=True,
        help="Operation mode: file (save to file) or virtual_mic (play to PulseAudio sink)",
    )
    parser.add_argument(
        "--output-path",
        help="Output file path (required for file mode)",
    )
    parser.add_argument(
        "--sink-name",
        help="PulseAudio sink name (required for virtual_mic mode)",
    )
    parser.add_argument(
        "--config",
        help="Optional path to .env-style config file",
    )
    return parser.parse_args(argv)


def _validate_args(args: argparse.Namespace) -> None:
    if args.mode == "file" and not args.output_path:
        raise ValueError("--output-path is required for file mode")
    if args.mode == "virtual_mic" and not args.sink_name:
        raise ValueError("--sink-name is required for virtual_mic mode")


def _load_config(config_path: str | None) -> Config:
    if config_path:
        return load_config(Path(config_path))
    return load_config()


def _init_synth(config: Config) -> tuple:
    provider = os.getenv("SYNTH_PROVIDER") or os.getenv("TTS_ENGINE")
    synth = create_synth(config, provider=provider)
    active_engine = provider or config.tts.engine.value
    return synth, active_engine


def _warmup_synth(synth, log) -> None:
    log.info("warming up synthesis engine...")
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            warmup_path = Path(tmp.name)
        try:
            result = synth.synth("тест", None, warmup_path)
            log.info(
                "warmup completed load_ms=%.1f synth_ms=%.1f duration=%.2fs",
                result.model_load_ms or 0.0,
                result.synth_ms,
                result.duration_seconds,
            )
        finally:
            warmup_path.unlink(missing_ok=True)
    except Exception as exc:
        log.warning("warmup failed: %s (will continue)", exc)


def _get_key() -> str:
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        key = sys.stdin.read(1)
        if ord(key) == 13:
            return "enter"
        if ord(key) == 27:
            return "esc"
        if ord(key) == 3:
            raise KeyboardInterrupt()
        return key
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def _check_sink_exists(sink_name: str) -> bool:
    try:
        result = subprocess.run(
            ["pactl", "list", "sinks", "short"],
            capture_output=True,
            text=True,
            check=True,
        )
        return sink_name in result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _preprocess_text(text: str, llm_config) -> str:
    if not text or not text.strip():
        return text
    return asyncio.run(preprocess_text(text.strip(), llm_config))


def _play_to_sink(audio_path: Path, sink_name: str) -> subprocess.Popen:
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    cmd = ["paplay", f"--device={sink_name}", str(audio_path)]
    return subprocess.Popen(cmd)


def _mode_file(synth, output_path: Path, config: Config, log) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    while True:
        try:
            text = input("> ").strip()
            if not text:
                continue
            text = _preprocess_text(text, config.llm)
            if not text.strip():
                log.warning("preprocessing resulted in empty text")
                continue
            if len(text) > config.tts.text_limit:
                log.warning("text too long, max=%d", config.tts.text_limit)
                continue
            result = synth.synth(text, None, output_path)
            metrics_line = format_metrics(
                "interactive_tts",
                load_ms=result.model_load_ms,
                synth_ms=result.synth_ms,
                duration_seconds=result.duration_seconds,
            )
            log.info("synth ok path=%s %s", result.path, metrics_line)
        except KeyboardInterrupt:
            log.info("interrupted by user")
            break
        except Exception as exc:
            log.error("synthesis failed: %s", exc, exc_info=True)


def _mode_virtual_mic(synth, sink_name: str, config: Config, log) -> None:
    if not _check_sink_exists(sink_name):
        raise ValueError(
            f"Sink '{sink_name}' not found. Create it with: pactl load-module module-null-sink sink_name={sink_name}"
        )
    while True:
        try:
            text = input("> ").strip()
            if not text:
                continue
            text = _preprocess_text(text, config.llm)
            if not text.strip():
                log.warning("preprocessing resulted in empty text")
                continue
            if len(text) > config.tts.text_limit:
                log.warning("text too long, max=%d", config.tts.text_limit)
                continue
            with tempfile.NamedTemporaryFile(
                suffix=f".{config.tts.audio_format}", delete=False
            ) as tmp:
                temp_path = Path(tmp.name)
            try:
                result = synth.synth(text, None, temp_path)
                metrics_line = format_metrics(
                    "interactive_tts",
                    load_ms=result.model_load_ms,
                    synth_ms=result.synth_ms,
                    duration_seconds=result.duration_seconds,
                )
                log.info("synth ok %s", metrics_line)
                while True:
                    print("Press Enter to play or Esc to discard...", flush=True)
                    try:
                        key = _get_key()
                        print()
                        if key == "enter":
                            process = _play_to_sink(result.path, sink_name)
                            process.wait()
                            log.info("played to sink=%s", sink_name)
                            break
                        elif key == "esc":
                            log.info("discarded audio")
                            break
                    except KeyboardInterrupt:
                        print()
                        raise
            finally:
                temp_path.unlink(missing_ok=True)
        except KeyboardInterrupt:
            log.info("interrupted by user")
            break
        except Exception as exc:
            log.error("synthesis failed: %s", exc, exc_info=True)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        _validate_args(args)
        config = _load_config(args.config)
        setup_logging(config.log_level)
        log = get_logger(__name__)
        synth, active_engine = _init_synth(config)
        log.info("synthesis engine=%s model=%s", active_engine, config.tts.model)
        _warmup_synth(synth, log)
        if args.mode == "file":
            output_path = Path(args.output_path)
            _mode_file(synth, output_path, config, log)
        else:
            _mode_virtual_mic(synth, args.sink_name, config, log)
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
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())


