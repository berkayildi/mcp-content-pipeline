"""MCP server entry point — registers all tools."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_content_pipeline.config import get_settings
from mcp_content_pipeline.models.schemas import VideoAnalysis
from mcp_content_pipeline.tools.analyse_video import analyse_video as _analyse_video
from mcp_content_pipeline.tools.batch_analyse import batch_analyse as _batch_analyse
from mcp_content_pipeline.tools.generate_image import generate_image as _generate_image
from mcp_content_pipeline.tools.list_channel_videos import (
    list_channel_videos as _list_channel_videos,
)
from mcp_content_pipeline.tools.sync_to_github import sync_to_github as _sync_to_github

mcp = FastMCP("mcp-content-pipeline")


@mcp.tool()
async def analyse_video(url: str, custom_prompt: str | None = None) -> str:
    """Analyse a single YouTube video — extracts transcript, generates key takeaways, TLDR, and Twitter/X hook draft.

    Args:
        url: YouTube video URL (supports youtube.com/watch?v=, youtu.be/, youtube.com/shorts/)
        custom_prompt: Additional analysis instructions (optional)
    """
    settings = get_settings()
    result = await _analyse_video(url=url, settings=settings, custom_prompt=custom_prompt)
    return result.model_dump_json(indent=2)


@mcp.tool()
async def batch_analyse(urls: list[str] | None = None, config_file: str | None = None) -> str:
    """Analyse multiple YouTube videos from a list of URLs or a config file path.

    Args:
        urls: List of YouTube URLs to analyse
        config_file: Path to a YAML/JSON file containing a list of URLs
    """
    settings = get_settings()
    result = await _batch_analyse(settings=settings, urls=urls, config_file=config_file)
    return result.model_dump_json(indent=2)


@mcp.tool()
async def list_channel_videos(
    channel_id: str,
    max_results: int = 10,
    published_after: str | None = None,
) -> str:
    """Fetch recent videos from a YouTube channel (requires YouTube Data API key).

    Args:
        channel_id: YouTube channel ID
        max_results: Number of recent videos to fetch (default: 10, max: 50)
        published_after: ISO date to filter videos published after this date
    """
    settings = get_settings()
    result = await _list_channel_videos(
        channel_id=channel_id,
        settings=settings,
        max_results=max_results,
        published_after=published_after,
    )
    return result.model_dump_json(indent=2)


@mcp.tool()
async def generate_image(analysis: dict) -> str:
    """Generate a comic-book style infographic image from a video analysis result.

    Takes the output of analyse_video or batch_analyse and generates a
    composite illustration summarising the key stories. Returns base64-encoded
    PNG image data and the prompt used.

    Args:
        analysis: Analysis result object from analyse_video or batch_analyse
    """
    settings = get_settings()
    result = await _generate_image(analysis_data=analysis, settings=settings)
    return result.model_dump_json(indent=2)


@mcp.tool()
async def sync_to_github(
    analyses: list[dict],
    commit_message: str = "Add video analyses",
    images: list[dict] | None = None,
) -> str:
    """Push analysed content as markdown files to a GitHub repository.

    Args:
        analyses: List of analysis result objects from analyse_video or batch_analyse
        commit_message: Git commit message (default: 'Add video analyses')
        images: Optional list of image objects with 'analysis' (dict) and 'image_base64' (str) fields
    """
    settings = get_settings()
    parsed = [VideoAnalysis.model_validate(a) for a in analyses]

    parsed_images = None
    if images:
        import base64

        parsed_images = []
        for img in images:
            analysis_obj = VideoAnalysis.model_validate(img["analysis"])
            image_bytes = base64.b64decode(img["image_base64"])
            parsed_images.append((analysis_obj, image_bytes))

    result = await _sync_to_github(
        analyses=parsed,
        settings=settings,
        commit_message=commit_message,
        images=parsed_images,
    )
    return result.model_dump_json(indent=2)


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
