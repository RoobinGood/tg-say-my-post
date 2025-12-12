# Contract: Programmatic Transliteration

**Module**: `src/bot/translit.py`

## Interface

### transliterate_programmatic

```python
def transliterate_programmatic(text: str, config_path: Path | None = None) -> str:
    """
    Программная транслитерация текста.
    
    Args:
        text: Текст для обработки
        config_path: Путь к JSON с картой транслитерации (default: config/transliteration.json)
    
    Returns:
        Текст с заменёнными числами, аббревиатурами и символами
    """
```

### fix_invalid_chars

```python
def fix_invalid_chars(text: str, config_path: Path | None = None) -> str:
    """
    Исправляет невалидные символы в тексте (после LLM).
    
    Args:
        text: Текст с возможными невалидными символами
        config_path: Путь к JSON с картой транслитерации
    
    Returns:
        Текст только с кириллицей и пунктуацией
    """
```

## Config File Format

**Path**: `config/transliteration.json`

```json
{
  "abbreviations": {
    "API": "эй пи ай",
    "URL": "ю ар эл",
    "HTTP": "эйч ти ти пи",
    "HTTPS": "эйч ти ти пи эс",
    "JSON": "джейсон",
    "XML": "икс эм эл",
    "HTML": "эйч ти эм эл",
    "CSS": "си эс эс",
    "JS": "джей эс",
    "SQL": "эс ку эл",
    "AI": "ай ай",
    "ML": "эм эл",
    "IT": "ай ти",
    "PR": "пи ар",
    "HR": "эйч ар",
    "CEO": "си и о",
    "CTO": "си ти о",
    "USA": "ю эс эй",
    "UK": "ю кей"
  },
  "symbols": {
    "%": "процент",
    "$": "доллар",
    "€": "евро",
    "£": "фунт",
    "₽": "рубль",
    "@": "собака",
    "&": "и",
    "#": "хэштег",
    "°": "градус"
  },
  "units": {
    "km": "километр",
    "m": "метр",
    "cm": "сантиметр",
    "mm": "миллиметр",
    "kg": "килограмм",
    "g": "грамм",
    "mg": "миллиграмм",
    "l": "литр",
    "ml": "миллилитр"
  }
}
```

## Behavior Contracts

### Numbers (via num2words)

| Input | Output |
|-------|--------|
| `"1500"` | `"одна тысяча пятьсот"` |
| `"2.5"` | `"два целых пять десятых"` |
| `"1/4"` | `"одна четвёртая"` |
| `"-15"` | `"минус пятнадцать"` |
| `"100 рублей"` | `"сто рублей"` |

### Abbreviations (via config)

| Input | Output |
|-------|--------|
| `"API"` | `"эй пи ай"` |
| `"проверь API"` | `"проверь эй пи ай"` |
| `"Unknown"` | `"Unknown"` (оставить как есть) |

### Symbols (via config)

| Input | Output |
|-------|--------|
| `"50%"` | `"50 процент"` → `"пятьдесят процент"` |
| `"$100"` | `"доллар 100"` → `"сто доллар"` |

### Fix Invalid Chars

| Input | Output |
|-------|--------|
| `"текст with English"` | `"текст виз инглиш"` (простая транслитерация) |
| `"текст 123"` | `"текст сто двадцать три"` |

## Processing Order

1. Заменить известные аббревиатуры (case-insensitive)
2. Заменить символы из словаря
3. Заменить числа через num2words
4. Оставшуюся латиницу транслитерировать посимвольно (fallback)

