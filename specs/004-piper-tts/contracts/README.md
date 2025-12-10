# Contracts: Piper TTS CLI

## CLI Interface (expected)
- Command: `python -m src.cli.piper_tts --text <text> --model <model_name> --cache-dir <path> [--output <file>] [--timeout-ms <ms>]`
- Input: UTF-8 text (<= text_limit), model name, cache dir for weights, optional output path, optional timeout.
- Output: audio file or stdout path; stdout logs include engine, model, duration, and errors.
- Errors:
  - Invalid config (missing model/engine) → non-zero exit, human-readable message.
  - Text too long → non-zero exit, clear message, no synthesis attempt.
  - Weights missing/bad checksum/download failure → non-zero exit, message with action to fix.
  - Timeout/unavailable engine → non-zero exit, message logged; no auto-fallback.

## Integration Expectations
- Bot path uses the same engine/model config as CLI; synthesis factory selects Piper when `TTS_ENGINE=piper`.
- Logging must include engine, model, duration, and error context for each request.
- Cache verification (checksum/size) runs at startup; failure blocks start.

