# mcp-content-pipeline

[![PyPI version](https://img.shields.io/pypi/v/mcp-content-pipeline)](https://pypi.org/project/mcp-content-pipeline/)
[![Downloads](https://img.shields.io/pypi/dm/mcp-content-pipeline)](https://pypi.org/project/mcp-content-pipeline/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/pypi/pyversions/mcp-content-pipeline)](https://pypi.org/project/mcp-content-pipeline/)

A content analysis and digest pipeline for YouTube videos and X (Twitter) feeds, exposed as [MCP](https://modelcontextprotocol.io/) tools: extract English transcripts, fetch posts from curated accounts, generate TL;DRs and key points, sync to GitHub.

```mermaid
flowchart LR
    A[YouTube URL<br/>or X feed] --> B[Extract content<br/>YouTube captions / X API]
    B --> C[LLM analysis<br/>TL;DR, key points]
    C --> D[Sync to GitHub<br/>markdown]
```

## Quick Start

```bash
git clone https://github.com/berkayildi/mcp-content-pipeline.git
cd mcp-content-pipeline
cp .env.example .env   # fill in the keys for the tools you use
uv sync
```

### Configuration

All config lives in a local `.env` (gitignored). On startup the server loads the nearest `.env` from its working directory upwards; set `MCP_CP_ENV_FILE` to load one from an explicit path instead. Variables already present in the process environment take precedence over `.env`.

### MCP client

Launch the server from the clone so it picks up `.env` — the same block works for Claude Desktop, Claude Code (`.mcp.json`), and other MCP clients:

```json
{
  "mcpServers": {
    "content-pipeline": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mcp-content-pipeline", "mcp-content-pipeline"]
    }
  }
}
```

To run the published package without a clone, use `uvx mcp-content-pipeline` and point it at your `.env`:

```json
{
  "mcpServers": {
    "content-pipeline": {
      "command": "uvx",
      "args": ["mcp-content-pipeline"],
      "env": { "MCP_CP_ENV_FILE": "/path/to/.env" }
    }
  }
}
```

## Usage

**YouTube Analysis**

> "Use content-pipeline to analyse this video: https://www.youtube.com/watch?v=..."
> "Sync the analysis to GitHub"

Or all in one prompt:

> "Use content-pipeline to analyse this video and sync to GitHub: https://www.youtube.com/watch?v=..."

**X Feed Digest**

> "Analyse the X feed"
> "Analyse the X feed for karpathy, bcherny, atmoio, and steipete about AI today"
> "Analyse the X feed from the last 7 days"

Or with the full pipeline:

> "Analyse the X feed and sync to GitHub"

## Tools

| Tool                  | Description                                                               | Requires                                |
| --------------------- | ------------------------------------------------------------------------- | --------------------------------------- |
| `analyse_video`       | Analyse a single YouTube video (English captions) — TL;DR and key points  | `PIPELINE_API_KEY`                      |
| `list_channel_videos` | Fetch recent videos from a YouTube channel                                | `YOUTUBE_API_KEY`                       |
| `sync_to_github`      | Push analyses as markdown files to a GitHub repo                          | `GITHUB_TOKEN`, `GITHUB_REPO`           |
| `analyse_x_feed`      | Analyse recent posts from curated X accounts — daily digest               | `PIPELINE_API_KEY`, `X_BEARER_TOKEN`    |

## Environment Variables

All prefixed with `MCP_CP_` and set in `.env` — see `.env.example` for a ready-to-copy template.

**Pipeline driver** — required for analyse_video, analyse_x_feed

| Variable            | Required | Description                                                               |
| -------------------- | -------- | -------------------------------------------------------------------------- |
| `PIPELINE_PROVIDER`  | No       | `anthropic` \| `openai` (default: `anthropic`)                            |
| `PIPELINE_API_KEY`   | Yes      | API key for the selected provider                                          |
| `PIPELINE_MODEL`     | No       | Model name valid for the selected provider (default: `claude-sonnet-4-6`)  |

**YouTube** — transcripts come from public English captions, no key needed

| Variable               | Required | Description                                          |
| ----------------------- | -------- | ------------------------------------------------------ |
| `YOUTUBE_API_KEY`       | No       | Only for `list_channel_videos`                          |
| `MAX_TRANSCRIPT_TOKENS` | No       | Default: `100000`                                       |

**GitHub** — required for sync_to_github

| Variable            | Required | Description                               |
| -------------------- | -------- | -------------------------------------------- |
| `GITHUB_TOKEN`       | Yes      | Personal access token                        |
| `GITHUB_REPO`        | Yes      | Target repo, `owner/repo` format             |
| `GITHUB_BRANCH`      | No       | Default: `main`                              |
| `GITHUB_OUTPUT_DIR`  | No       | Default: `content/youtube`                   |
| `GITHUB_X_OUTPUT_DIR`| No       | Default: `content/x-digest`                  |

**X/Twitter** — required for analyse_x_feed

| Variable       | Required | Description                      |
| --------------- | -------- | ----------------------------------- |
| `X_BEARER_TOKEN`| Yes      | X API v2 bearer token                |
| `X_ACCOUNTS`    | No       | Default usernames, comma-separated — required unless `usernames` is passed to the tool |
| `X_TOPICS`      | No       | Default: `AI,tech`                   |

## Cost Projections

Estimated monthly costs for two usage patterns:

| Service                       | Daily (every day)       | Weekly X + daily YouTube |
| ----------------------------- | ----------------------- | ------------------------ |
| YouTube analysis (LLM API)    | ~$3–5/mo (1 video/day)  | ~$3–5/mo (1 video/day)   |
| X feed digest (LLM API)       | ~$2–3/mo                | ~$0.50/mo                |
| X API reads                   | ~$4/mo ($0.13/day)      | ~$0.60/mo ($0.15/week)   |
| **Total (excl. LLM API)**     | **~$4/mo**              | **~$0.60/mo**            |

> LLM costs are estimated for the default `claude-sonnet-4-6` driver and vary with `PIPELINE_PROVIDER` / `PIPELINE_MODEL`; they are billed per token by the provider's API (a chat subscription such as Claude Pro does not cover API usage) and are not included in the totals. The X API spending cap can be configured in the [developer console](https://developer.x.com/).

### What this replaces

| Subscription          | Monthly cost | What the pipeline covers instead                           |
| --------------------- | ------------ | ---------------------------------------------------------- |
| X Premium              | ~$8/mo      | X feed reading via API (~$0.60–4/mo)                       |
| YouTube Premium        | ~$14/mo     | Transcript extraction from public captions (free)          |
| **Total saved**        | **~$22/mo** | **Pipeline cost: ~$0.60–4/mo** (plus LLM API usage) |

## Eval Gate

PRs touching `services/`, `tools/`, `config.py`, `server.py`, `eval/`, `.eval-gate.yml` or `pyproject.toml` run `.github/workflows/eval-gate.yml`: [mcp-llm-eval](https://github.com/berkayildi/mcp-llm-eval) scores faithfulness/relevance of 4 Anthropic/OpenAI models against `eval/dataset.json` and blocks the PR below the thresholds in `.eval-gate.yml`. Needs `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` repo secrets.

Run it locally (keys exported, unprefixed):

```bash
uvx --with "mcp<2" --with anthropic --with openai mcp-llm-eval run --config .eval-gate.yml --dataset eval/dataset.json --output-dir eval/results
uvx --with "mcp<2" mcp-llm-eval check --results eval/results/latest_summary.json --config .eval-gate.yml
```
