# Security Notes

## Default trust boundary

The server binds to `127.0.0.1` by default.

That default is intentional: this repository implements an MCP-to-OpenAI-compatible adapter, **not** a complete internet-facing authentication layer.

## If you expose the MCP endpoint

Put an authenticated HTTPS boundary in front of it and define:

- who may call the MCP tools;
- which upstream/model each caller may use;
- request-size and rate limits;
- logging/redaction policy;
- network egress policy.

Do not assume that changing `OPENAI_MCP_HOST` to `0.0.0.0` makes the service production-ready.

## Upstream credentials

`OPENAI_MCP_UPSTREAM_API_KEY` is read from the environment and sent only as the upstream Bearer credential.

Recommendations:

- do not place real keys in source files;
- do not commit `.env`;
- do not log Authorization headers;
- rotate keys independently from the bridge;
- use a least-privilege upstream credential when the provider supports it.

## Prompt/data boundary

Tool arguments and optional system prompts are forwarded to the configured upstream model.

Therefore callers must treat the upstream as a data processor for that content. Do not send secrets or private data to an upstream whose retention/training policy you have not evaluated.

## Upstream URL

The base URL is operator configuration, not an untrusted tool argument. If a future version allows per-request upstream URLs, it must add explicit allow-listing / SSRF controls.

## Deliberate exclusions

This project does not:

- extract browser cookies or sessions;
- automate website login;
- bypass provider access controls;
- implement a model host;
- provide tenant isolation or user authentication.
