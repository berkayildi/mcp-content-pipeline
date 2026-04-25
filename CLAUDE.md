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
- `MCP_CP_GITHUB_BRANCH` — branch to push to (default: main)
- `MCP_CP_GITHUB_OUTPUT_DIR` — output directory for YouTube analyses (default: content/youtube)
- `MCP_CP_CLAUDE_MODEL` — default: claude-sonnet-4-6
- `MCP_CP_MAX_TRANSCRIPT_TOKENS` — max transcript length in tokens (default: 100000)
- `MCP_CP_X_BEARER_TOKEN` — required for analyse_x_feed
- `MCP_CP_X_ACCOUNTS` — comma-separated X usernames
- `MCP_CP_X_TOPICS` — comma-separated topics (default: AI,tech)
- `MCP_CP_GEMINI_API_KEY` — required for generate_image
- `MCP_CP_GEMINI_MODEL` — default: gemini-3.1-flash-image-preview
- `MCP_CP_IMAGE_OUTPUT_DIR` — directory for generated images (default: ~/Downloads)

## Testing

```bash
uv run pytest -v --cov=src/mcp_content_pipeline
uv run ruff check src/ tests/
```

## Eval Gate

```bash
# Run eval locally
pip install mcp-llm-eval anthropic openai google-genai
mcp-llm-eval run --config .eval-gate.yml --dataset eval/dataset.json --output-dir eval/results
mcp-llm-eval check --results eval/results/latest_summary.json --config .eval-gate.yml
```

Triggered automatically on PRs that change prompt files or model config. Benchmarks Claude Sonnet vs Gemini 2.5 Flash.

### Benchmark

```bash
make benchmark        # Run eval against all 5 models (~$0.14, ~3 minutes)
make benchmark-copy   # Copy results to ../llm-benchmarks/text-generation/
```

API keys must be set in `.env` (ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY).

## MCP Tools

1. `analyse_video` — analyse a single YouTube video
2. `batch_analyse` — analyse multiple videos
3. `list_channel_videos` — fetch recent videos from a channel
4. `sync_to_github` — push analyses as markdown to GitHub
5. `generate_image` — generate a comic-book infographic from an analysis result
6. `analyse_x_feed` — analyse recent posts from curated X accounts
