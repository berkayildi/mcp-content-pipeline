"""Tests for the analyse_x_feed tool."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from mcp_content_pipeline.config import Settings
from mcp_content_pipeline.models.schemas import (
    VideoAnalysis,
    XDigestAnalysis,
    XFeedFailure,
    XFeedFetchResult,
    XNotablePost,
    XPost,
)
from mcp_content_pipeline.tools.analyse_x_feed import analyse_x_feed, x_digest_to_video_analysis


@pytest.fixture
def x_settings():
    return Settings(
        anthropic_api_key="test-api-key",
        x_bearer_token="test-bearer-token",
        x_accounts=["karpathy", "bcherny"],
        x_topics=["AI", "tech"],
    )


@pytest.fixture
def sample_feed_result():
    return XFeedFetchResult(
        accounts=["karpathy", "bcherny"],
        posts=[
            XPost(
                id="1",
                text="AI agents are the next big thing",
                author_username="karpathy",
                author_name="Andrej Karpathy",
                created_at="2026-04-10T10:00:00Z",
                url="https://x.com/karpathy/status/1",
                like_count=500,
                retweet_count=100,
            ),
        ],
    )


@pytest.fixture
def sample_digest():
    return XDigestAnalysis(
        title="AI Agents — X Feed Digest",
        accounts=["karpathy", "bcherny"],
        topics=["AI", "tech"],
        key_takeaways=["AI agents are becoming mainstream", "Infrastructure investment accelerating"],
        tldr="Key AI voices highlight agents as the next frontier.",
        twitter_hook="AI agents aren't just hype — they're replacing workflows #AI #Agents",
        notable_posts=[
            XNotablePost(
                author_username="karpathy",
                text="AI agents are the next big thing",
                url="https://x.com/karpathy/status/1",
                why_notable="Signals shift from models to applications",
            ),
        ],
        post_count=1,
    )


class TestAnalyseXFeed:
    @pytest.mark.asyncio
    async def test_missing_bearer_token_raises(self):
        settings = Settings(anthropic_api_key="test-key", x_bearer_token="", x_accounts=["testuser"])
        with pytest.raises(ValueError, match="X bearer token not configured"):
            await analyse_x_feed(settings=settings, usernames=["testuser"])

    @pytest.mark.asyncio
    async def test_empty_accounts_raises(self):
        settings = Settings(anthropic_api_key="test-key", x_bearer_token="test-token", x_accounts=[])
        with pytest.raises(ValueError, match="No X accounts specified"):
            await analyse_x_feed(settings=settings)

    @pytest.mark.asyncio
    async def test_no_posts_with_failures_raises(self, x_settings):
        empty_result = XFeedFetchResult(
            accounts=["baduser"],
            posts=[],
            failures=[XFeedFailure(username="baduser", error="404 Not Found")],
        )
        with patch(
            "mcp_content_pipeline.tools.analyse_x_feed.fetch_x_feed",
            new_callable=AsyncMock,
            return_value=empty_result,
        ):
            with pytest.raises(RuntimeError, match="all accounts failed"):
                await analyse_x_feed(settings=x_settings, usernames=["baduser"])

    @pytest.mark.asyncio
    async def test_no_posts_no_failures_raises(self, x_settings):
        empty_result = XFeedFetchResult(accounts=["testuser"], posts=[])
        with patch(
            "mcp_content_pipeline.tools.analyse_x_feed.fetch_x_feed",
            new_callable=AsyncMock,
            return_value=empty_result,
        ):
            with pytest.raises(RuntimeError, match="No posts found"):
                await analyse_x_feed(settings=x_settings, usernames=["testuser"])

    @pytest.mark.asyncio
    async def test_happy_path(self, x_settings, sample_feed_result, sample_digest):
        with (
            patch(
                "mcp_content_pipeline.tools.analyse_x_feed.fetch_x_feed",
                new_callable=AsyncMock,
                return_value=sample_feed_result,
            ),
            patch(
                "mcp_content_pipeline.tools.analyse_x_feed._analyse_digest",
                new_callable=AsyncMock,
                return_value=sample_digest,
            ),
        ):
            result = await analyse_x_feed(settings=x_settings)
            assert isinstance(result, XDigestAnalysis)
            assert result.title == "AI Agents — X Feed Digest"
            assert len(result.key_takeaways) == 2

    @pytest.mark.asyncio
    async def test_uses_settings_defaults(self, x_settings, sample_feed_result, sample_digest):
        with (
            patch(
                "mcp_content_pipeline.tools.analyse_x_feed.fetch_x_feed",
                new_callable=AsyncMock,
                return_value=sample_feed_result,
            ) as mock_fetch,
            patch(
                "mcp_content_pipeline.tools.analyse_x_feed._analyse_digest",
                new_callable=AsyncMock,
                return_value=sample_digest,
            ) as mock_analyse,
        ):
            await analyse_x_feed(settings=x_settings)
            # Should use settings defaults
            mock_fetch.assert_called_once_with(
                bearer_token="test-bearer-token",
                usernames=["karpathy", "bcherny"],
                hours_back=24,
            )
            mock_analyse.assert_called_once()
            assert mock_analyse.call_args.kwargs["topics"] == ["AI", "tech"]

    @pytest.mark.asyncio
    async def test_overrides_with_args(self, x_settings, sample_feed_result, sample_digest):
        with (
            patch(
                "mcp_content_pipeline.tools.analyse_x_feed.fetch_x_feed",
                new_callable=AsyncMock,
                return_value=sample_feed_result,
            ) as mock_fetch,
            patch(
                "mcp_content_pipeline.tools.analyse_x_feed._analyse_digest",
                new_callable=AsyncMock,
                return_value=sample_digest,
            ) as mock_analyse,
        ):
            await analyse_x_feed(
                settings=x_settings,
                usernames=["atmoio"],
                topics=["startups"],
                hours_back=48,
            )
            mock_fetch.assert_called_once_with(
                bearer_token="test-bearer-token",
                usernames=["atmoio"],
                hours_back=48,
            )
            assert mock_analyse.call_args.kwargs["topics"] == ["startups"]

    @pytest.mark.asyncio
    async def test_default_topics_when_empty(self):
        settings = Settings(
            anthropic_api_key="test-key",
            x_bearer_token="test-token",
            x_accounts=["testuser"],
            x_topics=[],
        )
        feed = XFeedFetchResult(
            accounts=["testuser"],
            posts=[
                XPost(
                    id="1",
                    text="test",
                    author_username="testuser",
                    author_name="Test",
                    created_at="2026-04-10T10:00:00Z",
                    url="https://x.com/testuser/status/1",
                ),
            ],
        )
        digest = XDigestAnalysis(
            title="Test",
            accounts=["testuser"],
            topics=["AI", "tech"],
            key_takeaways=["t1"],
            tldr="s",
            twitter_hook="h",
        )
        with (
            patch(
                "mcp_content_pipeline.tools.analyse_x_feed.fetch_x_feed",
                new_callable=AsyncMock,
                return_value=feed,
            ),
            patch(
                "mcp_content_pipeline.tools.analyse_x_feed._analyse_digest",
                new_callable=AsyncMock,
                return_value=digest,
            ) as mock_analyse,
        ):
            await analyse_x_feed(settings=settings)
            assert mock_analyse.call_args.kwargs["topics"] == ["AI", "tech"]


class TestXDigestToVideoAnalysis:
    def test_conversion(self, sample_digest):
        result = x_digest_to_video_analysis(sample_digest)
        assert isinstance(result, VideoAnalysis)
        assert result.title == sample_digest.title
        assert result.channel == "X Feed Digest"
        assert result.url == ""
        assert result.key_takeaways == sample_digest.key_takeaways
        assert result.tldr == sample_digest.tldr
        assert result.twitter_hook == sample_digest.twitter_hook
        assert result.topics == sample_digest.topics
        assert result.date_analysed == sample_digest.date_analysed
