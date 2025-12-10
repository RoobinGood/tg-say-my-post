# Data Model

## Entities

### TTSConfig
- engine: enum {silero, melotts} (required, from env).
- model: string (required per engine, from env).
- text_limit: int (required, shared for all models).
- log_level: string (reuse existing config, if present).

### TTSRequest
- text: string (<= text_limit, required).
- engine: enum {silero, melotts} (resolved from config).
- model: string (resolved from config).
- language: string (derived from model/engine defaults if needed).

### TTSResult
- audio_bytes: binary/bytes reference.
- duration_ms: int (measured duration of synthesis).
- engine: enum {silero, melotts}.
- model: string.
- error: optional string (set if synthesis failed or validation rejected).

## Relationships
- TTSConfig provides defaults for TTSRequest (engine, model, text_limit).
- TTSRequest produces TTSResult; errors logged when error is set.

## Validation Rules
- engine must be supported (silero|melotts); otherwise startup fails.
- model must be provided for the selected engine; otherwise startup fails.
- text length must not exceed text_limit; otherwise request is rejected before TTS call.
- On failure, error must be logged; user-facing message must remain friendly.
