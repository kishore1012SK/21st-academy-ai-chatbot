"""
Direct client for Ollama's REST API. No third-party AI provider is ever
contacted — every call in this file goes to settings.OLLAMA_BASE_URL, which
defaults to http://localhost:11434 and can later point at a private Linux
server with zero frontend changes.
"""
import json
import asyncio
import httpx
from typing import AsyncGenerator, List, Dict
from config import settings


class OllamaError(Exception):
    pass


async def _post_with_retries(client: httpx.AsyncClient, url: str, payload: dict):
    last_exc = None
    for attempt in range(settings.OLLAMA_MAX_RETRIES + 1):
        try:
            resp = await client.post(url, json=payload, timeout=settings.OLLAMA_TIMEOUT)
            resp.raise_for_status()
            return resp
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.HTTPStatusError) as exc:
            last_exc = exc
            if attempt < settings.OLLAMA_MAX_RETRIES:
                await asyncio.sleep(0.5 * (attempt + 1))  # backoff
            continue
    raise OllamaError(f"Ollama unreachable after retries: {last_exc}")


async def check_health() -> bool:
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5)
            return resp.status_code == 200
    except Exception:
        return False


def _build_messages(history: List[Dict[str, str]], user_message: str, context: str = "") -> list:
    messages = [{"role": "system", "content": settings.SYSTEM_PROMPT}]
    if context:
        messages.append({
            "role": "system",
            "content": f"Reference material retrieved from uploaded documents:\n\n{context}"
        })
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    return messages


async def chat_completion(history: List[Dict[str, str]], user_message: str, context: str = "") -> str:
    """Non-streaming chat completion. Returns full text response."""
    payload = {
        "model": settings.OLLAMA_CHAT_MODEL,
        "messages": _build_messages(history, user_message, context),
        "stream": False,
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await _post_with_retries(client, f"{settings.OLLAMA_BASE_URL}/api/chat", payload)
        except OllamaError:
            raise
        data = resp.json()
        return data.get("message", {}).get("content", "").strip()


async def chat_completion_stream(
    history: List[Dict[str, str]], user_message: str, context: str = ""
) -> AsyncGenerator[str, None]:
    """Yields response text tokens as they stream from Ollama (Server-Sent chunks)."""
    payload = {
        "model": settings.OLLAMA_CHAT_MODEL,
        "messages": _build_messages(history, user_message, context),
        "stream": True,
    }
    attempt = 0
    while True:
        try:
            async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT) as client:
                async with client.stream(
                    "POST", f"{settings.OLLAMA_BASE_URL}/api/chat", json=payload
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            chunk = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        token = chunk.get("message", {}).get("content", "")
                        if token:
                            yield token
                        if chunk.get("done"):
                            return
            return
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.HTTPStatusError) as exc:
            attempt += 1
            if attempt > settings.OLLAMA_MAX_RETRIES:
                yield "\n\n[Error: could not reach the AI model. Please try again shortly or contact admin@21stacademy.in]"
                return
            await asyncio.sleep(0.5 * attempt)


async def embed_text(text: str) -> List[float]:
    payload = {"model": settings.OLLAMA_EMBED_MODEL, "prompt": text}
    async with httpx.AsyncClient() as client:
        resp = await _post_with_retries(client, f"{settings.OLLAMA_BASE_URL}/api/embeddings", payload)
        data = resp.json()
        return data.get("embedding", [])
