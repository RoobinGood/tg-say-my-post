# Contract: LLMClient

**Module**: `src/bot/llm_client.py`

## Interface

### LLMClient class

```python
class LLMClient:
    def __init__(self, config: LLMConfig) -> None:
        """
        Инициализирует клиент LLM API.
        
        Args:
            config: Конфигурация LLM
        
        Raises:
            FileNotFoundError: Если system_prompt_path указан, но файл не существует
            ValueError: Если config невалиден
        """
    
    def transliterate(self, text: str) -> str:
        """
        Выполняет фонетическую транслитерацию текста.
        
        Args:
            text: Текст для транслитерации
        
        Returns:
            Транслитерированный текст (кириллица + пунктуация)
        
        Raises:
            LLMError: При ошибке API после всех retry
            LLMValidationError: При невалидном ответе после всех retry
        """
    
    def transliterate_chunks(self, chunks: list[TextChunk]) -> list[str]:
        """
        Транслитерирует список чанков.
        
        Args:
            chunks: Список чанков текста
        
        Returns:
            Список транслитерированных текстов
        """
```

### Exceptions

```python
class LLMError(Exception):
    """Базовая ошибка LLM."""
    pass

class LLMValidationError(LLMError):
    """Ответ LLM не прошёл валидацию."""
    pass

class LLMTimeoutError(LLMError):
    """Таймаут запроса к LLM."""
    pass
```

## System Prompt Contract

Системный промпт должен инструктировать LLM:

```text
Ты — препроцессор текста для русскоязычного синтеза речи.

Твоя задача:
1. Заменить все слова и аббревиатуры на латинице на фонетическую запись кириллицей
2. Заменить все числа на словесное произношение:
   - Целые: 1500 → тысяча пятьсот
   - Десятичные: 2.5 → два целых пять десятых
   - Дроби: 1/4 → одна четвёртая
3. Заменить специальные символы на слова:
   - % → процентов/процента
   - $ → долларов/доллара
   - € → евро
   - @ → собака/эт
   - & → и
4. Расставить ударения в омографах знаком + перед ударной гласной:
   - замок (дверной) → зам+ок
   - замок (крепость) → з+амок

Правила:
- Сохраняй структуру текста (абзацы, пунктуацию)
- Не добавляй ничего от себя
- Не меняй слова на кириллице
- Украинские/белорусские буквы оставляй как есть
- Возвращай ТОЛЬКО обработанный текст без комментариев
```

## Validation Contract

Ответ LLM валиден если:

```python
VALID_CHARS_REGEX = re.compile(
    r'^[а-яА-ЯёЁіІїЇєЄґҐ'  # Кириллица (рус + укр + бел)
    r'\s'                   # Пробелы
    r'\d'                   # Цифры (могут остаться в датах)
    r'\.,!?;:\-—–'          # Пунктуация
    r'""\'\'«»'             # Кавычки
    r'()\[\]'               # Скобки
    r'\+'                   # Знак ударения
    r'\n]+$'                # Переносы строк
)

def is_valid_response(text: str) -> bool:
    return bool(VALID_CHARS_REGEX.match(text))
```

## Retry Behavior

| Attempt | Action |
|---------|--------|
| 1 | Call LLM API |
| 2..N | Retry если timeout/rate limit/invalid response |
| N+1 | Raise LLMError/LLMValidationError |

Backoff: exponential с jitter (1s, 2s, 4s...)

