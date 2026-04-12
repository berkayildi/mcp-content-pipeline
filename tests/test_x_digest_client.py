"""Tests for the X digest analysis client service."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_content_pipeline.models.schemas import XDigestAnalysis, XFeedFetchResult, XPost
from mcp_content_pipeline.services.x_digest_client import (
    SYSTEM_PROMPT,
    analyse_x_feed,
    build_user_prompt,
    parse_digest_response,
)


@pytest.fixture
def sample_feed_result():
    return XFeedFetchResult(
        accounts=["karpathy", "bcherny"],
        posts=[
            XPost(
                id="1",
                text="AI agents are the next big thing in productivity",
                author_username="karpathy",
                author_name="Andrej Karpathy",
                created_at="2026-04-10T10:00:00Z",
                url="https://x.com/karpathy/status/1",
                like_count=500,
                retweet_count=100,
            ),
            XPost(
                id="2",
                text="Investing in AI infrastructure pays off long-term",
                author_username="bcherny",
                author_name="Boris Cherny",
                created_at="2026-04-10T09:00:00Z",
                url="https://x.com/bcherny/status/2",
                like_count=200,
                retweet_count=50,
            ),
        ],
    )


@pytest.fixture
def sample_digest_response():
    return {
        "title": "AI Agents & Infrastructure — X Feed Digest",
        "accounts": ["karpathy", "bcherny"],
        "topics": ["AI", "tech"],
        "key_takeaways": [
            "AI agents are becoming the primary productivity tool",
            "Infrastructure investment in AI is accelerating",
            "Both voices agree on AI's transformative potential",
            "Practical applications are moving beyond chatbots",
        ],
        "tldr": "Key AI voices highlight agents and infrastructure as the next frontier. "
        "Both Karpathy and Cherny see practical AI deployment accelerating beyond chatbots.",
        "twitter_hook": "AI agents aren't just hype — they're replacing entire workflows. "
        "Two of tech's sharpest minds agree on what's next #AI #Agents",
        "notable_posts": [
            {
                "author_username": "karpathy",
                "text": "AI agents are the next big thing in productivity",
                "url": "https://x.com/karpathy/status/1",
                "why_notable": "Signals a shift in Karpathy's focus from models to applications",
            },
        ],
        "post_count": 2,
    }


class TestBuildUserPrompt:
    def test_basic_prompt(self, sample_feed_result):
        prompt = build_user_prompt(sample_feed_result, ["AI", "tech"])
        assert "Accounts: karpathy, bcherny" in prompt
        assert "Topics: AI, tech" in prompt
        assert "Total posts: 2" in prompt
        assert "@karpathy" in prompt
        assert "AI agents are the next big thing" in prompt
        assert "URL: https://x.com/karpathy/status/1" in prompt

    def test_prompt_includes_metrics(self, sample_feed_result):
        prompt = build_user_prompt(sample_feed_result, ["AI"])
        assert "likes:500" in prompt
        assert "rt:100" in prompt

    def test_prompt_with_empty_posts(self):
        feed = XFeedFetchResult(accounts=["testuser"], posts=[])
        prompt = build_user_prompt(feed, ["AI"])
        assert "Total posts: 0" in prompt
        assert "Accounts: testuser" in prompt


class TestParseDigestResponse:
    def test_parse_clean_json(self, sample_feed_result, sample_digest_response):
        raw = json.dumps(sample_digest_response)
        result = parse_digest_response(raw, sample_feed_result, ["AI", "tech"])
        assert isinstance(result, XDigestAnalysis)
        assert result.title == "AI Agents & Infrastructure — X Feed Digest"
        assert len(result.key_takeaways) == 4
        assert result.source == "x_feed"
        assert result.post_count == 2

    def test_parse_json_with_markdown_fences(self, sample_feed_result, sample_digest_response):
        raw = f"```json\n{json.dumps(sample_digest_response)}\n```"
        result = parse_digest_response(raw, sample_feed_result, ["AI", "tech"])
        assert result.title == "AI Agents & Infrastructure — X Feed Digest"

    def test_parse_json_with_plain_fences(self, sample_feed_result, sample_digest_response):
        raw = f"```\n{json.dumps(sample_digest_response)}\n```"
        result = parse_digest_response(raw, sample_feed_result, ["AI", "tech"])
        assert result.title == "AI Agents & Infrastructure — X Feed Digest"

    def test_parse_fallback_fields(self, sample_feed_result):
        """Missing accounts/topics/post_count should fall back to feed data."""
        data = {
            "title": "Test Digest",
            "key_takeaways": ["t1"],
            "tldr": "summary",
            "twitter_hook": "hook",
            "notable_posts": [],
        }
        result = parse_digest_response(json.dumps(data), sample_feed_result, ["AI", "tech"])
        assert result.accounts == ["karpathy", "bcherny"]
        assert result.topics == ["AI", "tech"]
        assert result.post_count == 2

    def test_parse_overrides_date_and_source(self, sample_feed_result, sample_digest_response):
        sample_digest_response["date_analysed"] = "1999-01-01T00:00:00"
        sample_digest_response["source"] = "wrong"
        raw = json.dumps(sample_digest_response)
        result = parse_digest_response(raw, sample_feed_result, ["AI", "tech"])
        assert "1999-01-01" not in result.date_analysed
        assert result.source == "x_feed"

    def test_parse_invalid_json_raises(self, sample_feed_result):
        with pytest.raises(Exception):
            parse_digest_response("not json at all", sample_feed_result, ["AI"])


class TestAnalyseXFeed:
    @pytest.mark.asyncio
    async def test_analyse_x_feed_success(self, sample_feed_result, sample_digest_response):
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(sample_digest_response))]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)

        with patch(
            "mcp_content_pipeline.services.x_digest_client.anthropic.AsyncAnthropic",
            return_value=mock_client,
        ):
            result = await analyse_x_feed(
                api_key="test-key",
                model="claude-sonnet-4-20250514",
                feed_result=sample_feed_result,
                topics=["AI", "tech"],
            )
            assert isinstance(result, XDigestAnalysis)
            assert len(result.key_takeaways) > 0
            assert result.source == "x_feed"

    @pytest.mark.asyncio
    async def test_analyse_x_feed_uses_system_prompt(self, sample_feed_result, sample_digest_response):
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(sample_digest_response))]

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)

        with patch(
            "mcp_content_pipeline.services.x_digest_client.anthropic.AsyncAnthropic",
            return_value=mock_client,
        ):
            await analyse_x_feed(
                api_key="test-key",
                model="claude-sonnet-4-20250514",
                feed_result=sample_feed_result,
                topics=["AI"],
            )
            call_kwargs = mock_client.messages.create.call_args.kwargs
            assert call_kwargs["system"] == SYSTEM_PROMPT
            assert call_kwargs["model"] == "claude-sonnet-4-20250514"

    @pytest.mark.asyncio
    async def test_analyse_x_feed_api_error(self, sample_feed_result):
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(side_effect=Exception("API Error"))

        with patch(
            "mcp_content_pipeline.services.x_digest_client.anthropic.AsyncAnthropic",
            return_value=mock_client,
        ):
            with pytest.raises(Exception, match="API Error"):
                await analyse_x_feed(
                    api_key="test-key",
                    model="claude-sonnet-4-20250514",
                    feed_result=sample_feed_result,
                    topics=["AI"],
                )
