"""MCP tool: generate comic-book infographic from video analysis."""

from __future__ import annotations

from mcp_content_pipeline.config import Settings
from mcp_content_pipeline.models.schemas import ImageGenerationResult, VideoAnalysis
from mcp_content_pipeline.services.gemini_client import generate_image as _generate_image


async def generate_image(
    analysis_data: dict,
    settings: Settings,
) -> ImageGenerationResult:
    """Generate a comic-book infographic from a video analysis."""
    if not settings.gemini_api_key:
        raise ValueError(
            "Gemini API key not configured. "
            "Set MCP_CP_GEMINI_API_KEY environment variable to use this tool."
        )

    analysis = VideoAnalysis.model_validate(analysis_data)

    return await _generate_image(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
        analysis=analysis,
    )
