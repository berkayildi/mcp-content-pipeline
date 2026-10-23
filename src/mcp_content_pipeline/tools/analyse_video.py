"""MCP tool: analyse a single YouTube video."""

from __future__ import annotations

from mcp_content_pipeline.config import Settings
from mcp_content_pipeline.models.schemas import VideoAnalysis
from mcp_content_pipeline.services.transcript import fetch_transcript, parse_video_id
from mcp_content_pipeline.services.video_digest_client import analyse_transcript


async def analyse_video(
    url: str,
    settings: Settings,
    custom_prompt: str | None = None,
) -> VideoAnalysis:
    """Analyse a single YouTube video."""
    video_id = parse_video_id(url)
    transcript_text, metadata = await fetch_transcript(video_id, settings.max_transcript_tokens)

    return await analyse_transcript(
        api_key=settings.pipeline_api_key,
        model=settings.pipeline_model,
        transcript=transcript_text,
        metadata=metadata,
        custom_prompt=custom_prompt,
        provider=settings.pipeline_provider,
    )
