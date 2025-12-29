# Telegram TTS Bot

Stub implementation for Telegram text-to-speech bot with queueing and synthesis placeholder.


## bot

```sh
uv run python -m src.cli.run_bot
```

## text preprocessing

Text preprocessing includes:
- Basic cleanup: emoji removal, URL removal, capitalization, punctuation
- LLM transliteration: Latin → Cyrillic, numbers → words, stress marks (if LLM enabled)
- Programmatic fallback: num2words + dictionary-based transliteration (if LLM disabled)

### Configuration

#### Pipeline stages

`PREPROCESSING_STAGES` — список стадий обработки через запятую (по умолчанию: `basic,abbreviations,symbols,numbers,latin_letters`).

Доступные стадии:
- `basic` — удаляет URL и эмодзи, капитализирует начало абзацев и добавляет точки в конце абзацев
- `abbreviations` — заменяет известные аббревиатуры из словаря (например, API → "эй пи ай") и транслитерирует неизвестные по буквам
- `symbols` — заменяет специальные символы на слова по словарю (например, % → "процент", $ → "доллар")
- `numbers` — преобразует числа, дроби и десятичные дроби в словесное произношение (например, 2.5 → "две целых пять десятых")
- `latin_letters` — транслитерирует латинские буквы в кириллицу по словарю (например, a → а, b → б)
- `llm` — использует LLM для транслитерации латиницы, чисел и символов, а также для расстановки ударений в омографах (требует `LLM_ENABLED=true`)

Пример: `PREPROCESSING_STAGES=basic,numbers,latin_letters,llm`

#### LLM settings

- `LLM_ENABLED` (по умолчанию: `true`) — включить/выключить LLM-транслитерацию
- `LLM_API_URL` (по умолчанию: `https://api.openai.com/v1`) — базовый URL API
- `LLM_API_KEY` (обязательно, если `LLM_ENABLED=true`) — API ключ
- `LLM_MODEL` (по умолчанию: `gpt-4o-mini`) — название модели
- `LLM_TEMPERATURE` (по умолчанию: `0.3`, диапазон: `0.0-2.0`) — температура генерации
- `LLM_TOP_P` (по умолчанию: `1.0`, диапазон: `0.0-1.0`) — top-p sampling
- `LLM_TIMEOUT` (по умолчанию: `30`) — таймаут запроса в секундах
- `LLM_MAX_RETRIES` (по умолчанию: `2`) — количество повторных попыток
- `LLM_SYSTEM_PROMPT_PATH` — путь к файлу с системным промптом (опционально)
- `LLM_CACHE_SYSTEM_PROMPT` (по умолчанию: `false`) — кешировать системный промпт
- `LLM_MIN_CHUNK_SIZE` (по умолчанию: `500`) — минимальный размер чанка в символах
- `LLM_MAX_TOKENS` (по умолчанию: `4000`) — максимальное количество токенов на запрос

Если `LLM_ENABLED=false` или LLM недоступен, используется программная транслитерация (num2words + словарь).

### Testing preprocessing

```sh
# Basic usage
echo "API версии 2.5" | uv run python -m src.cli.preprocess

# With detailed metrics
echo "API версии 2.5" | uv run python -m src.cli.preprocess --with-result
```

## backlog

[ ] README
