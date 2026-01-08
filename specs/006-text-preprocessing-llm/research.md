# Research: Text Preprocessing with LLM

**Feature**: 006-text-preprocessing-llm  
**Date**: 2025-12-12

## Decision 1: OpenAI-compatible API Client

**Decision**: Использовать `openai` Python SDK

**Rationale**:
- Официальный SDK от OpenAI с полной поддержкой API
- Совместим с OpenAI-compatible провайдерами (Ollama, LM Studio, vLLM, etc.) через `base_url`
- Поддерживает async/await из коробки
- Активно поддерживается, хорошая документация
- Минимальные зависимости

**Alternatives considered**:
- `httpx` напрямую — больше boilerplate кода
- `litellm` — избыточен для одного провайдера, добавляет абстракцию
- `langchain` — слишком тяжёлый для простой задачи (нарушает YAGNI)

## Decision 2: Token Counting для Chunking

**Decision**: Использовать `tiktoken` для подсчёта токенов

**Rationale**:
- Официальная библиотека OpenAI для токенизации
- Быстрая (написана на Rust)
- Поддерживает все модели OpenAI
- Для non-OpenAI моделей: использовать cl100k_base как приближение

**Alternatives considered**:
- Считать по символам (chars / 4) — неточно, может привести к ошибкам
- `transformers` AutoTokenizer — тяжёлая зависимость
- Запрашивать у API — дополнительный latency

## Decision 3: Prompt Caching Strategy

**Decision**: Опциональное кеширование через параметр конфигурации

**Rationale**:
- OpenAI поддерживает prompt caching автоматически для длинных промптов
- Anthropic требует специальный формат `cache_control`
- Для локальных моделей кеширование не применимо
- Настройка `LLM_CACHE_SYSTEM_PROMPT=true/false` включает/отключает отправку системного промпта в отдельном сообщении

**Implementation**:
- Если кеширование включено: системный промпт в первом message с `role: system`
- Если выключено: системный промпт встраивается в user message

## Decision 4: Chunking Strategy

**Decision**: Разбиение по абзацам с учётом минимального размера

**Rationale**:
- Абзацы — естественные смысловые единицы текста
- Минимальный размер чанка предотвращает слишком частые вызовы API
- Если абзац превышает лимит — разбивать по предложениям

**Algorithm**:
1. Разбить текст на абзацы
2. Накапливать абзацы пока размер < min_chunk_size
3. Если накопленный размер > max_tokens — отправить чанк
4. Если один абзац > max_tokens — разбить по предложениям

## Decision 5: Response Validation

**Decision**: Regex-валидация + retry

**Rationale**:
- Простая проверка: текст содержит только кириллицу, пунктуацию и знак +
- При провале — retry с тем же промптом (LLM может выдать другой результат)
- После исчерпания retry — fallback на программную очистку

**Validation regex**: `^[а-яА-ЯёЁіІїЇєЄґҐ\s\d\.,!?;:\-—–""''«»()+\n]+$`

## Decision 6: Programmatic Transliteration (Fallback)

**Decision**: Использовать `num2words` + словарь аббревиатур в JSON файле

**Rationale**:
- `num2words` — зрелая библиотека с поддержкой русского языка
- Словарь аббревиатур в отдельном файле — легко расширять без изменения кода
- Программный fallback работает когда LLM выключен или даёт невалидный результат

**Implementation**:
```python
from num2words import num2words
num2words(1500, lang='ru')  # "одна тысяча пятьсот"
num2words(2.5, lang='ru')   # "два целых пять десятых"
```

**Transliteration map** (`config/transliteration.json`):
```json
{
  "abbreviations": {
    "API": "эй пи ай",
    "URL": "ю ар эл",
    "HTTP": "эйч ти ти пи",
    "JSON": "джейсон",
    "XML": "икс эм эл"
  },
  "symbols": {
    "%": "процент",
    "$": "доллар",
    "€": "евро",
    "@": "собака",
    "&": "и"
  }
}
```

## Dependencies to Add

```toml
[project.dependencies]
openai = ">=1.0.0"
tiktoken = ">=0.5.0"
num2words = ">=0.5.0"
```

## Configuration Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| LLM_API_URL | str | https://api.openai.com/v1 | Base URL для API |
| LLM_API_KEY | str | required | API ключ |
| LLM_MODEL | str | gpt-4o-mini | Название модели |
| LLM_TEMPERATURE | float | 0.3 | Temperature для генерации |
| LLM_TOP_P | float | 1.0 | Top-p sampling |
| LLM_TIMEOUT | int | 30 | Таймаут запроса в секундах |
| LLM_MAX_RETRIES | int | 2 | Количество retry при ошибке |
| LLM_SYSTEM_PROMPT_PATH | str | None | Путь к файлу с промптом |
| LLM_CACHE_SYSTEM_PROMPT | bool | false | Кешировать системный промпт |
| LLM_MIN_CHUNK_SIZE | int | 500 | Минимальный размер чанка в символах |
| LLM_MAX_TOKENS | int | 4000 | Максимум токенов на запрос |
| LLM_ENABLED | bool | true | Включить LLM обработку |

