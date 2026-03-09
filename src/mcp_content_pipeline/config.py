"""Settings via environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    youtube_api_key: str | None = None
    github_token: str = ""
    github_repo: str = ""  # format: "owner/repo"
    github_branch: str = "main"
    github_output_dir: str = "content/videos"
    claude_model: str = "claude-sonnet-4-20250514"
    max_transcript_tokens: int = 100000
    youtube_cookies_file: str | None = None

    model_config = SettingsConfigDict(env_prefix="MCP_CP_")


def get_settings() -> Settings:
    return Settings()
