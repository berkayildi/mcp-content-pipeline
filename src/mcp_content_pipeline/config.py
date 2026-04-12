"""Settings via environment variables."""

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _split_csv(v: str | list[str]) -> list[str]:
    """Split a comma-separated string into a list of strings."""
    if isinstance(v, str):
        return [s.strip() for s in v.split(",") if s.strip()] if v else []
    return list(v)


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    youtube_api_key: str | None = None
    github_token: str = ""
    github_repo: str = ""  # format: "owner/repo"
    github_branch: str = "main"
    github_output_dir: str = "content/youtube"
    github_x_output_dir: str = "content/x-digest"
    claude_model: str = "claude-sonnet-4-20250514"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.1-flash-image-preview"
    image_output_dir: str = ""
    max_transcript_tokens: int = 100000
    supadata_api_key: str = ""
    x_bearer_token: str = ""
    x_accounts: str | list[str] = []
    x_topics: str | list[str] = []

    model_config = SettingsConfigDict(env_prefix="MCP_CP_")

    @model_validator(mode="after")
    def _split_csv_fields(self) -> "Settings":
        self.x_accounts = _split_csv(self.x_accounts)
        self.x_topics = _split_csv(self.x_topics)
        return self


def get_settings() -> Settings:
    return Settings()
