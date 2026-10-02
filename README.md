# mcp-content-pipeline

[![PyPI version](https://img.shields.io/pypi/v/mcp-content-pipeline)](https://pypi.org/project/mcp-content-pipeline/)
[![Downloads](https://img.shields.io/pypi/dm/mcp-content-pipeline)](https://pypi.org/project/mcp-content-pipeline/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/pypi/pyversions/mcp-content-pipeline)](https://pypi.org/project/mcp-content-pipeline/)

A content analysis and digest pipeline for YouTube videos and X (Twitter) feeds, exposed as [MCP](https://modelcontextprotocol.io/) tools: extract transcripts, fetch posts from curated accounts, generate key takeaways/TLDRs/social hooks/infographics, sync to GitHub.

```mermaid
flowchart LR
    A[YouTube URL<br/>or X feed] --> B[Extract content<br/>Supadata / X API]
    B --> C[LLM analysis<br/>takeaways, TLDR, hook]
    C --> D[Gemini image<br/>comic infographic]
    D --> E[Sync to GitHub<br/>markdown + image]
```

## Role in ecosystem

- **Uses**: [mcp-llm-eval](https://github.com/berkayildi/mcp-llm-eval) for evaluation and CI quality gates
- **Produces**: benchmark JSON written to [llm-benchmarks](https://github.com/berkayildi/llm-benchmarks) under `text-generation/content-pipeline-*.json`
- **Visible at**: [LLMShot's Text Generation domain](https://llmshot.vercel.app/text-generation), Content Pipeline sub-benchmark

The eval dataset (`eval/dataset.json`) lives with this repo because the questions are specific to YouTube and X feed analysis — the dataset belongs with the use case, not the engine.

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
> "Generate an image for this analysis"
> "Sync the analysis and image to GitHub"

Or all in one prompt:

> "Use content-pipeline to analyse this video, generate the image, and sync to GitHub: https://www.youtube.com/watch?v=..."

**X Feed Digest**

> "Analyse the X feed"
> "Analyse the X feed for karpathy, bcherny, atmoio, and steipete about AI today"
> "Analyse the X feed from the last 7 days"

Or with the full pipeline:

> "Analyse the X feed, generate the image, and sync to GitHub"

## Tools

| Tool                  | Description                                                               | Requires                                |
| --------------------- | ------------------------------------------------------------------------- | --------------------------------------- |
| `analyse_video`       | Analyse a single YouTube video — transcript, takeaways, TLDR, social hook | `PIPELINE_API_KEY`, `SUPADATA_API_KEY` |
| `batch_analyse`       | Analyse multiple videos from a URL list or config file                    | `PIPELINE_API_KEY`, `SUPADATA_API_KEY` |
| `list_channel_videos` | Fetch recent videos from a YouTube channel                                | `YOUTUBE_API_KEY`                       |
| `sync_to_github`      | Push analyses as markdown files to a GitHub repo                          | `GITHUB_TOKEN`, `GITHUB_REPO`           |
| `analyse_x_feed`      | Analyse recent posts from curated X accounts — daily digest               | `PIPELINE_API_KEY`, `X_BEARER_TOKEN`    |
| `generate_image`      | Generate comic-book infographic from analysis result                      | `GEMINI_API_KEY`                        |

## Environment Variables

All prefixed with `MCP_CP_` and set in `.env` — see `.env.example` for a ready-to-copy template.

**Pipeline driver** — required for analyse_video, batch_analyse, analyse_x_feed

| Variable            | Required | Description                                                               |
| -------------------- | -------- | -------------------------------------------------------------------------- |
| `PIPELINE_PROVIDER`  | No       | `anthropic` \| `openai` \| `google` (default: `anthropic`)                 |
| `PIPELINE_API_KEY`   | Yes      | API key for the selected provider                                          |
| `PIPELINE_MODEL`     | No       | Model name valid for the selected provider (default: `claude-sonnet-4-6`)  |

**YouTube** — required for analyse_video, batch_analyse

| Variable               | Required | Description                                          |
| ----------------------- | -------- | ------------------------------------------------------ |
| `SUPADATA_API_KEY`      | Yes      | Transcript extraction                                   |
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

**Image generation** — required for generate_image

| Variable            | Required | Description                                             |
| -------------------- | -------- | ----------------------------------------------------------- |
| `GEMINI_API_KEY`    | Yes      | Google AI Studio API key                                     |
| `GEMINI_MODEL`      | No       | Default: `gemini-3.1-flash-image-preview`                    |
| `IMAGE_OUTPUT_DIR`  | No       | Default: `~/Downloads`                                       |

## Cost Projections

Estimated monthly costs for two usage patterns:

| Service                       | Daily (every day)       | Weekly X + daily YouTube |
| ----------------------------- | ----------------------- | ------------------------ |
| YouTube analysis (LLM API)    | ~$3–5/mo (1 video/day)  | ~$3–5/mo (1 video/day)   |
| X feed digest (LLM API)       | ~$2–3/mo                | ~$0.50/mo                |
| Image generation (Gemini API) | ~$2/mo ($0.067/image)   | ~$2/mo ($0.067/image)    |
| X API reads                   | ~$4/mo ($0.13/day)      | ~$0.60/mo ($0.15/week)   |
| Supadata transcript API       | ~$0 (free tier: 100/mo) | ~$0 (free tier: 100/mo)  |
| **Total (excl. LLM API)**     | **~$6–9/mo**            | **~$3–5/mo**             |

> LLM costs are estimated for the default `claude-sonnet-4-6` driver and vary with `PIPELINE_PROVIDER` / `PIPELINE_MODEL`; they are billed per token by the provider's API (a chat subscription such as Claude Pro does not cover API usage) and are not included in the totals. The X API spending cap can be configured in the [developer console](https://developer.x.com/).

### What this replaces

| Subscription          | Monthly cost | What the pipeline covers instead                           |
| --------------------- | ------------ | ---------------------------------------------------------- |
| Google One AI Premium  | ~$20/mo     | Image generation via Gemini API (~$2/mo)                   |
| X Premium              | ~$8/mo      | X feed reading via API (~$0.60–4/mo)                       |
| YouTube Premium        | ~$14/mo     | Transcript extraction via Supadata (free tier)             |
| **Total saved**        | **~$42/mo** | **Pipeline cost: ~$3–9/mo** (plus LLM API usage) |

## Eval Gates

PRs touching `services/`, `tools/`, `config.py`, `server.py`, `eval/`, `.eval-gate.yml` or `pyproject.toml` trigger a CI run via [mcp-llm-eval](https://github.com/berkayildi/mcp-llm-eval), scoring faithfulness/relevance across 8 models against a reference dataset; the PR is blocked below configured thresholds.

See `.eval-gate.yml` for threshold configuration and `eval/dataset.json` for the test dataset.

### Running benchmarks locally

The benchmark requires API keys for all three providers. Add them to the same `.env` (unprefixed — they are read by `mcp-llm-eval`, not the server):

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
```

Then run:

```bash
make benchmark        # Run eval against all 8 models
make benchmark-copy   # Copy results to llm-benchmarks repo
```

Results are written to `eval/results/` (gitignored) and feed [LLMShot](https://llmshot.vercel.app) via the [llm-benchmarks](https://github.com/berkayildi/llm-benchmarks) repo (`text-generation/content-pipeline-{summary,benchmark}.json`).

[![mcp-llm-eval](https://img.shields.io/pypi/v/mcp-llm-eval?label=mcp-llm-eval&color=blue&style=flat-square)](https://pypi.org/project/mcp-llm-eval/) powers CI quality gates. The pipeline's own driver (`MCP_CP_PIPELINE_PROVIDER`) is configurable at runtime — see Environment Variables above.

## Development

```bash
uv run mcp-content-pipeline   # run the server from the clone
uv run pytest -v --cov=src/mcp_content_pipeline
uv run ruff check src/ tests/
```

## Security

- Credentials live in a local `.env` (gitignored, see `.env.example`) — never committed, and never in MCP client config
- All API keys stay on your machine; nothing is sent anywhere but the configured providers

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Commit using [Conventional Commits](https://www.conventionalcommits.org/) (`feat: add new feature`)
4. Push and open a Pull Request

## License

[MIT](LICENSE)
