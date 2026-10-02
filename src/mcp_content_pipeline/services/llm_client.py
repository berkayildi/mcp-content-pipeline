"""Provider-agnostic text-completion client — the analysis "driver".

Backs analyse_video, batch_analyse, and analyse_x_feed. Swapping
MCP_CP_PIPELINE_PROVIDER (anthropic | openai | google) changes which API
MCP_CP_PIPELINE_API_KEY and MCP_CP_PIPELINE_MODEL are sent to; the calling
code and prompts stay identical.
"""

from __future__ import annotations

SUPPORTED_PROVIDERS = ("anthropic", "openai", "google")


async def complete(
    provider: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 4096,
) -> str:
    """Send a system+user prompt to the configured provider and return the raw text reply."""
    provider = provider.strip().lower()

    if provider == "anthropic":
        return await _complete_anthropic(api_key, model, system_prompt, user_prompt, max_tokens)
    if provider == "openai":
        return await _complete_openai(api_key, model, system_prompt, user_prompt, max_tokens)
    if provider == "google":
        return await _complete_google(api_key, model, system_prompt, user_prompt, max_tokens)

    raise ValueError(
        f"Unsupported MCP_CP_PIPELINE_PROVIDER '{provider}'. "
        f"Supported: {', '.join(SUPPORTED_PROVIDERS)}"
    )


async def _complete_anthropic(
    api_key: str, model: str, system_prompt: str, user_prompt: str, max_tokens: int
) -> str:
    import anthropic

    client = anthropic.AsyncAnthropic(api_key=api_key)
    message = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


async def _complete_openai(
    api_key: str, model: str, system_prompt: str, user_prompt: str, max_tokens: int
) -> str:
    import openai

    client = openai.AsyncOpenAI(api_key=api_key)
    response = await client.chat.completions.create(
        model=model,
        max_completion_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


async def _complete_google(
    api_key: str, model: str, system_prompt: str, user_prompt: str, max_tokens: int
) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    response = await client.aio.models.generate_content(
        model=model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=max_tokens,
        ),
    )
    return response.text
