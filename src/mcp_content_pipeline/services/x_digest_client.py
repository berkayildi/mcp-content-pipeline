"""LLM-driven X feed digests — provider-agnostic via services.llm_client."""

from __future__ import annotations

import json
import re
from datetime import datetime

from mcp_content_pipeline.models.schemas import XDigestAnalysis, XFeedFetchResult
from mcp_content_pipeline.services.llm_client import complete

SYSTEM_PROMPT = """\
You are a news analyst helping a busy reader catch up on tech and AI trends. \
Given a collection of posts from X (Twitter), produce EXACTLY this JSON structure:
{
  "title": "descriptive digest title",
  "accounts": ["username1", "username2"],
  "topics": ["topic1", "topic2"],
  "tldr": "1-2 sentences: the most important thing happening across these posts",
  "key_takeaways": ["point 1", "point 2", ...],
  "post_count": 42
}

RULES:
- tldr: lead with the news, not the feed ("Anthropic donated Agent Skills…", not "Today on X…")
- key_takeaways: 3-6 bullets, each one concrete fact, announcement or claim, under 25 words, ending with the source handle, e.g. "(@karpathy)"
- Synthesise across accounts; merge posts about the same thing into one bullet
- Only cover the provided topics; skip off-topic posts and filler
- Attribute opinions and predictions; keep facts and figures exact
- topics: 2-4 short lowercase tags
- post_count: total number of posts analysed

Respond ONLY with valid JSON — no markdown fences, no preamble."""


def build_user_prompt(feed_result: XFeedFetchResult, topics: list[str]) -> str:
    """Build the user prompt for the LLM from feed data."""
    parts = [
        f"Accounts: {', '.join(feed_result.accounts)}",
        f"Topics: {', '.join(topics)}",
        f"Total posts: {len(feed_result.posts)}",
        "",
        "POSTS:",
        "",
    ]

    for post in feed_result.posts:
        parts.append(
            f"@{post.author_username} ({post.created_at}) "
            f"[likes:{post.like_count} rt:{post.retweet_count}]"
        )
        parts.append(post.text)
        parts.append(f"URL: {post.url}")
        parts.append("")

    return "\n".join(parts)


def parse_digest_response(raw: str, feed_result: XFeedFetchResult, topics: list[str]) -> XDigestAnalysis:
    """Parse the LLM response into an XDigestAnalysis, handling non-clean JSON."""
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()

    data = json.loads(cleaned)

    data["date_analysed"] = datetime.now().isoformat()
    data["source"] = "x_feed"
    data.setdefault("accounts", feed_result.accounts)
    data.setdefault("topics", topics)
    data.setdefault("post_count", len(feed_result.posts))

    return XDigestAnalysis.model_validate(data)


async def analyse_x_feed(
    api_key: str,
    model: str,
    feed_result: XFeedFetchResult,
    topics: list[str],
    provider: str = "anthropic",
) -> XDigestAnalysis:
    """Send X feed data to the configured LLM provider for digest analysis."""
    user_prompt = build_user_prompt(feed_result, topics)

    raw_text = await complete(
        provider=provider,
        api_key=api_key,
        model=model,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
    )
    return parse_digest_response(raw_text, feed_result, topics)
