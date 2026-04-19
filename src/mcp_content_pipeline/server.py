"""MCP server entry point — registers all tools."""

from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from mcp_content_pipeline.config import get_settings
from mcp_content_pipeline.models.schemas import VideoAnalysis, XDigestAnalysis
from mcp_content_pipeline.tools.analyse_video import analyse_video as _analyse_video
from mcp_content_pipeline.tools.analyse_x_feed import analyse_x_feed as _analyse_x_feed
from mcp_content_pipeline.tools.batch_analyse import batch_analyse as _batch_analyse
from mcp_content_pipeline.tools.generate_image import generate_image as _generate_image
from mcp_content_pipeline.tools.list_channel_videos import (
    list_channel_videos as _list_channel_videos,
)
from mcp_content_pipeline.tools.sync_to_github import sync_to_github as _sync_to_github

mcp = FastMCP("mcp-content-pipeline")


@mcp.tool()
async def analyse_video(url: str, custom_prompt: str | None = None) -> str:
    """Analyse a single YouTube video — extracts transcript, generates key takeaways, TLDR, and social hook.

    Use this tool when the user provides a YouTube URL or asks to analyse a
    YouTube video. Supports youtube.com/watch, youtu.be, youtube.com/shorts,
    and youtube.com/live URLs. Works with videos in any language.

    Args:
        url: YouTube video URL
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
    """Generate a comic-book style infographic image from a video analysis or X digest result.

    Creates a visual summary with bold colours, panel divisions, and text labels.
    Use after analyse_video or analyse_x_feed to create a shareable infographic.

    Args:
        analysis: Analysis result object from analyse_video, batch_analyse, or converted X digest
    """
    settings = get_settings()
    result = await _generate_image(analysis_data=analysis, settings=settings)
    return result.model_dump_json(indent=2)


@mcp.tool()
async def analyse_x_feed(
    usernames: list[str] | None = None,
    topics: list[str] | None = None,
    hours_back: int = 24,
) -> str:
    """Analyse recent X (Twitter) posts and tweets from specified accounts or configured defaults.

    Fetches posts from X/Twitter user timelines, filters by topic, and generates
    a digest with key takeaways, TLDR, social hook, and notable posts. Use this
    tool when the user asks about X posts, tweets, Twitter feed, what someone
    posted on X, or wants a digest of X/Twitter activity.

    Args:
        usernames: X/Twitter usernames to analyse (defaults to configured MCP_CP_X_ACCOUNTS)
        topics: Topics to focus on (defaults to configured MCP_CP_X_TOPICS)
        hours_back: How far back to fetch posts (default: 24, use 168 for weekly)
    """
    settings = get_settings()
    result = await _analyse_x_feed(
        settings=settings,
        usernames=usernames,
        topics=topics,
        hours_back=hours_back,
    )
    return result.model_dump_json(indent=2)


@mcp.tool()
async def sync_to_github(
    analyses: list[dict],
    commit_message: str = "Add video analyses",
    image_paths: list[dict] | None = None,
    x_digests: list[dict] | None = None,
) -> str:
    """Push analysed content as markdown files to a GitHub repository.

    Syncs video analyses, X feed digests, and images to a configured GitHub repo.
    Use after analyse_video, analyse_x_feed, or generate_image to persist results.

    Args:
        analyses: List of analysis result objects from analyse_video or batch_analyse
        commit_message: Git commit message (default: 'Add video analyses')
        image_paths: Optional list of objects with 'analysis' (dict) and 'image_path' (str) fields
        x_digests: Optional list of X digest analysis objects from analyse_x_feed
    """
    settings = get_settings()
    parsed = [VideoAnalysis.model_validate(a) for a in analyses]

    parsed_images = None
    if image_paths:
        allowed_base = Path(settings.image_output_dir or "~/Downloads").expanduser().resolve()
        parsed_images = []
        for img in image_paths:
            analysis_obj = VideoAnalysis.model_validate(img["analysis"])
            p = Path(img["image_path"]).expanduser().resolve()
            if not p.is_relative_to(allowed_base):
                raise ValueError(f"image_path must be within {allowed_base} (got {p})")
            if p.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
                raise ValueError(f"image_path must be a png/jpg/jpeg/webp file (got {p.suffix})")
            with open(p, "rb") as f:
                image_bytes = f.read()
            parsed_images.append((analysis_obj, image_bytes))

    parsed_digests = None
    if x_digests:
        parsed_digests = [XDigestAnalysis.model_validate(d) for d in x_digests]

    result = await _sync_to_github(
        analyses=parsed,
        settings=settings,
        commit_message=commit_message,
        images=parsed_images,
        x_digests=parsed_digests,
    )
    return result.model_dump_json(indent=2)


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
