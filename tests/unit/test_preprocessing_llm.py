import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.preprocessing.llm import LLMClient, LLMError, LLMValidationError, LLMTimeoutError
from src.preprocessing.validation import validate_response
from src.utils.config import LLMConfig
from pathlib import Path


@pytest.fixture
def llm_config():
    return LLMConfig(
        api_url="https://api.openai.com/v1",
        api_key="test-key",
        model="gpt-4o-mini",
        temperature=0.3,
        top_p=1.0,
        timeout=30,
        max_retries=2,
        system_prompt_path=None,
        cache_system_prompt=False,
        min_chunk_size=500,
        max_tokens=4000,
        enabled=True,
    )


def test_validate_response():
    assert validate_response("Привет мир.")
    assert validate_response("Текст с ударением: зам+ок")
    assert not validate_response("Text with English")
    assert not validate_response("Текст с <invalid> символами")


@pytest.mark.asyncio
async def test_llm_client_transliterate_success(llm_config):
    with patch("src.preprocessing.llm.AsyncOpenAI") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Привет эй пи ай"
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        client = LLMClient(llm_config)
        result = await client.transliterate("Hello API")
        
        assert result == "Привет эй пи ай"
        mock_client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_llm_client_validation_error(llm_config):
    with patch("src.preprocessing.llm.AsyncOpenAI") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Invalid response with English"
        
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        client = LLMClient(llm_config)
        
        with pytest.raises(LLMValidationError):
            await client.transliterate("test")

