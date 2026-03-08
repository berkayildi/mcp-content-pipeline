"""YouTube Data API v3 client for channel video listing."""

from __future__ import annotations

from googleapiclient.discovery import build

from mcp_content_pipeline.models.schemas import ChannelVideo, ChannelVideosResult


async def list_channel_videos(
    api_key: str,
    channel_id: str,
    max_results: int = 10,
    published_after: str | None = None,
) -> ChannelVideosResult:
    """Fetch recent videos from a YouTube channel using the Data API v3."""
    youtube = build("youtube", "v3", developerKey=api_key)

    search_params: dict = {
        "channelId": channel_id,
        "order": "date",
        "type": "video",
        "part": "snippet",
        "maxResults": min(max_results, 50),
    }
    if published_after:
        search_params["publishedAfter"] = published_after

    request = youtube.search().list(**search_params)
    response = request.execute()

    videos = []
    for item in response.get("items", []):
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        videos.append(
            ChannelVideo(
                video_id=video_id,
                title=snippet["title"],
                url=f"https://www.youtube.com/watch?v={video_id}",
                published_at=snippet["publishedAt"],
            )
        )

    return ChannelVideosResult(channel_id=channel_id, videos=videos)
