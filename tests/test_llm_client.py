"""Tests for the provider-agnostic LLM driver."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_content_pipeline.services.llm_client import complete


class TestCompleteAnthropic:
    @pytest.mark.asyncio
    async def test_anthropic_provider(self):
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="anthropic reply")]
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)

        with patch("anthropic.AsyncAnthropic", return_value=mock_client):
            result = await complete(
                provider="anthropic",
                api_key="key",
                model="claude-sonnet-4-6",
                system_prompt="sys",
                user_prompt="user",
            )
            assert result == "anthropic reply"
            mock_client.messages.create.assert_called_once()
            assert mock_client.messages.create.call_args.kwargs["system"] == "sys"


class TestCompleteOpenAI:
    @pytest.mark.asyncio
    async def test_openai_provider(self):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="openai reply"))]
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        with patch("openai.AsyncOpenAI", return_value=mock_client):
            result = await complete(
                provider="openai",
                api_key="key",
                model="gpt-4o",
                system_prompt="sys",
                user_prompt="user",
            )
            assert result == "openai reply"
            call_kwargs = mock_client.chat.completions.create.call_args.kwargs
            assert call_kwargs["messages"][0] == {"role": "system", "content": "sys"}
            assert call_kwargs["messages"][1] == {"role": "user", "content": "user"}


class TestCompleteUnsupportedProvider:
    @pytest.mark.asyncio
    async def test_unsupported_provider_raises(self):
        with pytest.raises(ValueError, match="Unsupported MCP_CP_PIPELINE_PROVIDER"):
            await complete(
                provider="mistral",
                api_key="key",
                model="model",
                system_prompt="sys",
                user_prompt="user",
            )

    @pytest.mark.asyncio
    async def test_provider_is_case_insensitive(self):
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="reply")]
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)

        with patch("anthropic.AsyncAnthropic", return_value=mock_client):
            result = await complete(
                provider="Anthropic",
                api_key="key",
                model="claude-sonnet-4-6",
                system_prompt="sys",
                user_prompt="user",
            )
            assert result == "reply"
