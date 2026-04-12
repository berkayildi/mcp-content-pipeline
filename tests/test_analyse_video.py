"""Tests for the analyse_video tool."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from mcp_content_pipeline.models.schemas import VideoAnalysis
from mcp_content_pipeline.services.transcript import parse_video_id
from mcp_content_pipeline.tools.analyse_video import analyse_video


class TestParseVideoId:
    def test_standard_url(self):
        assert parse_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_short_url(self):
        assert parse_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_shorts_url(self):
        assert parse_video_id("https://youtube.com/shorts/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_embed_url(self):
        assert parse_video_id("https://youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_url_with_extra_params(self):
        assert parse_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120") == "dQw4w9WgXcQ"

    def test_url_with_playlist(self):
        assert parse_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLxyz") == "dQw4w9WgXcQ"

    def test_invalid_url_raises(self):
        with pytest.raises(ValueError, match="Could not parse video ID"):
            parse_video_id("https://example.com/not-youtube")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            parse_video_id("")

    def test_url_with_www(self):
        assert parse_video_id("https://www.youtube.com/watch?v=abc123def45") == "abc123def45"

    def test_url_without_www(self):
        assert parse_video_id("https://youtube.com/watch?v=abc123def45") == "abc123def45"


class TestAnalyseVideo:
    @pytest.mark.asyncio
    async def test_analyse_video_success(self, settings, sample_transcript, sample_video_metadata, sample_analysis_result):
        settings.supadata_api_key = "test-supadata-key"
        with (
            patch(
                "mcp_content_pipeline.tools.analyse_video.fetch_transcript",
                new_callable=AsyncMock,
                return_value=(sample_transcript, "en", None),
            ),
            patch(
                "mcp_content_pipeline.tools.analyse_video.fetch_video_metadata",
                new_callable=AsyncMock,
                return_value=sample_video_metadata,
            ),
            patch(
                "mcp_content_pipeline.tools.analyse_video.analyse_transcript",
                new_callable=AsyncMock,
                return_value=sample_analysis_result,
            ),
        ):
            result = await analyse_video(
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                settings=settings,
            )
            assert isinstance(result, VideoAnalysis)
            assert result.title == "ML in Production: 3 Strategies That Actually Work"
            assert len(result.key_takeaways) == 5

    @pytest.mark.asyncio
    async def test_analyse_video_with_custom_prompt(self, settings, sample_transcript, sample_video_metadata, sample_analysis_result):
        settings.supadata_api_key = "test-supadata-key"
        with (
            patch(
                "mcp_content_pipeline.tools.analyse_video.fetch_transcript",
                new_callable=AsyncMock,
                return_value=(sample_transcript, "en", None),
            ),
            patch(
                "mcp_content_pipeline.tools.analyse_video.fetch_video_metadata",
                new_callable=AsyncMock,
                return_value=sample_video_metadata,
            ),
            patch(
                "mcp_content_pipeline.tools.analyse_video.analyse_transcript",
                new_callable=AsyncMock,
                return_value=sample_analysis_result,
            ) as mock_analyse,
        ):
            await analyse_video(
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                settings=settings,
                custom_prompt="Focus on DevOps aspects",
            )
            mock_analyse.assert_called_once()
            assert mock_analyse.call_args.kwargs["custom_prompt"] == "Focus on DevOps aspects"

    @pytest.mark.asyncio
    async def test_analyse_video_passes_transcript_lang(self, settings, sample_transcript, sample_video_metadata, sample_analysis_result):
        settings.supadata_api_key = "test-supadata-key"
        with (
            patch(
                "mcp_content_pipeline.tools.analyse_video.fetch_transcript",
                new_callable=AsyncMock,
                return_value=(sample_transcript, "tr", None),
            ),
            patch(
                "mcp_content_pipeline.tools.analyse_video.fetch_video_metadata",
                new_callable=AsyncMock,
                return_value=sample_video_metadata,
            ),
            patch(
                "mcp_content_pipeline.tools.analyse_video.analyse_transcript",
                new_callable=AsyncMock,
                return_value=sample_analysis_result,
            ) as mock_analyse,
        ):
            await analyse_video(
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                settings=settings,
            )
            mock_analyse.assert_called_once()
            assert mock_analyse.call_args.kwargs["transcript_lang"] == "tr"

    @pytest.mark.asyncio
    async def test_analyse_video_invalid_url(self, settings):
        settings.supadata_api_key = "test-supadata-key"
        with pytest.raises(ValueError, match="Could not parse video ID"):
            await analyse_video(url="https://not-youtube.com/video", settings=settings)

    @pytest.mark.asyncio
    async def test_analyse_video_transcript_failure(self, settings):
        settings.supadata_api_key = "test-supadata-key"
        with patch(
            "mcp_content_pipeline.tools.analyse_video.parse_video_id",
            return_value="abc123def45",
        ), patch(
            "mcp_content_pipeline.tools.analyse_video.fetch_transcript",
            new_callable=AsyncMock,
            side_effect=Exception("No transcript available"),
        ):
            with pytest.raises(Exception, match="No transcript available"):
                await analyse_video(url="https://www.youtube.com/watch?v=abc123def45", settings=settings)

    @pytest.mark.asyncio
    async def test_analyse_video_missing_supadata_key(self, settings):
        settings.supadata_api_key = ""
        with pytest.raises(ValueError, match="MCP_CP_SUPADATA_API_KEY is required"):
            await analyse_video(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", settings=settings)
