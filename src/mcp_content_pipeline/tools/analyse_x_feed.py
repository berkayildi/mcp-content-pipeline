"""MCP tool: analyse recent posts from curated X accounts."""

from __future__ import annotations

from mcp_content_pipeline.config import Settings
from mcp_content_pipeline.models.schemas import VideoAnalysis, XDigestAnalysis
from mcp_content_pipeline.services.x_client import fetch_x_feed
from mcp_content_pipeline.services.x_digest_client import analyse_x_feed as _analyse_digest


def x_digest_to_video_analysis(digest: XDigestAnalysis) -> VideoAnalysis:
    """Convert an X digest to VideoAnalysis format for image generation compatibility."""
    return VideoAnalysis(
        title=digest.title,
        channel="X Feed Digest",
        url="",
        date_analysed=digest.date_analysed,
        key_takeaways=digest.key_takeaways,
        tldr=digest.tldr,
        twitter_hook=digest.twitter_hook,
        topics=digest.topics,
    )


async def analyse_x_feed(
    settings: Settings,
    usernames: list[str] | None = None,
    topics: list[str] | None = None,
    hours_back: int = 24,
) -> XDigestAnalysis:
    """Analyse recent posts from curated X accounts."""
    accounts = usernames or settings.x_accounts
    feed_topics = topics or settings.x_topics or ["AI", "tech"]

    if not settings.x_bearer_token:
        raise ValueError("X bearer token not configured — set MCP_CP_X_BEARER_TOKEN")

    if not accounts:
        raise ValueError("No X accounts specified — pass usernames or set MCP_CP_X_ACCOUNTS")

    feed_result = await fetch_x_feed(
        bearer_token=settings.x_bearer_token,
        usernames=accounts,
        hours_back=hours_back,
    )

    if not feed_result.posts:
        if feed_result.failures:
            failed = ", ".join(f"@{f.username}: {f.error}" for f in feed_result.failures)
            raise RuntimeError(f"No posts fetched — all accounts failed: {failed}")
        raise RuntimeError(f"No posts found in the last {hours_back} hours")

    analysis = await _analyse_digest(
        api_key=settings.anthropic_api_key,
        model=settings.claude_model,
        feed_result=feed_result,
        topics=feed_topics,
    )

    return analysis
