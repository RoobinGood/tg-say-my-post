# Contract: Silero TTS CLI

## Command
`uv run python -m src.cli.silero_tts --text "..." --out /path/file.wav [options]`

## Inputs (args/flags)
- `--text` (required) — исходный текст для синтеза.
- `--text-file` (optional) — путь к файлу с текстом (эксклюзивно с `--text`).
- `--voice` (optional) — идентификатор голоса из конфига (override).
- `--lang` (optional) — язык, если поддерживается выбранным голосом.
- `--format` (optional) — wav|mp3, по умолчанию из конфига.
- `--out` (required) — путь для сохранения аудио.
- `--config` (optional) — явный путь к конфигу; по умолчанию дефолтный.

## Behavior
- Загружает Silero модель (кеш/локальный путь). Cold start логирует время загрузки.
- Выполняет синтез, сохраняет файл, печатает путь и метрики (load_ms, synth_ms, duration_s).
- При ошибке выводит сообщение в stderr и завершает с кодом != 0.

## Outputs
- Статус выхода 0 при успехе.
- STDOUT: путь к файлу + метрики в человекочитаемом виде.
- STDERR: ошибки валидации, ошибки модели, проблемы записи.

