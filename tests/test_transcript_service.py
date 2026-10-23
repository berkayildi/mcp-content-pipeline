"""Tests for the transcript service (YouTube InnerTube player)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_content_pipeline.services.transcript import (
    _pick_english_track,
    _truncate,
    fetch_transcript,
    parse_caption_xml,
    parse_video_id,
)

SRV3_XML = """<?xml version="1.0" encoding="utf-8" ?><timedtext format="3">
<body>
<p t="1360" d="1680">We&amp;#39;re no strangers</p>
<p t="18640" d="3240"><s>to</s><s t="200"> love</s></p>
<p t="22640" d="4320">You know the rules
and so do I</p>
<p t="30000" d="10"> </p>
</body></timedtext>"""


def _player(tracks=None, status="OK", reason=None):
    playability = {"status": status}
    if reason:
        playability["reason"] = reason
    data = {
        "playabilityStatus": playability,
        "videoDetails": {"title": "Test Video", "author": "Test Channel"},
    }
    if tracks is not None:
        data["captions"] = {"playerCaptionsTracklistRenderer": {"captionTracks": tracks}}
    return data


def _mock_client(player: dict, caption_text: str = SRV3_XML):
    player_resp = MagicMock()
    player_resp.json.return_value = player
    caption_resp = MagicMock()
    caption_resp.text = caption_text

    client = AsyncMock()
    client.post = AsyncMock(return_value=player_resp)
    client.get = AsyncMock(return_value=caption_resp)
    return client


def _patch_client(client):
    patcher = patch("mcp_content_pipeline.services.transcript.httpx.AsyncClient")
    MockClient = patcher.start()
    MockClient.return_value.__aenter__ = AsyncMock(return_value=client)
    MockClient.return_value.__aexit__ = AsyncMock(return_value=None)
    return patcher


class TestFetchTranscript:
    @pytest.mark.asyncio
    async def test_fetch_transcript_success(self):
        client = _mock_client(_player([{"languageCode": "en", "baseUrl": "https://caps/en"}]))
        patcher = _patch_client(client)
        try:
            text, metadata = await fetch_transcript("dQw4w9WgXcQ")
        finally:
            patcher.stop()

        assert text == "We're no strangers to love You know the rules and so do I"
        assert metadata == {
            "title": "Test Video",
            "channel": "Test Channel",
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        }
        assert client.post.call_args.kwargs["json"]["videoId"] == "dQw4w9WgXcQ"
        client.get.assert_called_once_with("https://caps/en")

    @pytest.mark.asyncio
    async def test_fetch_transcript_no_english_track(self):
        client = _mock_client(_player([{"languageCode": "tr", "baseUrl": "https://caps/tr"}]))
        patcher = _patch_client(client)
        try:
            with pytest.raises(ValueError, match="No English transcript"):
                await fetch_transcript("dQw4w9WgXcQ")
        finally:
            patcher.stop()
        client.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_fetch_transcript_no_captions(self):
        client = _mock_client(_player(tracks=None))
        patcher = _patch_client(client)
        try:
            with pytest.raises(ValueError, match="No English transcript"):
                await fetch_transcript("dQw4w9WgXcQ")
        finally:
            patcher.stop()

    @pytest.mark.asyncio
    async def test_fetch_transcript_unplayable(self):
        client = _mock_client(_player(status="LOGIN_REQUIRED", reason="Sign in to confirm your age"))
        patcher = _patch_client(client)
        try:
            with pytest.raises(ValueError, match="not playable: Sign in to confirm your age"):
                await fetch_transcript("dQw4w9WgXcQ")
        finally:
            patcher.stop()

    @pytest.mark.asyncio
    async def test_fetch_transcript_empty_captions(self):
        client = _mock_client(
            _player([{"languageCode": "en", "baseUrl": "https://caps/en"}]),
            caption_text="<timedtext><body></body></timedtext>",
        )
        patcher = _patch_client(client)
        try:
            with pytest.raises(ValueError, match="Empty English transcript"):
                await fetch_transcript("dQw4w9WgXcQ")
        finally:
            patcher.stop()

    @pytest.mark.asyncio
    async def test_fetch_transcript_truncates(self):
        client = _mock_client(_player([{"languageCode": "en", "baseUrl": "https://caps/en"}]))
        patcher = _patch_client(client)
        try:
            text, _ = await fetch_transcript("dQw4w9WgXcQ", max_tokens=2)
        finally:
            patcher.stop()
        assert text.startswith("We're no")
        assert text.endswith("[Transcript truncated due to length]")


class TestPickEnglishTrack:
    def test_prefers_manual_over_asr(self):
        tracks = [
            {"languageCode": "en", "kind": "asr", "baseUrl": "asr"},
            {"languageCode": "en", "baseUrl": "manual"},
        ]
        assert _pick_english_track(tracks)["baseUrl"] == "manual"

    def test_falls_back_to_asr(self):
        tracks = [{"languageCode": "de"}, {"languageCode": "en", "kind": "asr", "baseUrl": "asr"}]
        assert _pick_english_track(tracks)["baseUrl"] == "asr"

    def test_accepts_regional_english(self):
        tracks = [{"languageCode": "en-GB", "baseUrl": "gb"}]
        assert _pick_english_track(tracks)["baseUrl"] == "gb"

    def test_none_when_no_english(self):
        assert _pick_english_track([{"languageCode": "es"}, {"languageCode": "eng-fake"}]) is None
        assert _pick_english_track([]) is None


class TestParseCaptionXml:
    def test_srv3(self):
        assert parse_caption_xml(SRV3_XML) == "We're no strangers to love You know the rules and so do I"

    def test_srv1(self):
        xml = '<transcript><text start="0" dur="1">Hello &amp;amp; welcome</text><text start="1">back</text></transcript>'
        assert parse_caption_xml(xml) == "Hello & welcome back"

    def test_empty(self):
        assert parse_caption_xml("") == ""

    def test_escaped_markup_stripped(self):
        xml = '<text start="0">&amp;lt;font color=&amp;quot;#E5E5E5&amp;quot;&amp;gt;Hello&amp;lt;/font&amp;gt; world</text>'
        assert parse_caption_xml(xml) == "Hello world"


class TestTruncate:
    def test_short_text_unchanged(self):
        assert _truncate("short", 100) == "short"

    def test_long_text_truncated(self):
        result = _truncate("a" * 50, 10)
        assert result == "a" * 40 + "\n\n[Transcript truncated due to length]"


class TestParseVideoId:
    def test_live_url(self):
        assert parse_video_id("https://www.youtube.com/live/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
