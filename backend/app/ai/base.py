import asyncio
from collections.abc import AsyncGenerator, Generator

from openai import OpenAI

from app.core.config import settings

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.DEEPSEEK_API_KEY, base_url=settings.DEEPSEEK_BASE_URL)
    return _client


def chat_stream(
    messages: list[dict[str, str]],
    model: str = "deepseek-chat",
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> Generator[str, None, None]:
    client = get_client()
    for attempt in range(3):
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content
            return
        except Exception as e:
            if attempt == 2:
                raise
            import time
            time.sleep(2**attempt)


def chat(
    messages: list[dict[str, str]],
    model: str = "deepseek-chat",
    temperature: float | None = 0.7,
    max_tokens: int = 4096,
    max_retries: int = 3,
    response_format: dict | None = None,
) -> str:
    client = get_client()
    for attempt in range(max_retries):
        try:
            kwargs = dict(model=model, messages=messages, max_tokens=max_tokens, stream=False)
            if temperature is not None:
                kwargs["temperature"] = temperature
            if response_format is not None:
                kwargs["response_format"] = response_format
            response = client.chat.completions.create(**kwargs, timeout=90)
            return response.choices[0].message.content or ""
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            import time
            time.sleep(2**attempt)


def chat_reasoner(
    messages: list[dict[str, str]],
    max_tokens: int = 8192,
) -> str:
    """Use deepseek-reasoner (or fallback to deepseek-chat) for deep analysis tasks."""
    try:
        # Don't pass temperature to reasoner model (not supported)
        return chat(messages, model="deepseek-reasoner", temperature=None, max_tokens=max_tokens, max_retries=1)
    except Exception:
        return chat(messages, model="deepseek-chat", temperature=0.3, max_tokens=max_tokens, max_retries=1)
