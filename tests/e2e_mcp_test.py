from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import threading

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from tests.mock_upstream import HOST, PORT, serve


async def main() -> None:
    env = os.environ.copy()
    repo_root = os.path.dirname(os.path.dirname(__file__))
    src = os.path.join(repo_root, "src")
    env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")
    env["OPENAI_MCP_UPSTREAM_BASE_URL"] = f"http://{HOST}:{PORT}/v1"
    env["OPENAI_MCP_MODEL"] = "mock-model"
    env["OPENAI_MCP_HOST"] = "127.0.0.1"
    env["OPENAI_MCP_PORT"] = "18787"

    threading.Thread(target=serve, daemon=True).start()

    proc = subprocess.Popen(
        [sys.executable, "-m", "openai_mcp_bridge.server"],
        cwd=repo_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        await asyncio.sleep(1.0)
        async with streamablehttp_client("http://127.0.0.1:18787/mcp") as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools = await session.list_tools()
                names = {tool.name for tool in tools.tools}
                assert {"bridge_ask", "bridge_health"} <= names

                result = await session.call_tool("bridge_ask", {"prompt": "hello through MCP"})
                texts = [x.text for x in result.content if getattr(x, "type", None) == "text"]
                assert texts and "MOCK_OK: hello through MCP" in texts[0]

                health = await session.call_tool("bridge_health", {})
                texts = [x.text for x in health.content if getattr(x, "type", None) == "text"]
                assert texts and "HTTP 200" in texts[0]

        print("MCP_E2E_PASS")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


if __name__ == "__main__":
    asyncio.run(main())
