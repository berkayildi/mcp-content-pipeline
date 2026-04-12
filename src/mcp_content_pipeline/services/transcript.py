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
) -> tuple[str, str, str | None]:
    """Fetch transcript for a YouTube video via Supadata API.

    Returns a tuple of (transcript_text, language_code, title_or_none).
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
                title = _extract_title(resp)
                return _truncate(text, max_tokens), "en", title

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
                            title = _extract_title(resp2)
                            return _truncate(text, max_tokens), lang, title
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
                    title = _extract_title(resp3)
                    return _truncate(text, max_tokens), lang, title

    raise ValueError(f"No transcript available for: {url}")


def _extract_title(resp: httpx.Response) -> str | None:
    """Try to extract a title field from a Supadata JSON response."""
    try:
        data = resp.json()
        if isinstance(data, dict):
            return data.get("title") or None
    except Exception:
        return None
    return None


def _truncate(text: str, max_tokens: int) -> str:
    """Truncate transcript text to approximately max_tokens."""
    max_chars = max_tokens * 4
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n[Transcript truncated due to length]"
    return text


async def fetch_video_metadata(video_id_or_url: str) -> dict:
    """Fetch video metadata via oembed (no API key needed).

    Accepts a bare video ID or any YouTube URL (including /live/ URLs).
    The URL is normalised to youtube.com/watch?v= before calling oEmbed,
    because the oEmbed endpoint rejects /live/ URLs.
    """
    try:
        video_id = parse_video_id(video_id_or_url)
    except ValueError:
        video_id = video_id_or_url
    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    url = f"https://www.youtube.com/oembed?url={watch_url}&format=json"
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.get(url)
        if resp.status_code in (401, 403):
            return {
                "title": "Unknown Title",
                "channel": "Unknown Channel",
                "url": f"https://www.youtube.com/watch?v={video_id}",
            }
        resp.raise_for_status()
        data = resp.json()

    return {
        "title": data.get("title", "Unknown Title"),
        "channel": data.get("author_name", "Unknown Channel"),
        "url": f"https://www.youtube.com/watch?v={video_id}",
    }
