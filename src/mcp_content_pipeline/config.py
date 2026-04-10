"""Settings via environment variables."""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    youtube_api_key: str | None = None
    github_token: str = ""
    github_repo: str = ""  # format: "owner/repo"
    github_branch: str = "main"
    github_output_dir: str = "content/videos"
    claude_model: str = "claude-sonnet-4-20250514"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.1-flash-image-preview"
    max_transcript_tokens: int = 100000
    youtube_cookies_file: str | None = None
    x_bearer_token: str = ""
    x_accounts: list[str] = []
    x_topics: list[str] = []

    model_config = SettingsConfigDict(env_prefix="MCP_CP_")

    @field_validator("x_accounts", mode="before")
    @classmethod
    def _split_x_accounts(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()] if v else []
        return v

    @field_validator("x_topics", mode="before")
    @classmethod
    def _split_x_topics(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()] if v else []
        return v


def get_settings() -> Settings:
    return Settings()
