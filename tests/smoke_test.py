from __future__ import annotations

import asyncio
import os
import threading
import time

from tests.mock_upstream import HOST, PORT, serve


async def main() -> None:
    os.environ["OPENAI_MCP_UPSTREAM_BASE_URL"] = f"http://{HOST}:{PORT}/v1"
    os.environ["OPENAI_MCP_MODEL"] = "mock-model"

    threading.Thread(target=serve, daemon=True).start()
    time.sleep(0.2)

    from openai_mcp_bridge.bridge import ask_upstream, upstream_health

    health = await upstream_health()
    answer = await ask_upstream("hello")
    assert "HTTP 200" in health
    assert answer == "MOCK_OK: hello"
    print("SMOKE_TEST_PASS")


if __name__ == "__main__":
    asyncio.run(main())
