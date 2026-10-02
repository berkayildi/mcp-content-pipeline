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

All prefixed with `MCP_CP_`.

**Pipeline driver** — required for analyse_video, batch_analyse, analyse_x_feed:
- `PIPELINE_PROVIDER` — `anthropic` | `openai` | `google` (default: anthropic). See `services/llm_client.py`.
- `PIPELINE_API_KEY` — API key for the selected provider
- `PIPELINE_MODEL` — model name valid for the selected provider (default: claude-sonnet-4-6)

**YouTube** — required for analyse_video, batch_analyse:
- `SUPADATA_API_KEY` — transcript extraction
- `YOUTUBE_API_KEY` — optional, only for list_channel_videos
- `MAX_TRANSCRIPT_TOKENS` — optional (default: 100000)

**GitHub** — required for sync_to_github:
- `GITHUB_TOKEN`
- `GITHUB_REPO` — format: "owner/repo"
- `GITHUB_BRANCH` — optional (default: main)
- `GITHUB_OUTPUT_DIR` — optional (default: content/youtube)

**X/Twitter** — required for analyse_x_feed:
- `X_BEARER_TOKEN`
- `X_ACCOUNTS` — comma-separated usernames
- `X_TOPICS` — optional (default: AI,tech)

**Image generation** — required for generate_image:
- `GEMINI_API_KEY`
- `GEMINI_MODEL` — optional (default: gemini-3.1-flash-image-preview)
- `IMAGE_OUTPUT_DIR` — optional (default: ~/Downloads)

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

Triggered automatically on PRs that change prompt files or model config. Benchmarks 8 models across Anthropic/OpenAI/Google.

### Benchmark

```bash
make benchmark        # Run eval against all 8 models (~$0.68, ~5 minutes)
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
