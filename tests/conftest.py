"""Shared fixtures for tests."""

from __future__ import annotations

import json

import pytest

from mcp_content_pipeline.config import Settings
from mcp_content_pipeline.models.schemas import VideoAnalysis


@pytest.fixture
def sample_transcript():
    return (
        "Welcome to today's video about machine learning in production. "
        "One of the biggest challenges teams face is the gap between training a model "
        "and deploying it reliably. In this video, we'll cover three key strategies. "
        "First, always version your models alongside your code. This ensures reproducibility. "
        "Second, implement shadow deployments before going live. Run your new model alongside "
        "the old one and compare outputs. Third, monitor data drift continuously. "
        "Your model is only as good as the data it sees, and production data shifts over time. "
        "Many teams underestimate the importance of feature stores. A centralized feature store "
        "ensures consistency between training and serving. "
        "Let me share a real example from our work at a fintech company. They reduced model "
        "incidents by 73% just by implementing these three practices. "
        "The most surprising finding was that shadow deployments caught issues that unit tests "
        "completely missed. Remember: your model in production IS the product."
    )


@pytest.fixture
def sample_video_metadata():
    return {
        "title": "ML in Production: 3 Strategies That Actually Work",
        "channel": "Tech Engineering Hub",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "duration": "PT15M30S",
    }


@pytest.fixture
def sample_analysis_result():
    return VideoAnalysis(
        title="ML in Production: 3 Strategies That Actually Work",
        channel="Tech Engineering Hub",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        date_analysed="2026-03-08T12:00:00",
        key_takeaways=[
            "Version models alongside code for reproducibility",
            "Use shadow deployments before going live with new models",
            "Monitor data drift continuously in production",
            "Feature stores ensure consistency between training and serving",
            "Shadow deployments catch issues that unit tests miss",
        ],
        tldr=(
            "Deploy ML models reliably by versioning them with code, running shadow deployments, "
            "and monitoring data drift. A fintech company reduced model incidents by 73% with these practices."
        ),
        twitter_hook=(
            "Shadow deployments catch ML bugs that unit tests completely miss. "
            "One fintech cut model incidents by 73% with 3 simple practices "
            "#MLOps #MachineLearning #AI"
        ),
        topics=["MLOps", "Machine Learning", "Production Engineering", "DevOps"],
    )


@pytest.fixture
def mock_anthropic_response(sample_analysis_result):
    """Mocked Claude API response."""
    return json.dumps(sample_analysis_result.model_dump())


@pytest.fixture
def settings():
    return Settings(
        anthropic_api_key="test-api-key",
        youtube_api_key="test-youtube-key",
        github_token="test-github-token",
        github_repo="owner/repo",
    )


@pytest.fixture
def sample_image_base64():
    # Minimal valid 1x1 red PNG
    import base64

    png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
        b"\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00"
        b"\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    return base64.b64encode(png_bytes).decode("utf-8")
