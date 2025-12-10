# Contracts

This feature does not add HTTP/GraphQL APIs. Interaction is via Telegram bot and internal TTS interface.

## Telegram Flow (informal contract)
- Input: text message from whitelisted user.
- Output: audio message synthesized by selected engine/model, or friendly error if engine unavailable or text exceeds limit.

## TTS Interface Expectations
- Input: text (<= configured limit), engine name, model name.
- Output: audio bytes and metadata (duration, engine, model) or structured error.
- Errors must be logged; no auto-fallback to other engines.
