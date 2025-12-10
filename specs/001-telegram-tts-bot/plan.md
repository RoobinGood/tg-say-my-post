# Implementation Plan: Telegram TTS Bot

**Branch**: `001-telegram-tts-bot` | **Date**: 2025-12-10 | **Spec**: [`specs/001-telegram-tts-bot/spec.md`](./spec.md)
**Input**: Feature specification from `/specs/001-telegram-tts-bot/spec.md`

**Note**: Plan follows constitution requirements (Python+uv, pluggable synthesis CLI, env-driven whitelist, logging, simplicity).

## Summary

Telegram-бот принимает текстовые и пересланные сообщения, генерирует озвучку и отвечает голосовыми сообщениями. Заглушка синтеза возвращает тестовый mp3, чтобы обкатать интерфейс, очередь и корректные префиксы. Ограничение 2000 символов, whitelist и текстовое логирование сохраняются.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11 (uv-managed)
**Primary Dependencies**: python-telegram-bot, pydub (для mp3 handling), pytest
**Storage**: Нет постоянного хранилища (in-memory очереди)
**Testing**: pytest + минимальные unit/contract тесты
**Target Platform**: Linux/Docker
**Project Type**: Single backend service (Telegram bot)
**Performance Goals**: Голосовой ответ ≤10 секунд для 95% сообщений
**Constraints**: Макс 2000 символов на сообщение; whitelist из env; простой текстовый лог с таймстемпами
**Scale/Scope**: Одиночный бот, один процесс; малый объём сообщений

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Python + uv, модульные entrypoints: план соблюдать.
- Плагин для синтеза: интерфейс + CLI-заглушка с test mp3: план соблюдать.
- Whitelist из ENV: план соблюдать.
- Текстовое логирование с таймстемпами: план соблюдать.
- Конфиг через ENV; Docker совместимость: план соблюдать.
- YAGNI: только нужные зависимости (python-telegram-bot, pydub, pytest).

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
src/
├── bot/               # handlers, routing, main loop
├── synthesis/         # интерфейс + заглушка, CLI
├── audio/             # статика (example.mp3 для заглушки)
├── cli/               # запускаемые entrypoints (run_bot, synth_stub)
└── utils/             # логирование, конфиг, очереди

tests/
├── unit/
├── integration/
└── contract/
```

**Structure Decision**: Single backend service; каталог `src` с bot/synthesis/utils и CLI-энтрипоинтами, тесты в tests/.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | n/a | n/a |
