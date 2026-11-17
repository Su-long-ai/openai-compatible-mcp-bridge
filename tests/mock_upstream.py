from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
PORT = 18080


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/v1/models":
            return self._send(200, {"object": "list", "data": [{"id": "mock-model"}]})
        self._send(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path != "/v1/chat/completions":
            return self._send(404, {"error": "not found"})
        length = int(self.headers.get("Content-Length", "0"))
        data = json.loads(self.rfile.read(length).decode("utf-8"))
        prompt = next(
            (m.get("content", "") for m in reversed(data.get("messages", [])) if m.get("role") == "user"),
            "",
        )
        self._send(
            200,
            {
                "choices": [{"message": {"role": "assistant", "content": f"MOCK_OK: {prompt}"}}],
                "model": data.get("model", "mock-model"),
            },
        )

    def log_message(self, format: str, *args) -> None:
        pass


def serve() -> None:
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
