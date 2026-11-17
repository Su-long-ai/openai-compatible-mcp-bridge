from __future__ import annotations

import os
from typing import Any

import httpx


def _env(name: str, default: str = "") -> str:
    value = os.getenv(name)
    return value.strip() if value and value.strip() else default


def upstream_base_url() -> str:
    return _env("OPENAI_MCP_UPSTREAM_BASE_URL", "http://127.0.0.1:8080/v1").rstrip("/")


def upstream_api_key() -> str:
    return _env("OPENAI_MCP_UPSTREAM_API_KEY")


def default_model() -> str:
    return _env("OPENAI_MCP_MODEL", "default")


def timeout_seconds() -> float:
    try:
        return float(_env("OPENAI_MCP_TIMEOUT_SECONDS", "180"))
    except ValueError:
        return 180.0


async def ask_upstream(prompt: str, *, system_prompt: str = "", model: str = "") -> str:
    prompt = prompt.strip()
    if not prompt:
        raise ValueError("prompt must not be empty")

    messages: list[dict[str, str]] = []
    if system_prompt.strip():
        messages.append({"role": "system", "content": system_prompt.strip()})
    messages.append({"role": "user", "content": prompt})

    payload: dict[str, Any] = {
        "model": model.strip() or default_model(),
        "messages": messages,
        "stream": False,
    }
    headers = {"Content-Type": "application/json"}
    if upstream_api_key():
        headers["Authorization"] = f"Bearer {upstream_api_key()}"

    async with httpx.AsyncClient(timeout=timeout_seconds()) as client:
        response = await client.post(
            f"{upstream_base_url()}/chat/completions",
            json=payload,
            headers=headers,
        )

    if response.is_error:
        raise RuntimeError(
            f"upstream returned HTTP {response.status_code}: {response.text[:2000]}"
        )

    try:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("upstream response is not OpenAI chat-completions compatible") from exc

    if not isinstance(content, str):
        raise RuntimeError("upstream message content is not a string")
    return content


async def upstream_health() -> str:
    headers = {}
    if upstream_api_key():
        headers["Authorization"] = f"Bearer {upstream_api_key()}"

    async with httpx.AsyncClient(timeout=min(timeout_seconds(), 15.0)) as client:
        response = await client.get(f"{upstream_base_url()}/models", headers=headers)

    return f"HTTP {response.status_code}: {response.text[:1000]}"
