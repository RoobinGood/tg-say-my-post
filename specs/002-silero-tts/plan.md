# Implementation Plan: Silero TTS module with metrics

**Branch**: `[002-silero-tts]` | **Date**: 2025-12-10 | **Spec**: specs/002-silero-tts/spec.md
**Input**: Feature specification from `/specs/002-silero-tts/spec.md`

## Summary

Deliver Silero-based TTS module with metrics, configurable model_id/speaker and formats, a CLI to generate audio, and integration so the Telegram bot uses the configured synthesizer with safe fallbacks.

## Technical Context

**Language/Version**: Python 3.11 (per project `requires-python >=3.11`).  
**Primary Dependencies**: torch + silero-models (via torch hub or predownloaded files), python-telegram-bot, pydub, pytest/pytest-asyncio.  
**Storage**: Local filesystem for generated audio; no persistent DB.  
**Testing**: pytest + pytest-asyncio.  
**Target Platform**: Linux server in Docker.  
**Project Type**: Single project (CLI + bot).  
**Performance Goals**: ≤8s wall-clock для текста до 500 символов; детерминированный вывод при неизменной модели.  
**Constraints**: Конфиг из окружения, офлайн-доступность весов Silero, минимальные зависимости, прозрачные логи.  
**Scale/Scope**: Один бот/CLI экземпляр; последовательные запросы, умеренный объём.

## Constitution Check

- Python-first с `uv`: остаёмся на Python 3.11, зависимости через uv/pyproject.
- Плагины синтеза со swappable интерфейсом + CLI: Silero реализация будет модулем `synthesis` и отдельной CLI обёрткой.
- Telegram whitelist: интеграция в бота не нарушает whitelisting (остаётся в общих обработчиках).
- Текстовое логирование с таймстемпами: метрики/ошибки в логи stdout.
- Конфиг из окружения + Docker: путь к весам/голос/устройство/формат аудио из env/конфига, совместимо с Docker.
- Простота/YAGNI: только необходимая реализация Silero + метрики без лишних абстракций.

## Project Structure

### Documentation (this feature)

```text
specs/002-silero-tts/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── checklists/
```

### Source Code (repository root)

```text
src/
├── synthesis/            # интерфейс + реализации (добавить silero)
├── cli/                  # CLI команды (добавить silero_tts)
├── bot/                  # хендлеры и воркер бота (подключение модуля)
├── utils/                # config/logging/helpers
└── audio/                # тестовые/пример аудио

tests/
├── unit/
├── integration/
└── contract/
```

**Structure Decision**: Используем существующий single-project layout (`src` + `tests`), добавляя реализацию Silero в `src/synthesis` и CLI в `src/cli`; документацию/контракты в `specs/002-silero-tts`.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | No constitution violations anticipated | N/A |

