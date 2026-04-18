# mcp-content-pipeline

[![PyPI version](https://img.shields.io/pypi/v/mcp-content-pipeline)](https://pypi.org/project/mcp-content-pipeline/)
[![Downloads](https://img.shields.io/pypi/dm/mcp-content-pipeline)](https://pypi.org/project/mcp-content-pipeline/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/pypi/pyversions/mcp-content-pipeline)](https://pypi.org/project/mcp-content-pipeline/)

A content analysis and digest pipeline for YouTube videos and X (Twitter) feeds, exposed as [MCP](https://modelcontextprotocol.io/) tools. Extract transcripts, fetch posts from curated accounts, and generate key takeaways, TLDRs, social hooks, and comic-book infographics — all callable by any MCP-compatible AI client like Claude Desktop.

## Why?

Keeping up with YouTube channels and X accounts means scattered tabs, manual note-taking, and lost insights. This MCP server turns content consumption into structured, chainable tools. Analyse a Bloomberg video, digest your X feed, generate infographics, and sync everything to GitHub — all from a single conversation with Claude.

## Quick Start

```bash
uvx mcp-content-pipeline
```

Or install explicitly:

```bash
uv tool install mcp-content-pipeline
mcp-content-pipeline
```

### Claude Desktop Configuration

Add to your Claude Desktop MCP config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "content-pipeline": {
      "command": "/usr/local/bin/uvx",
      "args": ["mcp-content-pipeline"],
      "env": {
        "MCP_CP_ANTHROPIC_API_KEY": "sk-ant-...",
        "MCP_CP_SUPADATA_API_KEY": "sd_...",
        "MCP_CP_GITHUB_TOKEN": "ghp_...",
        "MCP_CP_GITHUB_REPO": "your-username/your-repo",
        "MCP_CP_GEMINI_API_KEY": "your-gemini-api-key",
        "MCP_CP_X_BEARER_TOKEN": "your-x-bearer-token",
        "MCP_CP_X_ACCOUNTS": "karpathy,bcherny,atmoio,steipete",
        "MCP_CP_X_TOPICS": "AI,tech,engineering"
      }
    }
  }
}
```

## Usage

Once configured in Claude Desktop, use the tools in a single conversation.

> **Tip:** Including "content-pipeline" for YouTube or "X feed" for Twitter helps Claude Desktop route to the right tool.

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
| `analyse_video`       | Analyse a single YouTube video — transcript, takeaways, TLDR, social hook | `ANTHROPIC_API_KEY`, `SUPADATA_API_KEY` |
| `batch_analyse`       | Analyse multiple videos from a URL list or config file                    | `ANTHROPIC_API_KEY`, `SUPADATA_API_KEY` |
| `list_channel_videos` | Fetch recent videos from a YouTube channel                                | `YOUTUBE_API_KEY`                       |
| `sync_to_github`      | Push analyses as markdown files to a GitHub repo                          | `GITHUB_TOKEN`, `GITHUB_REPO`           |
| `analyse_x_feed`      | Analyse recent posts from curated X accounts — daily digest               | `X_BEARER_TOKEN`                        |
| `generate_image`      | Generate comic-book infographic from analysis result                      | `GEMINI_API_KEY`                        |

## Environment Variables

All prefixed with `MCP_CP_`:

| Variable                       | Required        | Description                                                         |
| ------------------------------ | --------------- | ------------------------------------------------------------------- |
| `MCP_CP_ANTHROPIC_API_KEY`     | Yes             | Anthropic API key for Claude analysis                               |
| `MCP_CP_SUPADATA_API_KEY`      | Yes for YouTube | Supadata API key for YouTube transcript extraction                  |
| `MCP_CP_YOUTUBE_API_KEY`       | No              | YouTube Data API v3 key (only for `list_channel_videos`)            |
| `MCP_CP_GITHUB_TOKEN`          | For sync        | GitHub personal access token                                        |
| `MCP_CP_GITHUB_REPO`           | For sync        | Target repo in `owner/repo` format                                  |
| `MCP_CP_GITHUB_BRANCH`         | No              | Branch to push to (default: `main`)                                 |
| `MCP_CP_GITHUB_OUTPUT_DIR`     | No              | Output directory for YouTube analyses (default: `content/youtube`)  |
| `MCP_CP_GITHUB_X_OUTPUT_DIR`   | No              | Output directory for X digests (default: `content/x-digest`)        |
| `MCP_CP_IMAGE_OUTPUT_DIR`      | No              | Directory for generated images (default: `~/Downloads`)             |
| `MCP_CP_CLAUDE_MODEL`          | No              | Claude model to use (default: `claude-sonnet-4-20250514`)           |
| `MCP_CP_MAX_TRANSCRIPT_TOKENS` | No              | Max transcript length in tokens (default: `100000`)                 |
| `MCP_CP_GEMINI_API_KEY`        | For image       | Google AI Studio API key for image generation                       |
| `MCP_CP_GEMINI_MODEL`          | No              | Gemini model for images (default: `gemini-3.1-flash-image-preview`) |
| `MCP_CP_X_BEARER_TOKEN`        | For X digest    | X API v2 bearer token                                               |
| `MCP_CP_X_ACCOUNTS`            | For X digest    | Comma-separated X usernames                                         |
| `MCP_CP_X_TOPICS`              | No              | Comma-separated topics (default: AI,tech)                           |

## Cost Projections

Estimated monthly costs for two usage patterns:

| Service                       | Daily (every day)       | Weekly X + daily YouTube |
| ----------------------------- | ----------------------- | ------------------------ |
| YouTube analysis (Claude API) | ~$3–5/mo (1 video/day)  | ~$3–5/mo (1 video/day)   |
| X feed digest (Claude API)    | ~$2–3/mo                | ~$0.50/mo                |
| Image generation (Gemini API) | ~$2/mo ($0.067/image)   | ~$2/mo ($0.067/image)    |
| X API reads                   | ~$4/mo ($0.13/day)      | ~$0.60/mo ($0.15/week)   |
| Supadata transcript API       | ~$0 (free tier: 100/mo) | ~$0 (free tier: 100/mo)  |
| **Total (excl. Claude API)**  | **~$6–9/mo**            | **~$3–5/mo**             |

> Claude API costs depend on your Anthropic billing plan and are not included in the totals above. If you already use Claude Pro ($20/mo), there is no additional Claude cost. The X API spending cap can be configured in the [developer console](https://developer.x.com/).

### What this replaces

| Subscription          | Monthly cost | What the pipeline covers instead                           |
| --------------------- | ------------ | ---------------------------------------------------------- |
| Google One AI Premium  | ~$20/mo     | Image generation via Gemini API (~$2/mo)                   |
| X Premium              | ~$8/mo      | X feed reading via API (~$0.60–4/mo)                       |
| YouTube Premium        | ~$14/mo     | Transcript extraction via Supadata (free tier)             |
| **Total saved**        | **~$42/mo** | **Pipeline cost: ~$3–9/mo** (plus your existing Claude plan) |

## Eval Gates

Prompt and model changes are automatically evaluated in CI using [mcp-llm-eval](https://github.com/berkayildi/mcp-llm-eval). The eval dataset covers both YouTube analysis and X feed digest prompts, benchmarking Claude Sonnet and Gemini 2.5 Flash on the same test cases. PRs that touch system prompts or model config trigger an evaluation run that scores faithfulness and relevance against a reference dataset. The PR is blocked if quality regresses below configured thresholds.

See `.eval-gate.yml` for threshold configuration and `eval/dataset.json` for the test dataset.

### Running benchmarks locally

The benchmark requires API keys for all providers. Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
```

Then run:

```bash
make benchmark        # Run eval against all 5 models
make benchmark-copy   # Copy results to llm-benchmarks repo
```

Results are written to `eval/results/` (gitignored). The benchmark output feeds into [LLMShot](https://llmshot.vercel.app) via the [llm-benchmarks](https://github.com/berkayildi/llm-benchmarks) repo at `text-generation/content-pipeline-summary.json` and `text-generation/content-pipeline-benchmark.json`.

The model used in the production pipeline is Claude Sonnet (`claude-sonnet-4-6`), configured via `MCP_CP_ANTHROPIC_API_KEY`. The benchmark tests all 5 models against the same prompts to track quality and cost across providers.

## Development

```bash
git clone https://github.com/your-username/mcp-content-pipeline.git
cd mcp-content-pipeline
uv sync
uv run pytest -v --cov=src/mcp_content_pipeline
uv run ruff check src/ tests/
```

## Security

- All credentials are configured via local environment variables — never committed to the repo
- The tool is open source but your API keys, YouTube key, and GitHub token stay on your machine
- **Never** create a `.env` file in the repo — use shell exports or Claude Desktop config instead

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Commit using [Conventional Commits](https://www.conventionalcommits.org/) (`feat: add new feature`)
4. Push and open a Pull Request

## License

[MIT](LICENSE)
