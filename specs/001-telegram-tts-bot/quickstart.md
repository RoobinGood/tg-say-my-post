# Quickstart: Telegram TTS Bot

## Prereqs
- Python 3.11, `uv` installed.
- Telegram bot token.

## Env Vars
- `BOT_TOKEN` — Telegram бот токен.
- `WHITELIST` — список user_id через запятую; пусто = запрещено всем.
- `DEBUG` — `true/false`; при true отправлять трассу ошибок пользователю.
- `AUDIO_STUB_PATH` — путь к test mp3 (по умолчанию `src/audio/example.mp3`).
- `LOG_LEVEL` — `INFO` (default) или `DEBUG`.

## Install
```bash
uv sync
```

## Run bot
```bash
uv run python -m src.cli.run_bot
```

## Run synth stub CLI (test)
```bash
uv run python -m src.cli.synth_stub --text "hello" --out /tmp/out.mp3
```

## Tests
```bash
uv run pytest
```

## Validation steps
- Проверить, что `BOT_TOKEN` и `WHITELIST` заданы.
- Запустить `uv run python -m src.cli.synth_stub --text "ping" --out /tmp/out.mp3`.
- Запустить бота: `uv run python -m src.cli.run_bot` и отправить текст ≤2000 → получить mp3.
- Переслать сообщение пользователя и пост канала → убедиться в голосовых префиксах.
- Отправить 5 сообщений подряд → убедиться, что аудио в исходном порядке.


