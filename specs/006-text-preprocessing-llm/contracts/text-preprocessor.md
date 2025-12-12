# Contract: TextPreprocessor

**Module**: `src/bot/text_preprocess.py`

## Interface

### preprocess_text

Основная функция препроцессинга текста.

```python
def preprocess_text(text: str, llm_config: LLMConfig | None = None) -> str:
    """
    Обрабатывает текст для TTS синтеза.
    
    Args:
        text: Исходный текст
        llm_config: Конфигурация LLM (None = только программная очистка)
    
    Returns:
        Обработанный текст (кириллица + пунктуация)
    
    Raises:
        ValueError: Если текст пустой после обработки
    """
```

### preprocess_text_with_result

Расширенная версия с метаданными.

```python
def preprocess_text_with_result(
    text: str, 
    llm_config: LLMConfig | None = None
) -> PreprocessResult:
    """
    Обрабатывает текст и возвращает результат с метаданными.
    
    Args:
        text: Исходный текст
        llm_config: Конфигурация LLM
    
    Returns:
        PreprocessResult с обработанным текстом и статистикой
    """
```

## Behavior Contracts

### Programmatic Cleanup (всегда выполняется)

| Input | Output |
|-------|--------|
| `"👋 привет"` | `"- Привет."` |
| `"текст без точки"` | `"Текст без точки."` |
| `"текст."` | `"Текст."` |
| `"смотри https://example.com тут"` | `"Смотри тут."` |
| `"ссылка: http://test.ru"` | `"Ссылка."` |
| `""` | ValueError |
| `"   "` | ValueError |

### LLM Transliteration (если llm_config != None и enabled)

| Input | Output (примерный) |
|-------|-------------------|
| `"API версии 2.5"` | `"эй пи ай версии два целых пять десятых"` |
| `"цена $100"` | `"цена сто долларов"` |
| `"50%"` | `"пятьдесят процентов"` |
| `"замок на двери"` | `"зам+ок на двери"` |

### Fallback Behavior

| Condition | Behavior |
|-----------|----------|
| `llm_config is None` | Только программная очистка |
| `llm_config.enabled = False` | Только программная очистка |
| LLM API недоступен | Программная очистка + log error |
| Невалидный ответ LLM после retry | Программная очистка + log error |

## Error Handling

| Error | Handling |
|-------|----------|
| Пустой текст | `ValueError("empty text")` |
| LLM timeout | Retry → Fallback → log |
| LLM rate limit | Retry с backoff → Fallback → log |
| Invalid API key | Fallback → log error |
| Network error | Retry → Fallback → log |

