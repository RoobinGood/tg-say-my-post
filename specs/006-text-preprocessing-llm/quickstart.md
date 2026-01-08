# Quickstart: Text Preprocessing with LLM

## Prerequisites

- Python 3.11+
- uv package manager
- OpenAI-compatible API (OpenAI, Ollama, LM Studio, etc.)

## Installation

```bash
# Добавить зависимости
uv add openai tiktoken num2words
```

## Configuration

Добавить в `.env`:

```bash
# Обязательные
LLM_API_KEY=sk-...

# Опциональные (показаны дефолты)
LLM_API_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.3
LLM_TOP_P=1.0
LLM_TIMEOUT=30
LLM_MAX_RETRIES=2
LLM_MIN_CHUNK_SIZE=500
LLM_MAX_TOKENS=4000
LLM_ENABLED=true

# Кастомный промпт (опционально)
LLM_SYSTEM_PROMPT_PATH=/path/to/prompt.txt
LLM_CACHE_SYSTEM_PROMPT=false
```

### Для локальных моделей (Ollama)

```bash
LLM_API_URL=http://localhost:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=llama3.2
```

### Для LM Studio

```bash
LLM_API_URL=http://localhost:1234/v1
LLM_API_KEY=lm-studio
LLM_MODEL=local-model
```

## Usage

### В коде

```python
from src.bot.text_preprocess import preprocess_text
from src.utils.config import load_config

config = load_config()
text = "Цена API составляет $100 за 1000 запросов"
result = preprocess_text(text, config.llm)
# "Цена эй пи ай составляет сто долларов за тысячу запросов"
```

### CLI (для тестирования)

```bash
# С LLM
echo "Тест API v2.5" | python -m src.cli.preprocess

# Без LLM (только программная очистка)
LLM_ENABLED=false echo "Тест 👋" | python -m src.cli.preprocess
```

## Testing

```bash
# Unit тесты
uv run pytest tests/unit/test_text_preprocess.py -v

# Integration тесты (требуют API)
LLM_API_KEY=sk-... uv run pytest tests/integration/test_llm_client.py -v
```

## Transliteration Config

Карта транслитерации хранится в `config/transliteration.json`:

```json
{
  "abbreviations": {
    "API": "эй пи ай",
    "URL": "ю ар эл"
  },
  "symbols": {
    "%": "процент",
    "$": "доллар"
  }
}
```

Расширяйте словарь по мере необходимости.

## Verification Checklist

- [ ] `LLM_API_KEY` установлен (или `LLM_ENABLED=false`)
- [ ] Текст с латиницей транслитерируется в кириллицу
- [ ] Числа преобразуются в слова
- [ ] Аббревиатуры из словаря заменяются
- [ ] При выключенном LLM программная транслитерация работает
- [ ] Длинные тексты разбиваются на чанки

