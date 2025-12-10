# Quickstart (MeloTTS support)

## Prereqs
- Python 3.11 with `uv` available.
- Telegram bot token and whitelist env vars as in existing setup.
- MeloTTS assets/endpoint available; Silero assets already configured.

## Configure
Set environment variables (examples):
- `TTS_ENGINE=melotts` (or `silero`)
- `TTS_MODEL=<melo_model_id>`
- `TTS_TEXT_LIMIT=1000` (shared limit for all models)
- Existing bot env: `TELEGRAM_TOKEN`, `ALLOWED_USERS`, logging vars, etc.

## Run bot
```bash
uv run python -m src.bot.worker
```

## Verify
1) Отправьте текстовое сообщение боту.
2) Получите аудио; убедитесь, что голос от выбранного движка/модели.
3) Попробуйте текст длиннее лимита — бот должен вернуть понятное сообщение без синтеза.
4) Отключите выбранный движок (симулировать недоступность) — бот должен вернуть сообщение об ошибке и залогировать проблему без падения.

## Switch engine/model
1) Измените `TTS_ENGINE` / `TTS_MODEL` / `TTS_TEXT_LIMIT` в окружении.
2) Перезапустите процесс, чтобы конфиг применился.
3) Повторите шаги проверки.
