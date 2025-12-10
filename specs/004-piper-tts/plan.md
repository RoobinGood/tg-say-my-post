# Implementation Plan: Piper TTS support and model switching

**Branch**: `004-piper-tts` | **Date**: 2025-12-10 | **Spec**: `specs/004-piper-tts/spec.md`
**Input**: Feature specification from `/specs/004-piper-tts/spec.md`

**Note**: Filled via `/speckit.plan`.

## Summary

Добавляем поддержку Piper как TTS-движка наряду с Silero, с выбором движка и модели через конфигурацию. Требования: локальные веса Piper с авто-скачиванием при старте, единый лимит длины текста, отсутствие авто-фолбэка при недоступности движка, дружелюбные ошибки пользователю и подробное логирование.

## Technical Context

**Language/Version**: Python 3.11 (uv-managed)
**Primary Dependencies**: aiogram/pyrogram stack for bot, existing Silero TTS client, планируемый Piper TTS клиент + CLI обёртка, logging/metrics (стандартный logging + структурированные записи), pytest для тестов
**Storage**: Локальные файлы весов (кеш), конфиг из env; БД не затрагивается
**Testing**: pytest (unit + integration для ботовых потоков и CLI), возможны контрактные проверки CLI
**Target Platform**: Linux server/Docker
**Project Type**: Single backend/CLI bot
**Performance Goals**: Аудио для ≤1000 символов за ≤5 секунд в 95% запросов
**Constraints**: env-driven конфиг (движок, модель, лимит текста, пути кеша), отсутствие авто-фолбэка, блокировка старта при некорректных весах, p95 синтеза ≤5s
**Scale/Scope**: Нагрузка телеграм-бота (десятки параллельных запросов), локальный inference

## Constitution Check

- Python-first с uv; модули исполнимы по отдельности — соблюдается.
- Синтез через сменные реализации с CLI — нужно сохранить и добавить Piper CLI.
- Telegram whitelist из env — не затрагиваем, оставить как есть.
- Текстовый лог с таймстампами шагов синтеза — расширяем логами Piper.
- Конфиг из env, Docker/uv — соблюдаем.
- YAGNI: только нужные зависимости для Piper.

## Project Structure

### Documentation (this feature)

```text
specs/004-piper-tts/
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
│   ├── models.py
│   └── prefix.py
├── cli/
│   ├── silero_tts.py
│   └── piper_tts.py          # new
├── synthesis/
│   ├── __init__.py
│   ├── silero.py
│   └── piper.py              # new
└── utils/
    └── config.py

tests/
├── integration/
└── unit/
```

**Structure Decision**: Сохраняем существующий single-project layout; добавляем Piper провайдер и CLI рядом с Silero, расширяем конфиг и тесты в текущих директориях.

## Complexity Tracking

None identified.

## Phase 0: Outline & Research

### Unknowns / Research items
- Проверить требования к весам Piper (формат, размер, источники, проверка checksum/размер).
- Выяснить рекомендуемые языковые/голосовые модели Piper для русского и их именование.
- Уточнить оптимальные параметры запуска Piper (CPU-only/ ускорения) для достижения p95 ≤5s.

### research.md

Создать `specs/004-piper-tts/research.md` со списком решений: Decision, Rationale, Alternatives.

## Phase 1: Design & Contracts

### Data Model
- Извлечь из спека сущности: настройка движка TTS (engine, model, text_limit, cache_dir), профиль модели (язык/голос), кеш весов (путь, checksum/size).
- Задокументировать в `specs/004-piper-tts/data-model.md` поля, валидации, отношения.

### API / CLI Contracts
- Piper CLI интерфейс по аналогии с silero_tts: вход (текст, настройки модели/пути), выход (аудио-файл/поток, метаданные длительности), ошибки (валидные коды/сообщения). Задокументировать в `specs/004-piper-tts/contracts/README.md`.

### Quickstart
- Добавить шаги включения Piper: установка зависимостей, подготовка/скачивание весов, настройка env (движок, модель, лимит, кеш), тестовый синтез через CLI. Записать в `specs/004-piper-tts/quickstart.md`.

### Agent Context
- Обновить контекст агента: `.specify/scripts/bash/update-agent-context.sh cursor-agent` после фиксации ключевых технологий (Piper TTS, CLI flow, env-driven конфиг).

## Phase 2: Tasks (delegated)

- После завершения плана вызвать `/speckit.tasks` для генерации задач на основе спека и плана.

