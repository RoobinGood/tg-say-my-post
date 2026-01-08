import os
from dataclasses import dataclass
from typing import Callable, Optional

from src.preprocessing import basic, programmatic
from src.preprocessing.chunking import split_into_chunks
from src.preprocessing.llm import LLMClient, LLMError, LLMValidationError
from src.utils.config import LLMConfig
from src.utils.logging import get_logger


@dataclass
class PreprocessResult:
    text: str
    llm_used: bool
    chunks_processed: int
    llm_calls: int
    fallback_used: bool
    errors: list[str]
    stages_used: list[str]


_VALID_STAGES = {"basic", "abbreviations", "symbols", "numbers", "latin_letters", "paragraph_pauses", "llm"}


def _parse_pipeline_stages(env_value: Optional[str] = None) -> list[str]:
    if env_value is None:
        env_value = os.getenv("PREPROCESSING_STAGES")

    if not env_value:
        return ["basic", "abbreviations", "symbols", "numbers", "latin_letters"]

    stages = [stage.strip() for stage in env_value.split(",") if stage.strip()]

    invalid_stages = [s for s in stages if s not in _VALID_STAGES]
    if invalid_stages:
        log = get_logger(__name__)
        log.warning("Unknown preprocessing stages: %s. Valid stages: %s", invalid_stages, sorted(_VALID_STAGES))

    valid_stages = [s for s in stages if s in _VALID_STAGES]

    return valid_stages if valid_stages else ["basic", "abbreviations", "symbols", "numbers", "latin_letters"]


def _stage_basic(text: str) -> str:
    text_no_urls = basic.remove_urls(text)
    lines = text_no_urls.split("\n")
    cleaned_lines: list[str] = []
    for line in lines:
        line_with_dash = basic.replace_leading_emoji_with_dash(line)
        line_no_emojis = basic.remove_emojis(line_with_dash)
        cleaned_lines.append(line_no_emojis)

    capitalized_lines = basic.capitalize_paragraphs(cleaned_lines)
    punctuated_lines = basic.ensure_paragraph_periods(capitalized_lines)
    return "\n".join(punctuated_lines)


def _stage_paragraph_pauses(text: str) -> str:
    return basic.enhance_paragraph_pauses(text)


def _stage_abbreviations(text: str) -> str:
    return programmatic.transliterate_abbreviations(text)


def _stage_symbols(text: str) -> str:
    return programmatic.transliterate_symbols(text)


def _stage_numbers(text: str) -> str:
    return programmatic.transliterate_numbers(text)


def _stage_latin_letters(text: str) -> str:
    return programmatic.transliterate_latin_letters(text)


async def _stage_llm(text: str, llm_config: LLMConfig) -> tuple[str, int, int]:
    client = LLMClient(llm_config)
    chunks = split_into_chunks(text, llm_config.min_chunk_size, llm_config.max_tokens)
    transliterated_chunks = await client.transliterate_chunks(chunks)
    result_text = "\n\n".join(transliterated_chunks)
    return result_text, len(chunks), len(chunks)


async def _preprocess_text_async(
    text: str,
    llm_config: Optional[LLMConfig] = None,
    stages: Optional[list[str]] = None,
) -> PreprocessResult:
    if not text:
        return PreprocessResult(
            text="",
            llm_used=False,
            chunks_processed=0,
            llm_calls=0,
            fallback_used=False,
            errors=[],
            stages_used=[],
        )

    if stages is None:
        stages = _parse_pipeline_stages()

    errors: list[str] = []
    stages_used: list[str] = []
    result_text = text
    llm_used = False
    chunks_processed = 0
    llm_calls = 0
    fallback_used = False

    for stage in stages:
        if stage == "llm":
            if not llm_config or not llm_config.enabled:
                continue

            try:
                result_text, chunks_processed, llm_calls = await _stage_llm(result_text, llm_config)
                llm_used = True
                stages_used.append(stage)
            except (LLMError, LLMValidationError) as exc:
                errors.append(str(exc))
                log = get_logger(__name__)
                log.warning("LLM stage failed: %s", exc)
                fallback_used = True
        else:
            stage_handlers: dict[str, Callable[[str], str]] = {
                "basic": _stage_basic,
                "abbreviations": _stage_abbreviations,
                "symbols": _stage_symbols,
                "numbers": _stage_numbers,
                "latin_letters": _stage_latin_letters,
                "paragraph_pauses": _stage_paragraph_pauses,
            }

            if stage in stage_handlers:
                result_text = stage_handlers[stage](result_text)
                stages_used.append(stage)

    return PreprocessResult(
        text=result_text,
        llm_used=llm_used,
        chunks_processed=chunks_processed,
        llm_calls=llm_calls,
        fallback_used=fallback_used,
        errors=errors,
        stages_used=stages_used,
    )


async def preprocess_text(text: str, llm_config: Optional[LLMConfig] = None) -> str:
    if not text:
        return text

    if llm_config and llm_config.enabled:
        try:
            result = await _preprocess_text_async(text, llm_config)
            return result.text
        except Exception:
            pass

    stages = _parse_pipeline_stages()
    if "llm" in stages:
        stages = [s for s in stages if s != "llm"]

    result = await _preprocess_text_async(text, llm_config, stages)
    return result.text


async def preprocess_text_with_result(text: str, llm_config: Optional[LLMConfig] = None) -> PreprocessResult:
    if not text:
        return PreprocessResult(
            text="",
            llm_used=False,
            chunks_processed=0,
            llm_calls=0,
            fallback_used=False,
            errors=[],
            stages_used=[],
        )

    return await _preprocess_text_async(text, llm_config)
