import argparse
import sys
from pathlib import Path

from src.synthesis.stub import StubSynthesis
from src.utils.config import load_config
from src.utils.logging import setup_logging


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synthesis stub CLI")
    parser.add_argument("--text", required=True, help="Text to voice (<=2000 chars)")
    parser.add_argument("--out", required=True, help="Output mp3 path")
    parser.add_argument("--prefix", required=False, help="Optional spoken prefix")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    config = load_config()
    setup_logging(config.log_level)

    synth = StubSynthesis(config.audio_stub_path)
    try:
        synth.synth(args.text, args.prefix, Path(args.out))
    except ValueError:
        return 2
    except FileNotFoundError:
        return 3
    except OSError:
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())


