"""X (Twitter) API v2 client for fetching user timelines."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import httpx

from mcp_content_pipeline.models.schemas import XFeedFailure, XFeedFetchResult, XPost

BASE_URL = "https://api.x.com/2"
HTTP_TIMEOUT = 30.0

# Module-level cache: username -> user ID
_user_id_cache: dict[str, str] = {}


async def _resolve_user_id(client: httpx.AsyncClient, username: str) -> str:
    """Resolve an X username to a user ID, using cache when available."""
    if username in _user_id_cache:
        return _user_id_cache[username]

    resp = await client.get(f"{BASE_URL}/users/by/username/{username}")
    resp.raise_for_status()
    data = resp.json()

    if "data" not in data:
        errors = data.get("errors", [{}])
        msg = errors[0].get("detail", f"User @{username} not found") if errors else f"User @{username} not found"
        raise ValueError(msg)

    user_id = data["data"]["id"]
    _user_id_cache[username] = user_id
    return user_id


async def _fetch_user_timeline(
    client: httpx.AsyncClient,
    user_id: str,
    username: str,
    start_time: str,
    max_results: int,
    exclude_retweets: bool,
    exclude_replies: bool,
) -> list[XPost]:
    """Fetch recent tweets from a user's timeline."""
    params: dict[str, str | int] = {
        "tweet.fields": "created_at,public_metrics,referenced_tweets,author_id",
        "expansions": "author_id",
        "user.fields": "username,name",
        "max_results": min(max_results, 100),
        "start_time": start_time,
    }

    exclude_types = []
    if exclude_retweets:
        exclude_types.append("retweets")
    if exclude_replies:
        exclude_types.append("replies")
    if exclude_types:
        params["exclude"] = ",".join(exclude_types)

    resp = await client.get(f"{BASE_URL}/users/{user_id}/tweets", params=params)
    resp.raise_for_status()
    data = resp.json()

    if "data" not in data:
        return []

    # Build author lookup from includes
    authors: dict[str, dict[str, str]] = {}
    for user in data.get("includes", {}).get("users", []):
        authors[user["id"]] = {"username": user["username"], "name": user["name"]}

    posts: list[XPost] = []
    for tweet in data["data"]:
        ref_tweets = tweet.get("referenced_tweets", [])
        is_retweet = any(rt.get("type") == "retweeted" for rt in ref_tweets)
        is_reply = any(rt.get("type") == "replied_to" for rt in ref_tweets)

        metrics = tweet.get("public_metrics", {})
        author_id = tweet.get("author_id", "")
        author_info = authors.get(author_id, {"username": username, "name": username})

        posts.append(
            XPost(
                id=tweet["id"],
                text=tweet["text"],
                author_username=author_info["username"],
                author_name=author_info["name"],
                created_at=tweet.get("created_at", ""),
                url=f"https://x.com/{author_info['username']}/status/{tweet['id']}",
                retweet_count=metrics.get("retweet_count", 0),
                like_count=metrics.get("like_count", 0),
                reply_count=metrics.get("reply_count", 0),
                quote_count=metrics.get("quote_count", 0),
                is_retweet=is_retweet,
                is_reply=is_reply,
            )
        )

    return posts


async def fetch_x_feed(
    bearer_token: str,
    usernames: list[str],
    hours_back: int = 24,
    max_results_per_user: int = 20,
    exclude_retweets: bool = True,
    exclude_replies: bool = True,
) -> XFeedFetchResult:
    """Fetch recent posts from multiple X accounts.

    Resolves usernames to user IDs, fetches timelines, and returns
    all posts sorted by engagement (likes + retweets) descending.
    """
    start_time = (datetime.now(timezone.utc) - timedelta(hours=hours_back)).strftime("%Y-%m-%dT%H:%M:%SZ")

    all_posts: list[XPost] = []
    failures: list[XFeedFailure] = []

    headers = {"Authorization": f"Bearer {bearer_token}"}

    async with httpx.AsyncClient(headers=headers, timeout=HTTP_TIMEOUT) as client:
        for username in usernames:
            try:
                user_id = await _resolve_user_id(client, username)
                posts = await _fetch_user_timeline(
                    client=client,
                    user_id=user_id,
                    username=username,
                    start_time=start_time,
                    max_results=max_results_per_user,
                    exclude_retweets=exclude_retweets,
                    exclude_replies=exclude_replies,
                )
                all_posts.extend(posts)
            except Exception as e:
                failures.append(XFeedFailure(username=username, error=str(e)))

    # Sort by engagement (likes + retweets) descending
    all_posts.sort(key=lambda p: p.like_count + p.retweet_count, reverse=True)

    return XFeedFetchResult(
        accounts=usernames,
        posts=all_posts,
        failures=failures,
    )
