# Implementation Plan: MeloTTS support and model switching

**Branch**: `003-melotts-tts` | **Date**: 2025-12-10 | **Spec**: `specs/003-melotts-tts/spec.md`
**Input**: Feature specification from `/specs/003-melotts-tts/spec.md`

**Note**: Filled via `/speckit.plan`.

## Summary

Фича отклонена: у MeloTTS нет русской модели, ценность для бота недостаточна; реализация не требуется, сохраняем текущие решения на Silero.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: uv (runtime/packaging), Telegram bot library (aiogram/pyrogram already in repo), existing Silero TTS client; добавить MeloTTS клиент + CLI обёртку.  
**Storage**: N/A (конфиг из окружения, файлы модели/кэши локально при необходимости).  
**Testing**: pytest; для CLI/worker — интеграционные проверки синтеза.  
**Target Platform**: Linux server/Docker.  
**Project Type**: Single backend/cli bot.  
**Performance Goals**: Аудио для ≤1000 символов за ≤5 секунд в 95% запросов.  
**Constraints**: p95 синтеза ≤5s, стабильность при недоступности движка, конфигурируемый лимит текста.  
**Scale/Scope**: Нагрузка телеграм-бота с умеренным числом пользователей; параллельных запросов — десятки.

## Constitution Check

- Python-first с `uv`; модули исполнимы по отдельности — соблюдается.
- Синтез через сменные реализации с CLI — сохранить и расширить MeloTTS.
- Telegram whitelist из окружения — не затрагивается, оставить.
- Текстовый лог с таймстампами шагов синтеза — сохраняем/расширяем.
- Конфиг из env, Docker/uv — соблюдаем.
- YAGNI: только нужные зависимости для MeloTTS.

## Project Structure

### Documentation (this feature)

```text
specs/003-melotts-tts/
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
│   └── melo_tts.py
└── utils/
    └── config.py

tests/
└── (add unit/integration for TTS selection)
```

**Structure Decision**: Single-project layout under `src/` with bot, cli, utils; docs under `specs/003-melotts-tts/`.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
