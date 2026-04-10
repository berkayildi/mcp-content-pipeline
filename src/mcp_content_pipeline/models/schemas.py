"""Pydantic models for all data."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class VideoMetadata(BaseModel):
    title: str
    channel: str
    url: str
    duration: str | None = None
    publish_date: str | None = None


class VideoAnalysis(BaseModel):
    title: str
    channel: str
    url: str
    date_analysed: str = Field(default_factory=lambda: datetime.now().isoformat())
    key_takeaways: list[str]
    tldr: str
    twitter_hook: str
    topics: list[str]


class BatchAnalysisResult(BaseModel):
    successes: list[VideoAnalysis] = Field(default_factory=list)
    failures: list[BatchFailure] = Field(default_factory=list)


class BatchFailure(BaseModel):
    url: str
    error: str


class ChannelVideo(BaseModel):
    video_id: str
    title: str
    url: str
    published_at: str


class ChannelVideosResult(BaseModel):
    channel_id: str
    videos: list[ChannelVideo]


class SyncFileResult(BaseModel):
    path: str
    action: str  # "created" or "updated"


class ImageGenerationResult(BaseModel):
    image_path: str
    prompt_used: str
    analysis_title: str


class SyncResult(BaseModel):
    files: list[SyncFileResult]
    commit_sha: str | None = None
    index_path: str | None = None
    image_files: list[SyncFileResult] = Field(default_factory=list)


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


class XNotablePost(BaseModel):
    """A post highlighted as particularly noteworthy."""

    author_username: str
    text: str
    url: str
    why_notable: str


class XDigestAnalysis(BaseModel):
    """Claude-generated digest of X feed posts."""

    title: str
    date_analysed: str = Field(default_factory=lambda: datetime.now().isoformat())
    accounts: list[str]
    topics: list[str]
    key_takeaways: list[str]
    tldr: str
    twitter_hook: str
    notable_posts: list[XNotablePost] = Field(default_factory=list)
    post_count: int = 0
    source: str = "x_feed"


# Rebuild models with forward references
BatchAnalysisResult.model_rebuild()
XFeedFetchResult.model_rebuild()
XDigestAnalysis.model_rebuild()
