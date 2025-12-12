# Implementation Plan: Text Preprocessing with LLM

**Branch**: `006-text-preprocessing-llm` | **Date**: 2025-12-12 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/006-text-preprocessing-llm/spec.md`

## Summary

Рефакторинг модуля препроцессинга текста с добавлением LLM-транслитерации и программного fallback.

**Порядок обработки:**
1. Базовая очистка (всегда): emoji, пунктуация, капитализация
2. Транслитерация (настраивается):
   - LLM включён → обработка через LLM
   - LLM выключен → программная транслитерация (num2words + словарь)
3. Исправление (если LLM вернул невалидный результат): программная доочистка проблемных мест

**Компоненты:** OpenAI-совместимый API, num2words, JSON-словарь аббревиатур.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: openai, tiktoken, num2words, python-telegram-bot  
**Storage**: N/A (stateless processing)  
**Testing**: pytest, pytest-asyncio  
**Target Platform**: Linux server (Docker)  
**Project Type**: Single project  
**Performance Goals**: <10s для текста до 500 символов  
**Constraints**: LLM API latency, token limits  
**Scale/Scope**: Single bot instance, ~100 requests/day

## Constitution Check

*GATE: ✅ PASSED*

| Principle | Status | Notes |
|-----------|--------|-------|
| Python-first with `uv` | ✅ | openai, tiktoken — стандартные пакеты |
| Module-level runnable | ✅ | CLI для тестирования препроцессинга |
| Pluggable synthesis | ✅ | Не затрагивает synthesis interface |
| Whitelist enforcement | ✅ | Не затрагивает |
| Text logging | ✅ | Логирование LLM вызовов и ошибок |
| Env configuration | ✅ | Все LLM параметры через env |
| Simplicity/YAGNI | ✅ | Минимальные зависимости, без абстракций |

## Project Structure

### Documentation (this feature)

```text
specs/006-text-preprocessing-llm/
├── plan.md              # This file
├── research.md          # ✅ Phase 0 output
├── data-model.md        # ✅ Phase 1 output
├── quickstart.md        # ✅ Phase 1 output
├── contracts/           # ✅ Phase 1 output
│   ├── text-preprocessor.md
│   ├── llm-client.md
│   └── translit.md
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── bot/
│   ├── text_preprocess.py   # Расширить: добавить LLM интеграцию
│   ├── llm_client.py        # Новый: клиент LLM API
│   ├── translit.py          # Новый: программная транслитерация
│   └── ...
├── cli/
│   └── preprocess.py        # Новый: CLI для тестирования
└── utils/
    └── config.py            # Расширить: добавить LLMConfig

tests/
├── unit/
│   ├── test_text_preprocess.py  # Расширить
│   ├── test_llm_client.py       # Новый
│   └── test_translit.py         # Новый
└── integration/
    └── test_llm_integration.py  # Новый

config/
└── transliteration.json     # Карта транслитерации (аббревиатуры, символы)

prompts/
└── transliteration.txt      # Системный промпт по умолчанию
```

**Structure Decision**: Single project. Препроцессинг остаётся в `src/bot/`, новый `llm_client.py` добавляется туда же. CLI для тестирования в `src/cli/`.

## Complexity Tracking

Нет нарушений Constitution — таблица не требуется.

## Phase 0 Artifacts

- [research.md](research.md) — решения по OpenAI SDK, tiktoken, chunking strategy

## Phase 1 Artifacts

- [data-model.md](data-model.md) — LLMConfig, TranslitConfig, TextChunk, PreprocessResult
- [contracts/text-preprocessor.md](contracts/text-preprocessor.md) — API препроцессора
- [contracts/llm-client.md](contracts/llm-client.md) — API LLM клиента
- [contracts/translit.md](contracts/translit.md) — API программной транслитерации
- [quickstart.md](quickstart.md) — инструкция по настройке

## Dependencies to Add

```toml
openai = ">=1.0.0"
tiktoken = ">=0.5.0"
num2words = ">=0.5.0"
```

## Next Steps

Запустить `/speckit.tasks` для генерации задач на основе этого плана.
