"""YouTube English transcript extraction via the public InnerTube player endpoint."""

from __future__ import annotations

import html
import re

import httpx

HTTP_TIMEOUT = 30.0
PLAYER_URL = "https://www.youtube.com/youtubei/v1/player"
# ANDROID client returns caption URLs that need no PoToken
CLIENT_VERSION = "20.10.38"
PLAYER_CONTEXT = {"client": {"clientName": "ANDROID", "clientVersion": CLIENT_VERSION}}
PLAYER_HEADERS = {"User-Agent": f"com.google.android.youtube/{CLIENT_VERSION} (Linux; U; Android 14)"}


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


async def fetch_transcript(video_id: str, max_tokens: int = 100000) -> tuple[str, dict]:
    """Fetch the English transcript and metadata for a video; returns (text, {title, channel, url})."""
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.post(
            PLAYER_URL,
            json={"context": PLAYER_CONTEXT, "videoId": video_id},
            headers=PLAYER_HEADERS,
        )
        resp.raise_for_status()
        player = resp.json()

        status = player.get("playabilityStatus", {})
        if status.get("status") != "OK":
            raise ValueError(f"Video {video_id} is not playable: {status.get('reason') or status.get('status')}")

        tracks = player.get("captions", {}).get("playerCaptionsTracklistRenderer", {}).get("captionTracks", [])
        track = _pick_english_track(tracks)
        if track is None:
            raise ValueError(f"No English transcript available for video {video_id}")

        caption_resp = await client.get(track["baseUrl"])
        caption_resp.raise_for_status()

    text = parse_caption_xml(caption_resp.text)
    if not text:
        raise ValueError(f"Empty English transcript for video {video_id}")

    details = player.get("videoDetails", {})
    metadata = {
        "title": details.get("title") or "Unknown Title",
        "channel": details.get("author") or "Unknown Channel",
        "url": f"https://www.youtube.com/watch?v={video_id}",
    }
    return _truncate(text, max_tokens), metadata


def _pick_english_track(tracks: list[dict]) -> dict | None:
    """Prefer a manual English track over an auto-generated (asr) one."""
    english = [t for t in tracks if t.get("languageCode", "").split("-")[0] == "en"]
    manual = [t for t in english if t.get("kind") != "asr"]
    return (manual or english or [None])[0]


def parse_caption_xml(xml: str) -> str:
    """Flatten timedtext XML (srv1 <text> or srv3 <p>) into plain text."""
    segments = re.findall(r"<(?:p|text)\b[^>]*>(.*?)</(?:p|text)>", xml, re.S)
    # srv3 nests <s> word tags; entities can be double-escaped
    cleaned = (html.unescape(html.unescape(re.sub(r"<[^>]+>", "", s))) for s in segments)
    return " ".join(" ".join(c.split()) for c in cleaned if c.strip())


def _truncate(text: str, max_tokens: int) -> str:
    """Truncate transcript text to approximately max_tokens."""
    max_chars = max_tokens * 4
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n[Transcript truncated due to length]"
    return text
