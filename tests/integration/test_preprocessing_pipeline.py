import os
import pytest

from src.preprocessing import preprocess_text, preprocess_text_with_result
from src.preprocessing.pipeline import _parse_pipeline_stages


def test_preprocess_without_llm():
    result = preprocess_text("API стоит $100")
    assert "API" not in result or "эй пи ай" in result.lower()


def test_preprocess_text_with_result():
    result = preprocess_text_with_result("тест")
    assert result.text == "Тест."
    assert not result.llm_used
    assert not result.fallback_used
    assert "basic" in result.stages_used


def test_parse_pipeline_stages_default():
    stages = _parse_pipeline_stages(None)
    assert stages == ["basic", "abbreviations", "symbols", "numbers", "latin_letters"]


def test_parse_pipeline_stages_from_env():
    os.environ["PREPROCESSING_STAGES"] = "basic,abbreviations,symbols"
    try:
        stages = _parse_pipeline_stages()
        assert stages == ["basic", "abbreviations", "symbols"]
    finally:
        del os.environ["PREPROCESSING_STAGES"]


def test_parse_pipeline_stages_with_llm():
    os.environ["PREPROCESSING_STAGES"] = "basic,abbreviations,llm"
    try:
        stages = _parse_pipeline_stages()
        assert "basic" in stages
        assert "abbreviations" in stages
        assert "llm" in stages
    finally:
        del os.environ["PREPROCESSING_STAGES"]


def test_parse_pipeline_stages_invalid():
    os.environ["PREPROCESSING_STAGES"] = "basic,invalid_stage,symbols"
    try:
        stages = _parse_pipeline_stages()
        assert "basic" in stages
        assert "invalid_stage" not in stages
        assert "symbols" in stages
    finally:
        del os.environ["PREPROCESSING_STAGES"]


def test_parse_pipeline_stages_empty():
    os.environ["PREPROCESSING_STAGES"] = ""
    try:
        stages = _parse_pipeline_stages()
        assert stages == ["basic", "abbreviations", "symbols", "numbers", "latin_letters"]
    finally:
        del os.environ["PREPROCESSING_STAGES"]


def test_preprocess_stages_order():
    result = preprocess_text_with_result("API $100")
    assert "basic" in result.stages_used
    assert "abbreviations" in result.stages_used
    assert "symbols" in result.stages_used
    stages_index = {stage: result.stages_used.index(stage) for stage in result.stages_used}
    assert stages_index["basic"] < stages_index["abbreviations"]
    assert stages_index["abbreviations"] < stages_index["symbols"]
