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
    if not settings.supadata_api_key:
        raise ValueError("MCP_CP_SUPADATA_API_KEY is required for YouTube video analysis")

    video_id = parse_video_id(url)
    transcript_text, transcript_lang = await fetch_transcript(
        url, settings.max_transcript_tokens, settings.supadata_api_key
    )
    metadata = await fetch_video_metadata(video_id)

    analysis = await analyse_transcript(
        api_key=settings.anthropic_api_key,
        model=settings.claude_model,
        transcript=transcript_text,
        metadata=metadata,
        custom_prompt=custom_prompt,
        transcript_lang=transcript_lang,
    )

    return analysis
