# Data Model: Text Preprocessing with LLM

**Feature**: 006-text-preprocessing-llm  
**Date**: 2025-12-12

## Entities

### LLMConfig

Конфигурация подключения к LLM API.

```python
@dataclass(frozen=True)
class LLMConfig:
    api_url: str                    # Base URL для API
    api_key: str                    # API ключ
    model: str                      # Название модели
    temperature: float              # Temperature (0.0-2.0)
    top_p: float                    # Top-p sampling (0.0-1.0)
    timeout: int                    # Таймаут в секундах
    max_retries: int                # Количество retry
    system_prompt_path: Path | None # Путь к файлу промпта
    cache_system_prompt: bool       # Кешировать промпт
    min_chunk_size: int             # Мин. размер чанка (символы)
    max_tokens: int                 # Макс. токенов на запрос
    enabled: bool                   # LLM включён
```

**Validation rules**:
- `api_key` required если `enabled=True`
- `system_prompt_path` если указан — файл должен существовать
- `temperature` в диапазоне [0.0, 2.0]
- `top_p` в диапазоне [0.0, 1.0]
- `timeout` > 0
- `max_retries` >= 0
- `min_chunk_size` > 0
- `max_tokens` > 0

### TextChunk

Часть текста для обработки LLM.

```python
@dataclass
class TextChunk:
    text: str           # Текст чанка
    start_index: int    # Начальная позиция в исходном тексте
    end_index: int      # Конечная позиция в исходном тексте
```

### PreprocessResult

Результат препроцессинга текста.

```python
@dataclass
class PreprocessResult:
    text: str                       # Обработанный текст
    llm_used: bool                  # Использовался ли LLM
    chunks_processed: int           # Количество обработанных чанков
    llm_calls: int                  # Количество вызовов LLM
    fallback_used: bool             # Использовался ли fallback
    errors: list[str]               # Список ошибок (для логирования)
```

### TranslitConfig

Конфигурация программной транслитерации (из JSON файла).

```python
@dataclass
class TranslitConfig:
    abbreviations: dict[str, str]  # "API" → "эй пи ай"
    symbols: dict[str, str]        # "%" → "процент"
```

**File**: `config/transliteration.json`

## State Transitions

### Processing Flow

```
[Input Text]
     │
     ▼
┌─────────────────────────────────┐
│ 1. БАЗОВАЯ ОЧИСТКА (всегда)    │
│    - Удаление emoji             │
│    - Пунктуация                 │
│    - Капитализация              │
└─────────────────────────────────┘
     │
     ▼
[LLM Enabled?] ──No──┐
     │Yes            │
     ▼               ▼
┌────────────┐  ┌─────────────────────────┐
│ 2a. LLM    │  │ 2b. ПРОГРАММНАЯ         │
│ обработка  │  │ ТРАНСЛИТЕРАЦИЯ          │
└────────────┘  │  - num2words (числа)    │
     │          │  - словарь аббревиатур  │
     ▼          │  - словарь символов     │
[Validate]      └─────────────────────────┘
     │                    │
     ▼                    │
[Invalid?]──Yes──┐        │
     │No         │        │
     │           ▼        │
     │    [Retry?]──No──┐ │
     │      │Yes        │ │
     │      ▼           │ │
     │    [LLM]─────────┘ │
     │           │        │
     │           ▼        │
     │    ┌──────────────┐│
     │    │ ПРОГРАММНОЕ  ││
     │    │ ИСПРАВЛЕНИЕ  ││
     │    │ проблемных   ││
     │    │ мест         ││
     │    └──────────────┘│
     │           │        │
     ▼           ▼        ▼
     └───────────┴────────┘
              │
              ▼
        [Output Text]
```

## Relationships

```
Config (1..*) ──contains──> LLMConfig (0..1)
     │
     └──────────────────────> TTSConfig (1)

TextPreprocessor ──uses──> LLMConfig
                 ──uses──> LLMClient
                 ──produces──> PreprocessResult

LLMClient ──configured by──> LLMConfig
          ──calls──> OpenAI API
```

## Integration with Existing Model

Расширение существующего `Config` в `src/utils/config.py`:

```python
@dataclass(frozen=True)
class Config:
    # ... existing fields ...
    llm: LLMConfig  # Новое поле
```

