# OpenAI-Compatible MCP Bridge

A minimal MCP server that exposes any **OpenAI-compatible chat-completions endpoint** as callable tools.

## Why this exists

Many local or self-hosted models already expose:

- `GET /v1/models`
- `POST /v1/chat/completions`

This bridge wraps that interface behind MCP without depending on browser automation, session scraping, or provider-specific SDKs.

```text
MCP client
   |
   v
OpenAI-Compatible MCP Bridge
   |
   +--> bridge.ask
   +--> bridge.health
   |
   v
OpenAI-compatible upstream
```

## Recruiter quick scan

- MCP server with Streamable HTTP transport
- OpenAI-compatible upstream adapter
- environment-only configuration
- explicit timeout and response validation
- mock upstream for offline testing
- no browser/session automation

## Quick start

```bash
pip install -e ".[dev]"
set OPENAI_MCP_UPSTREAM_BASE_URL=http://127.0.0.1:8080/v1
set OPENAI_MCP_MODEL=my-model
python -m openai_mcp_bridge
```

Default MCP endpoint:

```text
http://127.0.0.1:8787/mcp
```

## Tools

### `bridge_ask`

Inputs:

- `prompt`
- `system_prompt` (optional)
- `model` (optional)

### `bridge_health`

Calls the configured upstream `/v1/models` endpoint.

## Offline smoke test

```bash
python -m unittest tests.test_bridge -v
ruff check src tests
python -m tests.smoke_test
python -m tests.e2e_mcp_test
```

The validation suite checks configuration/input guards, then launches a local fake OpenAI-compatible server for adapter smoke testing and a real Streamable HTTP MCP client/server round trip.

## Configuration

| Variable | Default |
| --- | --- |
| `OPENAI_MCP_UPSTREAM_BASE_URL` | `http://127.0.0.1:8080/v1` |
| `OPENAI_MCP_UPSTREAM_API_KEY` | empty |
| `OPENAI_MCP_MODEL` | `default` |
| `OPENAI_MCP_TIMEOUT_SECONDS` | `180` |
| `OPENAI_MCP_HOST` | `127.0.0.1` |
| `OPENAI_MCP_PORT` | `8787` |

## Security boundary

The bridge binds to `127.0.0.1` by default. Exposing it beyond localhost requires an authenticated HTTPS boundary, request/rate limits and an explicit data-retention policy. See [`SECURITY.md`](SECURITY.md).

## Scope

This is an adapter, not a model host. The upstream service is responsible for authentication, model serving, rate limits, and provider-specific behavior.

## License

MIT
