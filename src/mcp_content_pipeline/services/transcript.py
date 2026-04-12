"""YouTube transcript extraction via Supadata API."""

from __future__ import annotations

import re

import httpx

HTTP_TIMEOUT = 30.0
COMMON_LANGS = ["tr", "es", "pt", "fr", "de", "ja", "ko", "zh", "ar", "hi"]


def parse_video_id(url: str) -> str:
    """Extract video ID from various YouTube URL formats."""
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/|youtube\.com/live/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not parse video ID from URL: {url}")


async def fetch_transcript(
    url: str, max_tokens: int = 100000, supadata_api_key: str = ""
) -> tuple[str, str]:
    """Fetch transcript for a YouTube video via Supadata API.

    Returns a tuple of (transcript_text, language_code).
    """
    if not supadata_api_key:
        raise ValueError("Supadata API key is required for transcript extraction")

    headers = {"x-api-key": supadata_api_key}
    base_params = {"url": url, "text": "true", "mode": "auto"}

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        # Step 1: Try English
        resp = await client.get(
            "https://api.supadata.ai/v1/transcript",
            headers=headers,
            params={**base_params, "lang": "en"},
        )
        if resp.status_code == 200:
            text = resp.text.strip()
            if text:
                return _truncate(text, max_tokens), "en"

        # Step 2: Check available languages from response
        if resp.status_code in (200, 206):
            try:
                data = resp.json()
                available_langs = data.get("availableLangs", [])
                for lang in available_langs:
                    resp2 = await client.get(
                        "https://api.supadata.ai/v1/transcript",
                        headers=headers,
                        params={**base_params, "lang": lang},
                    )
                    if resp2.status_code == 200:
                        text = resp2.text.strip()
                        if text:
                            return _truncate(text, max_tokens), lang
            except Exception:
                pass

        # Step 3: Try common languages directly
        for lang in COMMON_LANGS:
            resp3 = await client.get(
                "https://api.supadata.ai/v1/transcript",
                headers=headers,
                params={**base_params, "lang": lang},
            )
            if resp3.status_code == 200:
                text = resp3.text.strip()
                if text:
                    return _truncate(text, max_tokens), lang

    raise ValueError(f"No transcript available for: {url}")


def _truncate(text: str, max_tokens: int) -> str:
    """Truncate transcript text to approximately max_tokens."""
    max_chars = max_tokens * 4
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n[Transcript truncated due to length]"
    return text


async def fetch_video_metadata(video_id: str) -> dict:
    """Fetch video metadata via oembed (no API key needed)."""
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()

    return {
        "title": data.get("title", "Unknown Title"),
        "channel": data.get("author_name", "Unknown Channel"),
        "url": f"https://www.youtube.com/watch?v={video_id}",
    }
