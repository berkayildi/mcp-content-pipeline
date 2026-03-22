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
    image_base64: str
    prompt_used: str
    analysis_title: str


class SyncResult(BaseModel):
    files: list[SyncFileResult]
    commit_sha: str | None = None
    index_path: str | None = None
    image_files: list[SyncFileResult] = Field(default_factory=list)


# Rebuild BatchAnalysisResult to resolve forward reference
BatchAnalysisResult.model_rebuild()
