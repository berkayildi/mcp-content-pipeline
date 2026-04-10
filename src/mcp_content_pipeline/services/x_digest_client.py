"""Claude analysis client for X feed digests."""

from __future__ import annotations

import json
import re
from datetime import datetime

import anthropic

from mcp_content_pipeline.models.schemas import XDigestAnalysis, XFeedFetchResult

SYSTEM_PROMPT = """\
You are a content analyst and social media strategist. \
Given a collection of posts from X (Twitter), produce EXACTLY this JSON structure:
{
  "title": "descriptive digest title",
  "accounts": ["username1", "username2"],
  "topics": ["topic1", "topic2"],
  "key_takeaways": ["takeaway 1", "takeaway 2", ...],
  "tldr": "2-3 sentence summary a busy person can read in 15 seconds",
  "twitter_hook": "social hook — see rules below",
  "notable_posts": [
    {
      "author_username": "username",
      "text": "post text",
      "url": "post url",
      "why_notable": "reason this post stands out"
    }
  ],
  "post_count": 42
}

ANALYSIS RULES:
- Synthesise across ALL accounts — find common themes and disagreements
- Focus on the provided topics — ignore off-topic posts
- key_takeaways: 4-8 items that capture the most important insights
- notable_posts: 3-5 posts that are particularly noteworthy, with why_notable explaining the reason
- post_count: total number of posts analysed

SOCIAL HOOK RULES (strictly under 280 characters including hashtags):
- Lead with a bold claim, surprising stat, or contrarian take from the posts — NOT a summary
- Use a pattern like: "[Surprising insight] — here's why it matters:" or "Most people think [X]. Actually, [Y]."
- Write in a punchy, conversational tone — as if you're telling a friend the one thing they NEED to know
- End with 2-3 relevant hashtags (count towards 280 chars)
- Do NOT start with "Just read..." or "Today on X..." — go straight to the insight
- The hook must make someone stop scrolling and want to learn more

IMPORTANT: All output must be in English.

Respond ONLY with valid JSON — no markdown fences, no preamble."""


def build_user_prompt(feed_result: XFeedFetchResult, topics: list[str]) -> str:
    """Build the user prompt for Claude from feed data."""
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
    """Parse Claude's response into an XDigestAnalysis, handling non-clean JSON."""
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
) -> XDigestAnalysis:
    """Send X feed data to Claude for digest analysis."""
    client = anthropic.AsyncAnthropic(api_key=api_key)

    user_prompt = build_user_prompt(feed_result, topics)

    message = await client.messages.create(
        model=model,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw_text = message.content[0].text
    return parse_digest_response(raw_text, feed_result, topics)
