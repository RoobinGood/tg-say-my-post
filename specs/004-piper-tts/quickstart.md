# Quickstart: Piper TTS support

## Prerequisites
- Python 3.11 with `uv` installed.
- Docker environment ready (if used).
- Network access to download Piper weights on first run.

## Steps
1) Install deps: `uv sync` (ensure Piper dependency added in project).
2) Configure env: set `TTS_ENGINE=piper`, `TTS_MODEL=<piper_model_name>`, `TTS_TEXT_LIMIT=<max_chars>`, `TTS_CACHE_DIR=<path>`, optionally checksum/size vars if required.
3) Prepare cache dir: ensure writable path in `TTS_CACHE_DIR` (created if missing).
4) Run Piper CLI smoke test: `python -m src.cli.piper_tts --text "Привет" --model $TTS_MODEL --cache-dir $TTS_CACHE_DIR` and verify audio output.
5) Start bot with Piper: run bot entrypoint; send тестовый пост в чат и убедиться, что ответ аудио пришёл от Piper.
6) Failure check: временно переименовать файл весов, перезапустить — убедиться, что старт блокируется с понятной ошибкой и логом.

## Notes
- Лимит текста проверяется до вызова Piper; запросы длиннее отклоняются дружелюбным сообщением.
- Авто-фолбэка нет: при недоступности Piper бот сообщает об ошибке и не падает.

