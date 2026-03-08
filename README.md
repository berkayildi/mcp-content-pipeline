# mcp-content-pipeline

[![PyPI version](https://img.shields.io/pypi/v/mcp-content-pipeline)](https://pypi.org/project/mcp-content-pipeline/)
[![Python](https://img.shields.io/pypi/pyversions/mcp-content-pipeline)](https://pypi.org/project/mcp-content-pipeline/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A YouTube video analysis and content generation pipeline exposed as [MCP](https://modelcontextprotocol.io/) tools. Extract transcripts, generate key takeaways, TLDRs, and Twitter/X hook drafts — all callable by any MCP-compatible AI client like Claude Desktop.

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
        "MCP_CP_GITHUB_REPO": "your-username/your-repo"
      }
    }
  }
}
```

## Tools

| Tool | Description | Requires |
|------|-------------|----------|
| `analyse_video` | Analyse a single YouTube video — transcript, takeaways, TLDR, Twitter hook | `ANTHROPIC_API_KEY` |
| `batch_analyse` | Analyse multiple videos from a URL list or config file | `ANTHROPIC_API_KEY` |
| `list_channel_videos` | Fetch recent videos from a YouTube channel | `YOUTUBE_API_KEY` |
| `sync_to_github` | Push analyses as markdown files to a GitHub repo | `GITHUB_TOKEN`, `GITHUB_REPO` |

## Environment Variables

All prefixed with `MCP_CP_`:

| Variable | Required | Description |
|----------|----------|-------------|
| `MCP_CP_ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude analysis |
| `MCP_CP_YOUTUBE_API_KEY` | No | YouTube Data API v3 key (only for `list_channel_videos`) |
| `MCP_CP_GITHUB_TOKEN` | For sync | GitHub personal access token |
| `MCP_CP_GITHUB_REPO` | For sync | Target repo in `owner/repo` format |
| `MCP_CP_GITHUB_BRANCH` | No | Branch to push to (default: `main`) |
| `MCP_CP_GITHUB_OUTPUT_DIR` | No | Output directory in repo (default: `content/videos`) |
| `MCP_CP_CLAUDE_MODEL` | No | Claude model to use (default: `claude-sonnet-4-20250514`) |
| `MCP_CP_MAX_TRANSCRIPT_TOKENS` | No | Max transcript length in tokens (default: `100000`) |

## Example Workflow

Chain tools together in a single conversation:

```
1. "List the last 5 videos from channel UC_x5XG1OV2P6uZZ5FSM9Ttw"
   → list_channel_videos returns 5 video URLs

2. "Analyse all of these videos"
   → batch_analyse processes all 5, returns analyses

3. "Sync the results to GitHub"
   → sync_to_github pushes markdown files + index to your repo
```

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
