# Telegram TTS Bot

Stub implementation for Telegram text-to-speech bot with queueing and synthesis placeholder.


## bot

```sh
uv run python -m src.cli.run_bot
```

## text preprocessing

Text preprocessing includes:
- Basic cleanup: emoji removal, URL removal, capitalization, punctuation
- LLM transliteration: Latin → Cyrillic, numbers → words, stress marks (if LLM enabled)
- Programmatic fallback: num2words + dictionary-based transliteration (if LLM disabled)

### Configuration

Set `LLM_ENABLED=false` to use only programmatic transliteration.

See `.env.example` for all LLM configuration options.

### Testing preprocessing

```sh
# Basic usage
echo "API версии 2.5" | uv run python -m src.cli.preprocess

# With detailed metrics
echo "API версии 2.5" | uv run python -m src.cli.preprocess --with-result
```

## backlog

[ ] README
