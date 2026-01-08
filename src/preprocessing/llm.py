import asyncio
import random
from pathlib import Path
from typing import Optional

from openai import AsyncOpenAI
from openai import Timeout as OpenAITimeout

from src.preprocessing.chunking import TextChunk
from src.preprocessing.validation import validate_response
from src.utils.config import LLMConfig
from src.utils.logging import get_logger


class LLMError(Exception):
    """Base LLM error."""
    pass


class LLMValidationError(LLMError):
    """LLM response validation failed."""
    pass


class LLMTimeoutError(LLMError):
    """LLM request timeout."""
    pass


def _load_system_prompt(config: LLMConfig, project_root: Path) -> str:
    if config.system_prompt_path:
        if not config.system_prompt_path.exists():
            raise FileNotFoundError(f"System prompt file not found: {config.system_prompt_path}")
        with open(config.system_prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    default_prompt_path = project_root / "src" / "preprocessing" / "prompts" / "transliteration.txt"
    if default_prompt_path.exists():
        with open(default_prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    return """Ты — препроцессор текста для русскоязычного синтеза речи.

Твоя задача:
1. Заменить все слова и аббревиатуры написанные не на кириллице на фонетическую запись кириллицей
2. Заменить все числа и дроби на словесное произношение
3. Заменить специальные символы на слова
4. Расставить ударения в омографах знаком + перед ударной гласной

Правила:
- Сохраняй структуру текста (абзацы, пунктуацию)
- Не добавляй ничего от себя
- Не меняй слова на кириллице
- Украинские/белорусские буквы оставляй как есть
- Возвращай ТОЛЬКО обработанный текст без комментариев"""


class LLMClient:
    def __init__(self, config: LLMConfig) -> None:
        if not config.enabled:
            raise ValueError("LLM is disabled in config")

        if not config.api_key:
            raise ValueError("LLM_API_KEY is required")

        project_root = Path(__file__).resolve().parents[2]
        self.config = config
        self.log = get_logger(__name__)
        self._system_prompt = _load_system_prompt(config, project_root)

        self._client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.api_url,
            timeout=OpenAITimeout(config.timeout),
        )

    async def transliterate(self, text: str) -> str:
        """Transliterate text using LLM."""
        for attempt in range(self.config.max_retries + 1):
            try:
                messages = []
                if self.config.cache_system_prompt:
                    messages.append({"role": "system", "content": self._system_prompt})
                    messages.append({"role": "user", "content": text})
                else:
                    messages.append({"role": "user", "content": f"{self._system_prompt}\n\n{text}"})

                response = await self._client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    temperature=self.config.temperature,
                    top_p=self.config.top_p,
                    max_tokens=self.config.max_tokens,
                )

                result_text = response.choices[0].message.content.strip()

                if validate_response(result_text):
                    self.log.debug("LLM transliteration successful, attempt %d", attempt + 1)
                    return result_text
                else:
                    self.log.warning("LLM response validation failed, attempt %d", attempt + 1)
                    if attempt < self.config.max_retries:
                        await asyncio.sleep(2 ** attempt + random.uniform(0, 1))
                        continue
                    raise LLMValidationError(f"Invalid response after {self.config.max_retries + 1} attempts")

            except asyncio.TimeoutError:
                self.log.warning("LLM timeout, attempt %d", attempt + 1)
                if attempt < self.config.max_retries:
                    await asyncio.sleep(2 ** attempt + random.uniform(0, 1))
                    continue
                raise LLMTimeoutError(f"Timeout after {self.config.max_retries + 1} attempts")

            except (LLMValidationError, LLMTimeoutError):
                raise

            except Exception as exc:
                self.log.error("LLM error: %s, attempt %d", exc, attempt + 1)
                if attempt < self.config.max_retries:
                    await asyncio.sleep(2 ** attempt + random.uniform(0, 1))
                    continue
                raise LLMError(f"LLM API error: {exc}") from exc

        raise LLMError("Max retries exceeded")

    async def transliterate_chunks(self, chunks: list[TextChunk]) -> list[str]:
        """Transliterate multiple chunks using LLM."""
        results = []
        for chunk in chunks:
            try:
                result = await self.transliterate(chunk.text)
                results.append(result)
                self.log.debug("Processed chunk %d-%d", chunk.start_index, chunk.end_index)
            except Exception as exc:
                self.log.error("Failed to process chunk %d-%d: %s", chunk.start_index, chunk.end_index, exc)
                results.append(chunk.text)
        return results

