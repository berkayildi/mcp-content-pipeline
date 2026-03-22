"""Gemini API client for image generation."""

from __future__ import annotations

import os
import tempfile
from datetime import datetime

from google import genai
from google.genai import types
from google.genai.errors import APIError
from slugify import slugify

from mcp_content_pipeline.models.schemas import ImageGenerationResult, VideoAnalysis


def build_image_prompt(analysis: VideoAnalysis) -> str:
    """Construct a detailed image generation prompt from a video analysis."""
    takeaways = analysis.key_takeaways[:6]
    numbered = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(takeaways))
    topics = ", ".join(analysis.topics)

    return f"""Create a comic-book style infographic illustration summarising these news stories.
Use bold colours, clear panel divisions, text labels on each panel, and visual metaphors.
Style: editorial illustration, Bloomberg-style, professional but visually striking.
Orientation: landscape, 16:9 aspect ratio.

Stories to illustrate (one panel per story, max 6 panels):
{numbered}

Title: {analysis.title}
Topics: {topics}

Requirements:
- Each panel has a SHORT bold text label (2-5 words)
- Use recognisable visual metaphors (e.g., dragon for China, rocket for SpaceX, bull/bear for markets)
- No real human faces — use silhouettes or symbols instead
- Bold, saturated colours with thick outlines
- Comic-book panel borders separating each story"""


async def generate_image(api_key: str, model: str, analysis: VideoAnalysis) -> ImageGenerationResult:
    """Generate a comic-book infographic image from a video analysis using Gemini."""
    client = genai.Client(api_key=api_key)
    prompt = build_image_prompt(analysis)

    try:
        response = await client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio="16:9",
                ),
            ),
        )
    except APIError as e:
        raise RuntimeError(f"Gemini API error: {e}") from e

    image_data = None
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image_data = part.inline_data.data
            break

    if image_data is None:
        raise RuntimeError("Gemini API returned no image data")

    temp_dir = tempfile.gettempdir()
    slug = slugify(analysis.title, max_length=80)
    date_str = datetime.now().strftime("%Y-%m-%d")
    image_path = os.path.join(temp_dir, f"{date_str}-{slug}.png")

    with open(image_path, "wb") as f:
        f.write(image_data)

    return ImageGenerationResult(
        image_path=image_path,
        prompt_used=prompt,
        analysis_title=analysis.title,
    )
