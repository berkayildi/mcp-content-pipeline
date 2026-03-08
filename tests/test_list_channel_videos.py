"""Tests for the list_channel_videos tool."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from mcp_content_pipeline.config import Settings
from mcp_content_pipeline.models.schemas import ChannelVideo, ChannelVideosResult
from mcp_content_pipeline.tools.list_channel_videos import list_channel_videos


class TestListChannelVideos:
    @pytest.mark.asyncio
    async def test_list_channel_videos_success(self, settings):
        mock_result = ChannelVideosResult(
            channel_id="UC_test",
            videos=[
                ChannelVideo(
                    video_id="abc123",
                    title="Test Video 1",
                    url="https://www.youtube.com/watch?v=abc123",
                    published_at="2026-03-01T00:00:00Z",
                ),
                ChannelVideo(
                    video_id="def456",
                    title="Test Video 2",
                    url="https://www.youtube.com/watch?v=def456",
                    published_at="2026-03-02T00:00:00Z",
                ),
            ],
        )

        with patch(
            "mcp_content_pipeline.tools.list_channel_videos._list_channel_videos",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            result = await list_channel_videos(channel_id="UC_test", settings=settings)
            assert len(result.videos) == 2
            assert result.channel_id == "UC_test"

    @pytest.mark.asyncio
    async def test_list_channel_videos_missing_api_key(self):
        settings = Settings(
            anthropic_api_key="test",
            youtube_api_key=None,
            github_token="test",
            github_repo="owner/repo",
        )
        with pytest.raises(ValueError, match="YouTube API key not configured"):
            await list_channel_videos(channel_id="UC_test", settings=settings)

    @pytest.mark.asyncio
    async def test_list_channel_videos_with_max_results(self, settings):
        mock_result = ChannelVideosResult(channel_id="UC_test", videos=[])

        with patch(
            "mcp_content_pipeline.tools.list_channel_videos._list_channel_videos",
            new_callable=AsyncMock,
            return_value=mock_result,
        ) as mock_fn:
            await list_channel_videos(channel_id="UC_test", settings=settings, max_results=5)
            mock_fn.assert_called_once_with(
                api_key="test-youtube-key",
                channel_id="UC_test",
                max_results=5,
                published_after=None,
            )

    @pytest.mark.asyncio
    async def test_list_channel_videos_with_published_after(self, settings):
        mock_result = ChannelVideosResult(channel_id="UC_test", videos=[])

        with patch(
            "mcp_content_pipeline.tools.list_channel_videos._list_channel_videos",
            new_callable=AsyncMock,
            return_value=mock_result,
        ) as mock_fn:
            await list_channel_videos(
                channel_id="UC_test",
                settings=settings,
                published_after="2026-01-01T00:00:00Z",
            )
            mock_fn.assert_called_once()
            assert mock_fn.call_args.kwargs["published_after"] == "2026-01-01T00:00:00Z"

    @pytest.mark.asyncio
    async def test_list_channel_videos_result_format(self, settings):
        mock_result = ChannelVideosResult(
            channel_id="UC_test",
            videos=[
                ChannelVideo(
                    video_id="vid1",
                    title="Video Title",
                    url="https://www.youtube.com/watch?v=vid1",
                    published_at="2026-03-01T00:00:00Z",
                ),
            ],
        )

        with patch(
            "mcp_content_pipeline.tools.list_channel_videos._list_channel_videos",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            result = await list_channel_videos(channel_id="UC_test", settings=settings)
            video = result.videos[0]
            assert video.video_id == "vid1"
            assert "youtube.com" in video.url
            assert video.published_at == "2026-03-01T00:00:00Z"
