"""Pydantic models for all data."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class VideoAnalysis(BaseModel):
    title: str
    channel: str
    url: str
    date_analysed: str = Field(default_factory=lambda: datetime.now().isoformat())
    key_takeaways: list[str]
    tldr: str
    topics: list[str]


class SyncFileResult(BaseModel):
    path: str
    action: str  # "created" or "updated"


class SyncResult(BaseModel):
    files: list[SyncFileResult]
    commit_sha: str | None = None
    index_path: str | None = None


class XPost(BaseModel):
    """A single post from X."""

    id: str
    text: str
    author_username: str
    author_name: str
    created_at: str
    url: str
    retweet_count: int = 0
    like_count: int = 0
    reply_count: int = 0
    quote_count: int = 0
    is_retweet: bool = False
    is_reply: bool = False


class XFeedFailure(BaseModel):
    username: str
    error: str


class XFeedFetchResult(BaseModel):
    """Raw fetch result from X API before analysis."""

    accounts: list[str]
    posts: list[XPost] = Field(default_factory=list)
    failures: list[XFeedFailure] = Field(default_factory=list)
    fetched_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class XDigestAnalysis(BaseModel):
    """LLM-generated digest of X feed posts."""

    title: str
    date_analysed: str = Field(default_factory=lambda: datetime.now().isoformat())
    accounts: list[str]
    topics: list[str]
    key_takeaways: list[str]
    tldr: str
    post_count: int = 0
    source: str = "x_feed"

