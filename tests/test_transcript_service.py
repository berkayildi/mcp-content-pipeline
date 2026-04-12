"""Tests for the transcript service (Supadata API)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_content_pipeline.services.transcript import (
    fetch_transcript,
    fetch_video_metadata,
    parse_video_id,
)


class TestFetchTranscript:
    @pytest.mark.asyncio
    async def test_fetch_transcript_english(self):
        """Successful English transcript from Supadata."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Hello this is a transcript"

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("mcp_content_pipeline.services.transcript.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=None)

            text, lang = await fetch_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ", supadata_api_key="test-key")
            assert text == "Hello this is a transcript"
            assert lang == "en"
            mock_client.get.assert_called_once()
            call_kwargs = mock_client.get.call_args
            assert call_kwargs[1]["params"]["lang"] == "en"

    @pytest.mark.asyncio
    async def test_fetch_transcript_fallback_available_langs(self):
        """Falls back to available languages when English returns empty."""
        empty_response = MagicMock()
        empty_response.status_code = 200
        empty_response.text = ""
        empty_response.json.return_value = {"availableLangs": ["tr", "de"]}

        tr_response = MagicMock()
        tr_response.status_code = 200
        tr_response.text = "Turkce transkript"

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=[empty_response, tr_response])

        with patch("mcp_content_pipeline.services.transcript.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=None)

            text, lang = await fetch_transcript("https://www.youtube.com/watch?v=test123", supadata_api_key="test-key")
            assert text == "Turkce transkript"
            assert lang == "tr"

    @pytest.mark.asyncio
    async def test_fetch_transcript_fallback_common_langs(self):
        """Falls back to trying common languages when no availableLangs."""
        empty_response = MagicMock()
        empty_response.status_code = 200
        empty_response.text = ""
        empty_response.json.side_effect = Exception("not json")

        fail_response = MagicMock()
        fail_response.status_code = 404
        fail_response.text = ""

        es_response = MagicMock()
        es_response.status_code = 200
        es_response.text = "Transcripcion en espanol"

        mock_client = AsyncMock()
        # First call: English (empty), then tr (404), then es (success)
        mock_client.get = AsyncMock(side_effect=[empty_response, fail_response, es_response])

        with patch("mcp_content_pipeline.services.transcript.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=None)

            text, lang = await fetch_transcript("https://www.youtube.com/watch?v=test123", supadata_api_key="test-key")
            assert text == "Transcripcion en espanol"
            assert lang == "es"

    @pytest.mark.asyncio
    async def test_fetch_transcript_no_transcript_raises(self):
        """Raises ValueError when no transcript is available in any language."""
        empty_response = MagicMock()
        empty_response.status_code = 404
        empty_response.text = ""

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=empty_response)

        with patch("mcp_content_pipeline.services.transcript.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=None)

            with pytest.raises(ValueError, match="No transcript available"):
                await fetch_transcript("https://www.youtube.com/watch?v=test123", supadata_api_key="test-key")

    @pytest.mark.asyncio
    async def test_fetch_transcript_truncation(self):
        """Long transcripts are truncated."""
        long_text = "A" * 500000
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = long_text

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("mcp_content_pipeline.services.transcript.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=None)

            text, lang = await fetch_transcript(
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ", max_tokens=1000, supadata_api_key="test-key"
            )
            assert len(text) < len(long_text)
            assert "[Transcript truncated due to length]" in text
            assert lang == "en"

    @pytest.mark.asyncio
    async def test_fetch_transcript_no_truncation_needed(self):
        """Short transcripts are not truncated."""
        short_text = "Short transcript."
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = short_text

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("mcp_content_pipeline.services.transcript.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=None)

            text, lang = await fetch_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ", supadata_api_key="test-key")
            assert text == short_text
            assert "[Transcript truncated" not in text

    @pytest.mark.asyncio
    async def test_fetch_transcript_missing_api_key_raises(self):
        """Raises ValueError when supadata_api_key is empty."""
        with pytest.raises(ValueError, match="Supadata API key is required"):
            await fetch_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")


class TestParseVideoId:
    def test_live_url(self):
        url = "https://www.youtube.com/live/-c7k_MT84eQ"
        assert parse_video_id(url) == "-c7k_MT84eQ"

    def test_live_url_with_query_params(self):
        url = "https://www.youtube.com/live/-c7k_MT84eQ?si=abc123"
        assert parse_video_id(url) == "-c7k_MT84eQ"

    def test_standard_watch_url(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert parse_video_id(url) == "dQw4w9WgXcQ"

    def test_invalid_url_raises(self):
        with pytest.raises(ValueError):
            parse_video_id("https://example.com/notavideo")


class TestFetchVideoMetadata:
    @pytest.mark.asyncio
    async def test_fetch_metadata_success(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "title": "Test Video",
            "author_name": "Test Channel",
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("mcp_content_pipeline.services.transcript.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await fetch_video_metadata("dQw4w9WgXcQ")
            assert result["title"] == "Test Video"
            assert result["channel"] == "Test Channel"
            assert "youtube.com/watch?v=dQw4w9WgXcQ" in result["url"]

    @pytest.mark.asyncio
    async def test_fetch_metadata_missing_fields(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("mcp_content_pipeline.services.transcript.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await fetch_video_metadata("dQw4w9WgXcQ")
            assert result["title"] == "Unknown Title"
            assert result["channel"] == "Unknown Channel"
