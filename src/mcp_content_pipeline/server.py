"""MCP server entry point — registers all tools."""

from __future__ import annotations

import os

from dotenv import find_dotenv, load_dotenv
from mcp.server.fastmcp import FastMCP

from mcp_content_pipeline.config import get_settings
from mcp_content_pipeline.models.schemas import VideoAnalysis, XDigestAnalysis
from mcp_content_pipeline.tools.analyse_video import analyse_video as _analyse_video
from mcp_content_pipeline.tools.analyse_x_feed import analyse_x_feed as _analyse_x_feed
from mcp_content_pipeline.tools.sync_to_github import sync_to_github as _sync_to_github

mcp = FastMCP("mcp-content-pipeline")


@mcp.tool()
async def analyse_video(url: str, custom_prompt: str | None = None) -> str:
    """Analyse a single YouTube video — extracts the English transcript, generates a TL;DR and key points.

    Use this tool when the user provides a YouTube URL or asks to analyse a
    YouTube video. Supports youtube.com/watch, youtu.be, youtube.com/shorts,
    and youtube.com/live URLs. The video must have English captions.

    Args:
        url: YouTube video URL
        custom_prompt: Additional analysis instructions (optional)
    """
    settings = get_settings()
    result = await _analyse_video(url=url, settings=settings, custom_prompt=custom_prompt)
    return result.model_dump_json(indent=2)


@mcp.tool()
async def analyse_x_feed(
    usernames: list[str] | None = None,
    topics: list[str] | None = None,
    hours_back: int = 24,
) -> str:
    """Analyse recent X (Twitter) posts and tweets from specified accounts or configured defaults.

    Fetches posts from X/Twitter user timelines, filters by topic, and generates
    a digest with a TL;DR and key points. Use this
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
    x_digests: list[dict] | None = None,
) -> str:
    """Push analysed content as markdown files to a GitHub repository.

    Syncs video analyses and X feed digests to a configured GitHub repo.
    Use after analyse_video or analyse_x_feed to persist results.

    Args:
        analyses: List of analysis result objects from analyse_video
        commit_message: Git commit message (default: 'Add video analyses')
        x_digests: Optional list of X digest analysis objects from analyse_x_feed
    """
    settings = get_settings()
    parsed = [VideoAnalysis.model_validate(a) for a in analyses]

    parsed_digests = None
    if x_digests:
        parsed_digests = [XDigestAnalysis.model_validate(d) for d in x_digests]

    result = await _sync_to_github(
        analyses=parsed,
        settings=settings,
        commit_message=commit_message,
        x_digests=parsed_digests,
    )
    return result.model_dump_json(indent=2)


def main():
    """Run the MCP server."""
    # MCP_CP_ENV_FILE, else nearest .env from cwd
    load_dotenv(os.environ.get("MCP_CP_ENV_FILE") or find_dotenv(usecwd=True))
    mcp.run()


if __name__ == "__main__":
    main()
