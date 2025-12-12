# Implementation Plan: Vosk TTS Integration

**Branch**: `005-vosk-tts` | **Date**: 2025-12-12 | **Spec**: `specs/005-vosk-tts/spec.md`
**Input**: Feature specification from `/specs/005-vosk-tts/spec.md`

**Note**: Filled via `/speckit.plan`.

## Summary

Добавляем поддержку Vosk TTS как нового TTS-движка наряду с Silero и Piper. Vosk использует библиотеку vosk-tts с API `Model` + `Synth`. Реализация включает модуль синтеза `VoskSynthesis`, CLI утилиту `vosk_tts.py`, расширение enum `TTSEngine` и конфигурацию через env.

## Technical Context

**Language/Version**: Python 3.11 (uv-managed)  
**Primary Dependencies**: vosk-tts (pip), существующие aiogram/pyrogram для бота, pytest для тестов  
**Storage**: Локальные файлы моделей в кеше (скачиваются автоматически библиотекой vosk-tts)  
**Testing**: pytest (unit + integration), CLI contract tests  
**Target Platform**: Linux server/Docker  
**Project Type**: Single backend/CLI bot  
**Performance Goals**: Аудио для ≤1000 символов за ≤5 секунд в 95% запросов  
**Constraints**: env-driven конфиг, без авто-фолбэка, блокировка при ошибках модели  
**Scale/Scope**: Нагрузка телеграм-бота (десятки параллельных запросов), локальный inference

## Constitution Check

- Python-first с uv; модули исполнимы по отдельности — соблюдается.
- Синтез через сменные реализации с CLI — добавляем Vosk CLI.
- Telegram whitelist из env — не затрагиваем.
- Текстовый лог с таймстампами шагов синтеза — расширяем логами Vosk.
- Конфиг из env, Docker/uv — соблюдаем.
- YAGNI: только vosk-tts как зависимость.

## Project Structure

### Documentation (this feature)

```text
specs/005-vosk-tts/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md            # via /speckit.tasks
```

### Source Code (repository root)

```text
src/
├── bot/
│   ├── handlers.py
│   ├── worker.py
│   └── ...
├── cli/
│   ├── silero_tts.py
│   ├── piper_tts.py
│   └── vosk_tts.py          # new
├── synthesis/
│   ├── __init__.py
│   ├── interface.py
│   ├── silero.py
│   ├── piper.py
│   ├── vosk.py              # new
│   └── types.py             # extend TTSEngine
└── utils/
    └── config.py            # add VoskConfig

tests/
├── integration/
└── unit/
```

**Structure Decision**: Сохраняем существующий single-project layout; добавляем Vosk провайдер и CLI рядом с существующими, расширяем enum и конфиг.

## Complexity Tracking

None identified.

## Phase 0: Outline & Research

### Unknowns / Research items
- API vosk-tts: классы Model и Synth, метод synth().
- Доступные модели для русского языка и диапазон speaker_id.
- Формат выходного аудио (wav).

### research.md

См. `specs/005-vosk-tts/research.md` с решениями.

## Phase 1: Design & Contracts

### Data Model
- VoskConfig: model_name, speaker_id, audio_format, cache_dir, metrics_path.
- TTSEngine.VOSK: новое значение enum.
- Интеграция в общий Config.

### API / CLI Contracts
- CLI: `vosk_tts.py` с аргументами --text/--text-file, --out, --model, --speaker-id, --format.
- Synthesis: метод `synth(text, prefix, out_path) -> SynthesisResult`.

### Quickstart
- Установка vosk-tts, настройка env, тест через CLI.

### Agent Context
- Обновить контекст агента после фиксации технологий.

## Phase 2: Tasks (delegated)

- После завершения плана вызвать `/speckit.tasks` для генерации задач.

