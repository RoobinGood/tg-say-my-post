# Contract: Synthesis CLI (Stub)

## Command
```bash
uv run python -m src.cli.synth_stub --text "<text>" --out <path/to/output.mp3> [--prefix "<optional prefix>"]
```

## Arguments
- `--text` (required): текст ≤2000 символов.
- `--out` (required): путь для сохранения mp3.
- `--prefix` (optional): строка, которая должна быть озвучена перед текстом (например, «сообщение от пользователя <имя>»).

## Behavior
- Читает `AUDIO_STUB_PATH`; копирует/дублирует в `--out`.
- Если задан `--prefix`, может добавлять тишину/метаданные (заглушка: достаточно логировать использованный префикс).
- Возвращает код 0 при успехе; при ошибке — ненулевой код и лог в stderr.

## Errors
- Пустой `--text` или длина >2000 → exit 2.
- Невозможно прочитать `AUDIO_STUB_PATH` → exit 3.
- Невозможно записать `--out` → exit 4.


