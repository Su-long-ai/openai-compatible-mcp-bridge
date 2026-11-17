from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from .bridge import ask_upstream, upstream_health


def _port() -> int:
    try:
        return int(os.getenv("OPENAI_MCP_PORT", "8787"))
    except ValueError:
        return 8787


mcp = FastMCP(
    "openai-compatible-bridge",
    instructions="Bridge MCP tool calls to a configured OpenAI-compatible upstream.",
    host=os.getenv("OPENAI_MCP_HOST", "127.0.0.1"),
    port=_port(),
    streamable_http_path="/mcp",
    json_response=True,
    stateless_http=True,
)


@mcp.tool()
async def bridge_ask(prompt: str, system_prompt: str = "", model: str = "") -> str:
    """Send one prompt to the configured OpenAI-compatible upstream."""
    return await ask_upstream(prompt, system_prompt=system_prompt, model=model)


@mcp.tool()
async def bridge_health() -> str:
    """Check whether the configured upstream responds on /v1/models."""
    return await upstream_health()


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
