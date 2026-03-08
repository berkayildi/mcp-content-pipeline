"""MCP tool: sync analysed content to GitHub as markdown files."""

from __future__ import annotations

from mcp_content_pipeline.config import Settings
from mcp_content_pipeline.models.schemas import SyncResult, VideoAnalysis
from mcp_content_pipeline.services.github_client import (
    sync_to_github as _sync_to_github,
)


async def sync_to_github(
    analyses: list[VideoAnalysis],
    settings: Settings,
    commit_message: str = "Add video analyses",
) -> SyncResult:
    """Push analysed content as markdown files to a GitHub repository."""
    if len(commit_message) > 500:
        raise ValueError("commit_message must be 500 characters or fewer.")
    if not commit_message.strip():
        raise ValueError("commit_message must not be empty.")

    if not settings.github_token:
        raise ValueError(
            "GitHub token not configured. "
            "Set MCP_CP_GITHUB_TOKEN environment variable to use this tool."
        )
    if not settings.github_repo:
        raise ValueError(
            "GitHub repo not configured. "
            "Set MCP_CP_GITHUB_REPO environment variable (format: owner/repo)."
        )

    return await _sync_to_github(
        token=settings.github_token,
        repo_name=settings.github_repo,
        branch=settings.github_branch,
        output_dir=settings.github_output_dir,
        analyses=analyses,
        commit_message=commit_message,
    )
