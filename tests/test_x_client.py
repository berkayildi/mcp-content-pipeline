"""Tests for the X API client service."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_content_pipeline.models.schemas import XFeedFetchResult
from mcp_content_pipeline.services.x_client import _user_id_cache, fetch_x_feed


@pytest.fixture(autouse=True)
def _clear_user_id_cache():
    """Clear the module-level user ID cache before each test."""
    _user_id_cache.clear()
    yield
    _user_id_cache.clear()


def _mock_response(json_data: dict):
    """Create a mock httpx response with sync json() and raise_for_status()."""
    resp = MagicMock()
    resp.json.return_value = json_data
    resp.raise_for_status.return_value = None
    return resp


def _mock_user_lookup_response(user_id: str, username: str):
    return _mock_response({"data": {"id": user_id, "username": username}})


def _mock_timeline_response(tweets: list[dict], includes: dict | None = None):
    data = {"data": tweets}
    if includes:
        data["includes"] = includes
    return _mock_response(data)


def _mock_empty_timeline_response():
    return _mock_response({"meta": {"result_count": 0}})


class TestFetchXFeed:
    @pytest.mark.asyncio
    async def test_user_id_resolution(self):
        user_resp = _mock_user_lookup_response("123", "testuser")
        timeline_resp = _mock_empty_timeline_response()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=[user_resp, timeline_resp])
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("mcp_content_pipeline.services.x_client.httpx.AsyncClient", return_value=mock_client):
            result = await fetch_x_feed(bearer_token="test-token", usernames=["testuser"])

        assert isinstance(result, XFeedFetchResult)
        assert result.accounts == ["testuser"]
        # Verify user lookup was called
        first_call = mock_client.get.call_args_list[0]
        assert "/users/by/username/testuser" in first_call.args[0]

    @pytest.mark.asyncio
    async def test_timeline_fetching(self):
        user_resp = _mock_user_lookup_response("123", "testuser")
        tweets = [
            {
                "id": "tweet1",
                "text": "Hello world",
                "created_at": "2026-04-10T10:00:00Z",
                "author_id": "123",
                "public_metrics": {
                    "like_count": 10,
                    "retweet_count": 5,
                    "reply_count": 2,
                    "quote_count": 1,
                },
            }
        ]
        includes = {"users": [{"id": "123", "username": "testuser", "name": "Test User"}]}
        timeline_resp = _mock_timeline_response(tweets, includes)

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=[user_resp, timeline_resp])
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("mcp_content_pipeline.services.x_client.httpx.AsyncClient", return_value=mock_client):
            result = await fetch_x_feed(bearer_token="test-token", usernames=["testuser"])

        assert len(result.posts) == 1
        post = result.posts[0]
        assert post.id == "tweet1"
        assert post.text == "Hello world"
        assert post.author_username == "testuser"
        assert post.author_name == "Test User"
        assert post.like_count == 10
        assert post.retweet_count == 5
        assert post.url == "https://x.com/testuser/status/tweet1"

    @pytest.mark.asyncio
    async def test_retweet_filtering(self):
        user_resp = _mock_user_lookup_response("123", "testuser")
        tweets = [
            {
                "id": "tweet1",
                "text": "Original post",
                "created_at": "2026-04-10T10:00:00Z",
                "author_id": "123",
                "public_metrics": {"like_count": 10, "retweet_count": 5, "reply_count": 0, "quote_count": 0},
            },
            {
                "id": "tweet2",
                "text": "RT @someone: retweeted post",
                "created_at": "2026-04-10T09:00:00Z",
                "author_id": "123",
                "referenced_tweets": [{"type": "retweeted", "id": "original1"}],
                "public_metrics": {"like_count": 0, "retweet_count": 0, "reply_count": 0, "quote_count": 0},
            },
        ]
        includes = {"users": [{"id": "123", "username": "testuser", "name": "Test User"}]}
        timeline_resp = _mock_timeline_response(tweets, includes)

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=[user_resp, timeline_resp])
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("mcp_content_pipeline.services.x_client.httpx.AsyncClient", return_value=mock_client):
            result = await fetch_x_feed(bearer_token="test-token", usernames=["testuser"])

        # Both posts returned (filtering done via API exclude param), but retweet is flagged
        assert len(result.posts) == 2
        retweet = [p for p in result.posts if p.id == "tweet2"][0]
        assert retweet.is_retweet is True

    @pytest.mark.asyncio
    async def test_reply_detection(self):
        user_resp = _mock_user_lookup_response("123", "testuser")
        tweets = [
            {
                "id": "tweet1",
                "text": "This is a reply",
                "created_at": "2026-04-10T10:00:00Z",
                "author_id": "123",
                "referenced_tweets": [{"type": "replied_to", "id": "parent1"}],
                "public_metrics": {"like_count": 5, "retweet_count": 0, "reply_count": 0, "quote_count": 0},
            },
        ]
        includes = {"users": [{"id": "123", "username": "testuser", "name": "Test User"}]}
        timeline_resp = _mock_timeline_response(tweets, includes)

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=[user_resp, timeline_resp])
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("mcp_content_pipeline.services.x_client.httpx.AsyncClient", return_value=mock_client):
            result = await fetch_x_feed(bearer_token="test-token", usernames=["testuser"])

        assert result.posts[0].is_reply is True

    @pytest.mark.asyncio
    async def test_engagement_sorting(self):
        user_resp = _mock_user_lookup_response("123", "testuser")
        tweets = [
            {
                "id": "low",
                "text": "Low engagement",
                "created_at": "2026-04-10T10:00:00Z",
                "author_id": "123",
                "public_metrics": {"like_count": 1, "retweet_count": 0, "reply_count": 0, "quote_count": 0},
            },
            {
                "id": "high",
                "text": "High engagement",
                "created_at": "2026-04-10T09:00:00Z",
                "author_id": "123",
                "public_metrics": {"like_count": 100, "retweet_count": 50, "reply_count": 0, "quote_count": 0},
            },
        ]
        includes = {"users": [{"id": "123", "username": "testuser", "name": "Test User"}]}
        timeline_resp = _mock_timeline_response(tweets, includes)

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=[user_resp, timeline_resp])
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("mcp_content_pipeline.services.x_client.httpx.AsyncClient", return_value=mock_client):
            result = await fetch_x_feed(bearer_token="test-token", usernames=["testuser"])

        assert result.posts[0].id == "high"
        assert result.posts[1].id == "low"

    @pytest.mark.asyncio
    async def test_failure_handling(self):
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=Exception("API rate limit exceeded"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("mcp_content_pipeline.services.x_client.httpx.AsyncClient", return_value=mock_client):
            result = await fetch_x_feed(bearer_token="test-token", usernames=["baduser"])

        assert len(result.posts) == 0
        assert len(result.failures) == 1
        assert result.failures[0].username == "baduser"
        assert "API rate limit exceeded" in result.failures[0].error

    @pytest.mark.asyncio
    async def test_cached_user_id_lookups(self):
        """Verify that user IDs are cached and reused on subsequent calls."""
        user_resp = _mock_user_lookup_response("123", "testuser")
        timeline_resp1 = _mock_empty_timeline_response()
        timeline_resp2 = _mock_empty_timeline_response()

        mock_client = AsyncMock()
        # First call: user lookup + timeline. Second call: only timeline (cached).
        mock_client.get = AsyncMock(side_effect=[user_resp, timeline_resp1, timeline_resp2])
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("mcp_content_pipeline.services.x_client.httpx.AsyncClient", return_value=mock_client):
            # Pre-populate cache from first call
            await fetch_x_feed(bearer_token="test-token", usernames=["testuser"])

            assert "testuser" in _user_id_cache
            assert _user_id_cache["testuser"] == "123"

            # Second call should use cache — only 1 API call (timeline), not 2
            await fetch_x_feed(bearer_token="test-token", usernames=["testuser"])

        # Total: user_lookup(1) + timeline(1) + timeline(1) = 3 calls
        assert mock_client.get.call_count == 3

    @pytest.mark.asyncio
    async def test_partial_failure(self):
        """One user succeeds, another fails — failures don't block successes."""
        good_user_resp = _mock_user_lookup_response("123", "gooduser")
        good_timeline = _mock_timeline_response(
            [
                {
                    "id": "t1",
                    "text": "Good post",
                    "created_at": "2026-04-10T10:00:00Z",
                    "author_id": "123",
                    "public_metrics": {"like_count": 5, "retweet_count": 0, "reply_count": 0, "quote_count": 0},
                }
            ],
            {"users": [{"id": "123", "username": "gooduser", "name": "Good User"}]},
        )

        bad_user_resp = MagicMock()
        bad_user_resp.raise_for_status.side_effect = Exception("404 Not Found")

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=[good_user_resp, good_timeline, bad_user_resp])
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("mcp_content_pipeline.services.x_client.httpx.AsyncClient", return_value=mock_client):
            result = await fetch_x_feed(bearer_token="test-token", usernames=["gooduser", "baduser"])

        assert len(result.posts) == 1
        assert len(result.failures) == 1
        assert result.failures[0].username == "baduser"
