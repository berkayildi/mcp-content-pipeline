# mcp-content-pipeline

YouTube video analysis and X feed digest pipeline exposed as MCP tools.

## Quick Start

```bash
uv sync
uv run pytest
uv run mcp-content-pipeline
```

## Architecture

- `src/mcp_content_pipeline/server.py` — MCP server entry point, registers all tools
- `src/mcp_content_pipeline/tools/` — one file per MCP tool
- `src/mcp_content_pipeline/config.py` — `Settings` (pydantic-settings, `MCP_CP_` prefix)
- `src/mcp_content_pipeline/services/` — API clients (LLM driver, Supadata, YouTube, X, Gemini, GitHub)
- `src/mcp_content_pipeline/models/` — Pydantic schemas

## Environment Variables

All prefixed with `MCP_CP_` and kept in a local `.env` (gitignored; template in `.env.example`) — not in MCP client config. `server.main()` loads `MCP_CP_ENV_FILE` if set, otherwise the nearest `.env` from the working directory upwards; real environment variables win over `.env`. When adding a setting, update `config.py`, `.env.example`, this file and the README tables together.

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
- `GITHUB_X_OUTPUT_DIR` — optional (default: content/x-digest)

**X/Twitter** — required for analyse_x_feed:
- `X_BEARER_TOKEN`
- `X_ACCOUNTS` — comma-separated default usernames (required unless `usernames` is passed)
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
make benchmark   # runs mcp-llm-eval via uvx with keys from .env
uvx mcp-llm-eval check --results eval/results/latest_summary.json --config .eval-gate.yml
```

Triggered automatically on PRs touching `services/`, `tools/`, `config.py`, `server.py`, `eval/`, `.eval-gate.yml` or `pyproject.toml` (see `.github/workflows/eval-gate.yml`). Benchmarks 8 models across Anthropic/OpenAI/Google.

### Benchmark

```bash
make benchmark        # Run eval against all 8 models (~$0.68, ~5 minutes)
make benchmark-copy   # Copy results to ../llm-benchmarks/text-generation/
```

API keys must be set in `.env`, unprefixed (ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY).

## MCP Tools

1. `analyse_video` — analyse a single YouTube video
2. `batch_analyse` — analyse multiple videos
3. `list_channel_videos` — fetch recent videos from a channel
4. `sync_to_github` — push analyses as markdown to GitHub
5. `generate_image` — generate a comic-book infographic from an analysis result
6. `analyse_x_feed` — analyse recent posts from curated X accounts
