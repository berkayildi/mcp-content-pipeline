"""Tests for the batch_analyse tool."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest

from mcp_content_pipeline.models.schemas import BatchAnalysisResult
from mcp_content_pipeline.tools.batch_analyse import batch_analyse


class TestBatchAnalyse:
    @pytest.mark.asyncio
    async def test_batch_analyse_multiple_urls(self, settings, sample_analysis_result):
        with patch(
            "mcp_content_pipeline.tools.batch_analyse.analyse_video",
            new_callable=AsyncMock,
            return_value=sample_analysis_result,
        ):
            result = await batch_analyse(
                settings=settings,
                urls=["https://youtube.com/watch?v=abc", "https://youtube.com/watch?v=def"],
            )
            assert isinstance(result, BatchAnalysisResult)
            assert len(result.successes) == 2
            assert len(result.failures) == 0

    @pytest.mark.asyncio
    async def test_batch_analyse_partial_failure(self, settings, sample_analysis_result):
        call_count = 0

        async def side_effect(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise Exception("Video unavailable")
            return sample_analysis_result

        with patch(
            "mcp_content_pipeline.tools.batch_analyse.analyse_video",
            new_callable=AsyncMock,
            side_effect=side_effect,
        ):
            result = await batch_analyse(
                settings=settings,
                urls=["https://youtube.com/watch?v=abc", "https://youtube.com/watch?v=def", "https://youtube.com/watch?v=ghi"],
            )
            assert len(result.successes) == 2
            assert len(result.failures) == 1
            assert "Video unavailable" in result.failures[0].error

    @pytest.mark.asyncio
    async def test_batch_analyse_empty_list(self, settings):
        result = await batch_analyse(settings=settings, urls=[])
        assert len(result.successes) == 0
        assert len(result.failures) == 0

    @pytest.mark.asyncio
    async def test_batch_analyse_no_input(self, settings):
        result = await batch_analyse(settings=settings)
        assert len(result.successes) == 0

    @pytest.mark.asyncio
    async def test_batch_analyse_from_json_config(self, settings, sample_analysis_result, tmp_path):
        urls = ["https://youtube.com/watch?v=abc", "https://youtube.com/watch?v=def"]
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"urls": urls}))

        with patch(
            "mcp_content_pipeline.tools.batch_analyse.analyse_video",
            new_callable=AsyncMock,
            return_value=sample_analysis_result,
        ), patch("mcp_content_pipeline.tools.batch_analyse.Path.cwd", return_value=tmp_path):
            result = await batch_analyse(settings=settings, config_file=str(config_file))
            assert len(result.successes) == 2

    @pytest.mark.asyncio
    async def test_batch_analyse_from_json_list(self, settings, sample_analysis_result, tmp_path):
        urls = ["https://youtube.com/watch?v=abc"]
        config_file = tmp_path / "urls.json"
        config_file.write_text(json.dumps(urls))

        with patch(
            "mcp_content_pipeline.tools.batch_analyse.analyse_video",
            new_callable=AsyncMock,
            return_value=sample_analysis_result,
        ), patch("mcp_content_pipeline.tools.batch_analyse.Path.cwd", return_value=tmp_path):
            result = await batch_analyse(settings=settings, config_file=str(config_file))
            assert len(result.successes) == 1

    @pytest.mark.asyncio
    async def test_batch_analyse_config_file_path_traversal_rejected(self, settings):
        with pytest.raises(ValueError, match="must be within the current working directory"):
            await batch_analyse(settings=settings, config_file="/etc/passwd")

    @pytest.mark.asyncio
    async def test_batch_analyse_config_file_relative_traversal_rejected(self, settings):
        with pytest.raises(ValueError, match="must be within the current working directory"):
            await batch_analyse(settings=settings, config_file="../../etc/passwd")

    @pytest.mark.asyncio
    async def test_batch_analyse_all_failures(self, settings):
        with patch(
            "mcp_content_pipeline.tools.batch_analyse.analyse_video",
            new_callable=AsyncMock,
            side_effect=Exception("fail"),
        ):
            result = await batch_analyse(
                settings=settings,
                urls=["https://youtube.com/watch?v=abc"],
            )
            assert len(result.successes) == 0
            assert len(result.failures) == 1
