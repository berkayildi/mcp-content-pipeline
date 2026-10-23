# mcp-content-pipeline

YouTube video analysis and X feed digest pipeline exposed as MCP tools, synced to GitHub.

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
- `src/mcp_content_pipeline/services/` — API clients (LLM driver, YouTube transcripts, YouTube Data API, X, GitHub)
- `src/mcp_content_pipeline/models/` — Pydantic schemas

## Environment Variables

All prefixed with `MCP_CP_` and kept in a local `.env` (gitignored; template in `.env.example`) — not in MCP client config. `server.main()` loads `MCP_CP_ENV_FILE` if set, otherwise the nearest `.env` from the working directory upwards; real environment variables win over `.env`. When adding a setting, update `config.py`, `.env.example`, this file and the README tables together.

**Pipeline driver** — required for analyse_video, analyse_x_feed:
- `PIPELINE_PROVIDER` — `anthropic` | `openai` (default: anthropic). See `services/llm_client.py`.
- `PIPELINE_API_KEY` — API key for the selected provider
- `PIPELINE_MODEL` — model name valid for the selected provider (default: claude-sonnet-4-6)

**YouTube** — transcripts come from public English captions via `services/transcript.py`, no key needed:
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

## Testing

```bash
uv run pytest -v --cov=src/mcp_content_pipeline
uv run ruff check src/ tests/
```

## Eval Gate

PRs touching `services/`, `tools/`, `config.py`, `server.py`, `eval/`, `.eval-gate.yml` or `pyproject.toml` run `.github/workflows/eval-gate.yml`: [mcp-llm-eval](https://github.com/berkayildi/mcp-llm-eval) scores faithfulness/relevance of 4 Anthropic/OpenAI models against `eval/dataset.json` and blocks the PR below the thresholds in `.eval-gate.yml`. Needs `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` repo secrets.

Run it locally (keys exported, unprefixed):

```bash
uvx --with "mcp<2" --with anthropic --with openai mcp-llm-eval run --config .eval-gate.yml --dataset eval/dataset.json --output-dir eval/results
uvx --with "mcp<2" mcp-llm-eval check --results eval/results/latest_summary.json --config .eval-gate.yml
```

## MCP Tools

1. `analyse_video` — analyse a single YouTube video (TL;DR + key points)
2. `list_channel_videos` — fetch recent videos from a channel
3. `sync_to_github` — push analyses as markdown to GitHub
4. `analyse_x_feed` — analyse recent posts from curated X accounts
