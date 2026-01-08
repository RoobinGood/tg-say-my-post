#!/usr/bin/env python3
import argparse
import asyncio
import sys
from pathlib import Path

from src.preprocessing import preprocess_text, preprocess_text_with_result
from src.utils.config import load_config


def main() -> int:
    parser = argparse.ArgumentParser(description="Test text preprocessing")
    parser.add_argument("text", nargs="?", help="Text to preprocess (or read from stdin)")
    parser.add_argument("--with-result", action="store_true", help="Show detailed result")
    parser.add_argument("--config", type=Path, help="Path to config file")
    
    args = parser.parse_args()
    
    if args.text:
        text = args.text
    else:
        text = sys.stdin.read()
    
    if not text.strip():
        print("Empty text", file=sys.stderr)
        return 1
    
    try:
        config = load_config(args.config) if args.config else None
        llm_config = getattr(config, "llm", None) if config else None
        
        if args.with_result:
            result = asyncio.run(preprocess_text_with_result(text, llm_config))
            print(f"Text: {result.text}")
            print(f"LLM used: {result.llm_used}")
            print(f"Chunks processed: {result.chunks_processed}")
            print(f"LLM calls: {result.llm_calls}")
            print(f"Fallback used: {result.fallback_used}")
            if result.errors:
                print(f"Errors: {result.errors}")
        else:
            result_text = asyncio.run(preprocess_text(text, llm_config))
            print(result_text)
        
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

