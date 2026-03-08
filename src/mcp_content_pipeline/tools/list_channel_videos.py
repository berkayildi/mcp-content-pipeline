"""MCP tool: list recent videos from a YouTube channel."""

from __future__ import annotations

from mcp_content_pipeline.config import Settings
from mcp_content_pipeline.models.schemas import ChannelVideosResult
from mcp_content_pipeline.services.youtube_api import (
    list_channel_videos as _list_channel_videos,
)


async def list_channel_videos(
    channel_id: str,
    settings: Settings,
    max_results: int = 10,
    published_after: str | None = None,
) -> ChannelVideosResult:
    """Fetch recent videos from a YouTube channel."""
    if not settings.youtube_api_key:
        raise ValueError(
            "YouTube API key not configured. "
            "Set MCP_CP_YOUTUBE_API_KEY environment variable to use this tool."
        )

    return await _list_channel_videos(
        api_key=settings.youtube_api_key,
        channel_id=channel_id,
        max_results=max_results,
        published_after=published_after,
    )
