"""MCP tool: analyse a single YouTube video."""

from __future__ import annotations

from mcp_content_pipeline.config import Settings
from mcp_content_pipeline.models.schemas import VideoAnalysis
from mcp_content_pipeline.services.claude_client import analyse_transcript
from mcp_content_pipeline.services.transcript import (
    fetch_transcript,
    fetch_video_metadata,
    parse_video_id,
)


async def analyse_video(
    url: str,
    settings: Settings,
    custom_prompt: str | None = None,
) -> VideoAnalysis:
    """Analyse a single YouTube video."""
    video_id = parse_video_id(url)
    transcript = await fetch_transcript(video_id, settings.max_transcript_tokens)
    metadata = await fetch_video_metadata(video_id)

    analysis = await analyse_transcript(
        api_key=settings.anthropic_api_key,
        model=settings.claude_model,
        transcript=transcript,
        metadata=metadata,
        custom_prompt=custom_prompt,
    )

    return analysis
