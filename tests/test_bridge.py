from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from openai_mcp_bridge.bridge import ask_upstream, default_model, timeout_seconds


class BridgeValidationTests(unittest.IsolatedAsyncioTestCase):
    async def test_empty_prompt_is_rejected_before_network(self):
        with self.assertRaisesRegex(ValueError, "prompt"):
            await ask_upstream("   ")

    def test_default_model_uses_configured_value(self):
        with patch.dict(os.environ, {"OPENAI_MCP_MODEL": "local-model"}, clear=False):
            self.assertEqual(default_model(), "local-model")

    def test_invalid_timeout_falls_back(self):
        with patch.dict(os.environ, {"OPENAI_MCP_TIMEOUT_SECONDS": "not-a-number"}, clear=False):
            self.assertEqual(timeout_seconds(), 180.0)


if __name__ == "__main__":
    unittest.main()
