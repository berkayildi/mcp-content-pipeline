"""MCP tool: batch analyse multiple YouTube videos."""

from __future__ import annotations

import json
from pathlib import Path

from mcp_content_pipeline.config import Settings
from mcp_content_pipeline.models.schemas import BatchAnalysisResult, BatchFailure
from mcp_content_pipeline.tools.analyse_video import analyse_video


async def batch_analyse(
    settings: Settings,
    urls: list[str] | None = None,
    config_file: str | None = None,
) -> BatchAnalysisResult:
    """Analyse multiple YouTube videos from a list of URLs or config file."""
    if config_file:
        # Path is constrained to CWD to prevent accidental reads outside the project.
        # This is a local MCP tool: we trust the CWD and do not resolve symlinks that
        # point outside it. A symlink within CWD pointing elsewhere will still be read.
        path = Path(config_file).resolve()
        cwd = Path.cwd().resolve()
        if not path.is_relative_to(cwd):
            raise ValueError(
                f"config_file must be within the current working directory ({cwd}). "
                f"Got: {path}"
            )
        content = path.read_text()
        if path.suffix in (".yaml", ".yml"):
            import importlib

            yaml = importlib.import_module("yaml")
            data = yaml.safe_load(content)
        else:
            data = json.loads(content)

        file_urls = data if isinstance(data, list) else data.get("urls", [])
        urls = (urls or []) + file_urls

    if not urls:
        return BatchAnalysisResult()

    result = BatchAnalysisResult()

    for url in urls:
        try:
            analysis = await analyse_video(url=url, settings=settings)
            result.successes.append(analysis)
        except Exception as e:
            result.failures.append(BatchFailure(url=url, error=str(e)))

    return result
