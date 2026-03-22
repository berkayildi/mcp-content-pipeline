"""Tests for the generate_image tool."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from mcp_content_pipeline.config import Settings
from mcp_content_pipeline.models.schemas import ImageGenerationResult
from mcp_content_pipeline.tools.generate_image import generate_image


@pytest.fixture
def valid_analysis_dict():
    return {
        "title": "Test Video",
        "channel": "Test Channel",
        "url": "https://www.youtube.com/watch?v=abc123",
        "date_analysed": "2026-03-08T12:00:00",
        "key_takeaways": ["Takeaway 1", "Takeaway 2"],
        "tldr": "A short summary.",
        "twitter_hook": "Hook #AI",
        "topics": ["AI"],
    }


class TestGenerateImageTool:
    @pytest.mark.asyncio
    async def test_success(self, valid_analysis_dict):
        settings = Settings(
            anthropic_api_key="test",
            gemini_api_key="test-gemini-key",
        )
        mock_result = ImageGenerationResult(
            image_base64="aW1hZ2VfZGF0YQ==",
            prompt_used="test prompt",
            analysis_title="Test Video",
        )
        with patch(
            "mcp_content_pipeline.tools.generate_image._generate_image",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            result = await generate_image(analysis_data=valid_analysis_dict, settings=settings)

        assert isinstance(result, ImageGenerationResult)
        assert result.analysis_title == "Test Video"

    @pytest.mark.asyncio
    async def test_missing_api_key(self, valid_analysis_dict):
        settings = Settings(
            anthropic_api_key="test",
            gemini_api_key="",
        )
        with pytest.raises(ValueError, match="Gemini API key not configured"):
            await generate_image(analysis_data=valid_analysis_dict, settings=settings)

    @pytest.mark.asyncio
    async def test_invalid_analysis_dict(self):
        settings = Settings(
            anthropic_api_key="test",
            gemini_api_key="test-gemini-key",
        )
        with pytest.raises(Exception):
            await generate_image(analysis_data={"bad": "data"}, settings=settings)
