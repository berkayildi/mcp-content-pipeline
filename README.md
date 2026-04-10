# mcp-content-pipeline

[![PyPI version](https://img.shields.io/pypi/v/mcp-content-pipeline)](https://pypi.org/project/mcp-content-pipeline/)
[![Downloads](https://img.shields.io/pypi/dm/mcp-content-pipeline)](https://pypi.org/project/mcp-content-pipeline/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/pypi/pyversions/mcp-content-pipeline)](https://pypi.org/project/mcp-content-pipeline/)

A YouTube video analysis and X feed digest pipeline exposed as [MCP](https://modelcontextprotocol.io/) tools. Extract transcripts, generate key takeaways, TLDRs, and Twitter/X hook drafts — plus daily X feed digests from curated accounts — all callable by any MCP-compatible AI client like Claude Desktop.

## Why?

Manually copying YouTube transcripts into AI tools, crafting prompts, and formatting output is tedious and error-prone. This MCP server turns the entire workflow into chainable tools that any AI agent can call. List videos from a channel, analyse them in batch, and sync the results to GitHub — all in a single conversation.

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
        "MCP_CP_GITHUB_TOKEN": "ghp_...",
        "MCP_CP_GITHUB_REPO": "your-username/your-repo",
        "MCP_CP_GEMINI_API_KEY": "your-gemini-api-key"
      }
    }
  }
}
```

## Usage

Once configured in Claude Desktop, chain the tools in a single conversation:

**Step 1 — Analyse**
> "Analyse this video: https://www.youtube.com/watch?v=..."

**Step 2 — Generate image**
> "Generate an image for this analysis"

**Step 3 — Sync to GitHub**
> "Sync the analysis and image to GitHub"

Or do it all in one prompt:
> "Analyse this video, generate the image, and sync to GitHub: https://www.youtube.com/watch?v=..."

**X Feed Digest**
> "Analyse what karpathy, garrytan, and elvissun posted about AI today"

Or with the full pipeline:
> "Analyse the X feed, generate the image, and sync to GitHub"

## Tools

| Tool                  | Description                                                                | Requires                      |
| --------------------- | -------------------------------------------------------------------------- | ----------------------------- |
| `analyse_video`       | Analyse a single YouTube video — transcript, takeaways, TLDR, Twitter hook | `ANTHROPIC_API_KEY`           |
| `batch_analyse`       | Analyse multiple videos from a URL list or config file                     | `ANTHROPIC_API_KEY`           |
| `list_channel_videos` | Fetch recent videos from a YouTube channel                                 | `YOUTUBE_API_KEY`             |
| `sync_to_github`      | Push analyses as markdown files to a GitHub repo                           | `GITHUB_TOKEN`, `GITHUB_REPO` |
| `analyse_x_feed`      | Analyse recent posts from curated X accounts — daily digest                | `X_BEARER_TOKEN`              |
| `generate_image`      | Generate comic-book infographic from analysis result                       | `GEMINI_API_KEY`              |

## Environment Variables

All prefixed with `MCP_CP_`:

| Variable                       | Required | Description                                               |
| ------------------------------ | -------- | --------------------------------------------------------- |
| `MCP_CP_ANTHROPIC_API_KEY`     | Yes      | Anthropic API key for Claude analysis                     |
| `MCP_CP_YOUTUBE_API_KEY`       | No       | YouTube Data API v3 key (only for `list_channel_videos`)  |
| `MCP_CP_GITHUB_TOKEN`          | For sync | GitHub personal access token                              |
| `MCP_CP_GITHUB_REPO`           | For sync | Target repo in `owner/repo` format                        |
| `MCP_CP_GITHUB_BRANCH`         | No       | Branch to push to (default: `main`)                       |
| `MCP_CP_GITHUB_OUTPUT_DIR`     | No       | Output directory in repo (default: `content/videos`)      |
| `MCP_CP_CLAUDE_MODEL`          | No       | Claude model to use (default: `claude-sonnet-4-20250514`) |
| `MCP_CP_MAX_TRANSCRIPT_TOKENS` | No       | Max transcript length in tokens (default: `100000`)       |
| `MCP_CP_GEMINI_API_KEY`        | For image | Google AI Studio API key for image generation             |
| `MCP_CP_GEMINI_MODEL`          | No        | Gemini model for images (default: `gemini-3.1-flash-image-preview`) |
| `MCP_CP_X_BEARER_TOKEN`       | For X digest | X API v2 bearer token                                  |
| `MCP_CP_X_ACCOUNTS`           | For X digest | Comma-separated X usernames                            |
| `MCP_CP_X_TOPICS`             | No           | Comma-separated topics (default: AI,tech)              |

## Cost Projections

Estimated monthly costs for two usage patterns:

| Service                        | Daily (every day)       | Weekly X + daily YouTube |
| ------------------------------ | ----------------------- | ------------------------ |
| YouTube analysis (Claude API)  | ~$3–5/mo (1 video/day) | ~$3–5/mo (1 video/day)   |
| X feed digest (Claude API)     | ~$2–3/mo               | ~$0.50/mo                |
| Image generation (Gemini API)  | ~$2/mo ($0.067/image)  | ~$2/mo ($0.067/image)    |
| X API reads                    | ~$4/mo ($0.13/day)     | ~$0.60/mo ($0.15/week)   |
| **Total**                      | **~$11–14/mo**         | **~$6–8/mo**             |

> Claude API costs depend on your Anthropic billing plan and are separate from the X API and Gemini totals shown above. The X API spending cap can be configured in the [developer console](https://developer.x.com/).

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
