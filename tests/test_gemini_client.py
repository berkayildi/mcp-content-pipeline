"""Tests for the Gemini client."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_content_pipeline.models.schemas import VideoAnalysis
from mcp_content_pipeline.services.gemini_client import build_image_prompt, generate_image


@pytest.fixture
def analysis():
    return VideoAnalysis(
        title="AI News Roundup: March 2026",
        channel="Tech Channel",
        url="https://www.youtube.com/watch?v=test123",
        date_analysed="2026-03-08T12:00:00",
        key_takeaways=["Takeaway 1", "Takeaway 2", "Takeaway 3"],
        tldr="A summary of AI news.",
        twitter_hook="AI is changing everything #AI",
        topics=["AI", "Machine Learning"],
    )


class TestBuildImagePrompt:
    def test_prompt_contains_title(self, analysis):
        prompt = build_image_prompt(analysis)
        assert "AI News Roundup: March 2026" in prompt

    def test_prompt_contains_takeaways(self, analysis):
        prompt = build_image_prompt(analysis)
        assert "Takeaway 1" in prompt
        assert "Takeaway 2" in prompt
        assert "Takeaway 3" in prompt

    def test_prompt_contains_topics(self, analysis):
        prompt = build_image_prompt(analysis)
        assert "AI, Machine Learning" in prompt

    def test_prompt_truncates_to_six_stories(self):
        analysis = VideoAnalysis(
            title="Many Stories",
            channel="C",
            url="https://youtube.com/watch?v=abc",
            date_analysed="2026-03-08T12:00:00",
            key_takeaways=[f"Takeaway {i}" for i in range(10)],
            tldr="s",
            twitter_hook="h",
            topics=["t"],
        )
        prompt = build_image_prompt(analysis)
        assert "Takeaway 5" in prompt
        assert "Takeaway 6" not in prompt

    def test_prompt_handles_empty_takeaways(self):
        analysis = VideoAnalysis(
            title="Empty",
            channel="C",
            url="https://youtube.com/watch?v=abc",
            date_analysed="2026-03-08T12:00:00",
            key_takeaways=[],
            tldr="s",
            twitter_hook="h",
            topics=["t"],
        )
        prompt = build_image_prompt(analysis)
        assert "Empty" in prompt


class TestGenerateImage:
    @pytest.mark.asyncio
    async def test_generate_image_success(self, analysis):
        fake_image_bytes = b"\x89PNG\r\n\x1a\nfake_image_data"

        mock_part = MagicMock()
        mock_part.inline_data = MagicMock()
        mock_part.inline_data.data = fake_image_bytes

        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].content.parts = [mock_part]

        mock_aio_models = MagicMock()
        mock_aio_models.generate_content = AsyncMock(return_value=mock_response)

        mock_aio = MagicMock()
        mock_aio.models = mock_aio_models

        mock_client = MagicMock()
        mock_client.aio = mock_aio

        with patch("mcp_content_pipeline.services.gemini_client.genai") as mock_genai:
            mock_genai.Client.return_value = mock_client
            result = await generate_image("fake-key", "gemini-2.5-flash-image", analysis)

        assert result.analysis_title == "AI News Roundup: March 2026"
        assert result.image_path.endswith(".png")
        assert os.path.exists(result.image_path)
        assert result.prompt_used != ""

        with open(result.image_path, "rb") as f:
            saved_bytes = f.read()
        assert saved_bytes == fake_image_bytes

        os.unlink(result.image_path)

    @pytest.mark.asyncio
    async def test_generate_image_no_image_in_response(self, analysis):
        mock_part = MagicMock()
        mock_part.inline_data = None

        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].content.parts = [mock_part]

        mock_aio_models = MagicMock()
        mock_aio_models.generate_content = AsyncMock(return_value=mock_response)

        mock_aio = MagicMock()
        mock_aio.models = mock_aio_models

        mock_client = MagicMock()
        mock_client.aio = mock_aio

        with patch("mcp_content_pipeline.services.gemini_client.genai") as mock_genai:
            mock_genai.Client.return_value = mock_client
            with pytest.raises(RuntimeError, match="no image data"):
                await generate_image("fake-key", "gemini-2.5-flash-image", analysis)

    @pytest.mark.asyncio
    async def test_generate_image_api_error(self, analysis):
        mock_aio_models = MagicMock()
        mock_aio_models.generate_content = AsyncMock(side_effect=Exception("API quota exceeded"))

        mock_aio = MagicMock()
        mock_aio.models = mock_aio_models

        mock_client = MagicMock()
        mock_client.aio = mock_aio

        with patch("mcp_content_pipeline.services.gemini_client.genai") as mock_genai:
            mock_genai.Client.return_value = mock_client
            with pytest.raises(Exception, match="API quota exceeded"):
                await generate_image("fake-key", "gemini-2.5-flash-image", analysis)
