# Quickstart: Silero TTS module

## Prereqs
- Python 3.11, `uv` installed.
- Доступ к весам Silero (torch hub cache или локальный путь).

## Env Vars (основные)
- `SILERO_MODEL_ID` — модель (например, v5_ru).
- `SILERO_SPEAKER` — спикер внутри модели (например, aidar, eugene, kseniya, baya, xenia).
- `SILERO_LANGUAGE` — язык для синтеза (например, ru/en).
- `SILERO_FORMAT` — `wav` (default) или `mp3`.
- `SILERO_SAMPLE_RATE` — частота (рекомендуется 48000 для v5_ru).
- `SILERO_OUTPUT_DIR` — директория для сохранения аудио (существует/создаётся).
- `SILERO_DEVICE` — `cpu` или `cuda`.
- `SILERO_MODEL_PATH` — необязательно, путь к локальным весам (иначе hub cache).
- `SILERO_METRICS_FILE` — опционально, путь для записи метрик (append).
- `SYNTH_PROVIDER` — `silero` (default) или `stub` для запуска бота без Silero.
- `LOG_LEVEL` — `INFO` (default) или `DEBUG`.
- Для бота также: `BOT_TOKEN`, `WHITELIST` (список user_id), `DEBUG` (true/false).

## Install
```bash
uv sync
```

## Run Silero CLI
```bash
uv run python -m src.cli.silero_tts --text "Привет" --out /tmp/out.wav
```
- Проверить, что файл создан и в stdout есть метрики (load_ms, synth_ms, duration_s). При отсутствующем конфиге/каталоге выводится ошибка и код != 0.

## Run bot with Silero synthesizer
```bash
uv run python -m src.cli.run_bot
```
- Бот использует модуль синтеза из конфига (SILERO_*). Отправьте текст → получите голосовое сообщение; при недоступности Silero бот отвечает текстом.

## Tests
```bash
uv run pytest
```

## Validation steps
- Убедиться, что `SILERO_VOICE`/`SILERO_LANGUAGE` заданы и поддерживаются моделью.
- Запустить CLI с коротким текстом и проверить аудио и метрики.
- Запустить бота и отправить сообщение whitelisted пользователем → получить голосовой ответ.
- Отключить доступность модели (например, неверный путь) → бот/CLI выдают текстовую ошибку и ненулевой код выхода.

