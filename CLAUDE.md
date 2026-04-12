# mcp-content-pipeline

YouTube video analysis and content pipeline exposed as MCP tools.

## Quick Start

```bash
uv sync
uv run pytest
uv run mcp-content-pipeline
```

## Architecture

- `src/mcp_content_pipeline/server.py` — MCP server entry point, registers all tools
- `src/mcp_content_pipeline/tools/` — one file per MCP tool
- `src/mcp_content_pipeline/services/` — API clients (YouTube, Claude, GitHub)
- `src/mcp_content_pipeline/models/` — Pydantic schemas

## Environment Variables

All prefixed with `MCP_CP_`:
- `MCP_CP_ANTHROPIC_API_KEY` — required
- `MCP_CP_YOUTUBE_API_KEY` — optional (only for list_channel_videos)
- `MCP_CP_SUPADATA_API_KEY` — required for YouTube transcript extraction
- `MCP_CP_GITHUB_TOKEN` — required for sync_to_github
- `MCP_CP_GITHUB_REPO` — format: "owner/repo"
- `MCP_CP_CLAUDE_MODEL` — default: claude-sonnet-4-20250514
- `MCP_CP_X_BEARER_TOKEN` — required for analyse_x_feed
- `MCP_CP_X_ACCOUNTS` — comma-separated X usernames
- `MCP_CP_X_TOPICS` — comma-separated topics (default: AI,tech)
- `MCP_CP_GEMINI_API_KEY` — required for generate_image
- `MCP_CP_GEMINI_MODEL` — default: gemini-3.1-flash-image-preview

## Testing

```bash
uv run pytest -v --cov=src/mcp_content_pipeline
uv run ruff check src/ tests/
```

## MCP Tools

1. `analyse_video` — analyse a single YouTube video
2. `batch_analyse` — analyse multiple videos
3. `list_channel_videos` — fetch recent videos from a channel
4. `sync_to_github` — push analyses as markdown to GitHub
5. `generate_image` — generate a comic-book infographic from an analysis result
6. `analyse_x_feed` — analyse recent posts from curated X accounts
