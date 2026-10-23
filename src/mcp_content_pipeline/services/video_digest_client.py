"""LLM-driven video analysis — provider-agnostic via services.llm_client."""

from __future__ import annotations

import json
import re
from datetime import datetime

from mcp_content_pipeline.models.schemas import VideoAnalysis
from mcp_content_pipeline.services.llm_client import complete

SYSTEM_PROMPT = """\
You are a news analyst helping a busy reader catch up on tech and AI trends. \
Given a YouTube video transcript, produce EXACTLY this JSON structure:
{
  "title": "original video title",
  "channel": "channel name",
  "url": "original URL",
  "date_analysed": "ISO 8601 date",
  "tldr": "1-2 sentences: the single most important thing that happened or was claimed",
  "key_takeaways": ["point 1", "point 2", ...],
  "topics": ["topic1", "topic2"]
}

RULES:
- tldr: lead with the news, not the video ("Intel guided Q2 above estimates…", not "In this video…")
- key_takeaways: 3-6 bullets, each one concrete fact, number, announcement or claim, under 25 words
- Attribute opinions and predictions to whoever made them; keep facts and figures exact
- Skip intros, sponsor reads and filler
- topics: 2-4 short lowercase tags (e.g. "ai agents", "chips", "earnings")

Respond ONLY with valid JSON — no markdown fences, no preamble."""


def build_user_prompt(
    transcript: str,
    metadata: dict,
    custom_prompt: str | None = None,
) -> str:
    """Build the user prompt for the LLM."""
    parts = [
        f"Video Title: {metadata.get('title', 'Unknown')}",
        f"Channel: {metadata.get('channel', 'Unknown')}",
        f"URL: {metadata.get('url', '')}",
        "",
        "TRANSCRIPT:",
        transcript,
    ]
    if custom_prompt:
        parts.extend(["", "ADDITIONAL INSTRUCTIONS:", custom_prompt])
    return "\n".join(parts)


def parse_analysis_response(raw: str, metadata: dict) -> VideoAnalysis:
    """Parse the LLM response into a VideoAnalysis, handling non-clean JSON."""
    # Strip markdown code fences if present
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()

    data = json.loads(cleaned)

    # Ensure required fields have fallbacks from metadata
    data.setdefault("title", metadata.get("title", "Unknown"))
    data.setdefault("channel", metadata.get("channel", "Unknown"))
    data.setdefault("url", metadata.get("url", ""))
    data["date_analysed"] = datetime.now().isoformat()

    return VideoAnalysis.model_validate(data)


async def analyse_transcript(
    api_key: str,
    model: str,
    transcript: str,
    metadata: dict,
    custom_prompt: str | None = None,
    provider: str = "anthropic",
) -> VideoAnalysis:
    """Send transcript to the configured LLM provider for analysis."""
    user_prompt = build_user_prompt(transcript, metadata, custom_prompt)

    raw_text = await complete(
        provider=provider,
        api_key=api_key,
        model=model,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
    )
    return parse_analysis_response(raw_text, metadata)
