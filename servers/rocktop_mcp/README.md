Rocktop MCP (Python) — Stub

Purpose
- Minimal, key-gated stub for a Model Context Protocol server.
- No external MCP SDK required yet; prints a stub message for wiring.

Environment
- Set `ROCKTOP_MCP_KEY` to a non-empty value to authorize startup.
- Optional `ROCKTOP_ALLOWED_DIRS` as a colon-separated list for future sandboxing.

Run (development)
- `python -m rocktop_mcp`  # from this package directory after install, or
- `python servers/rocktop_mcp/rocktop_mcp/__main__.py`  # direct module path

Install in editable mode
- `pip install -e servers/rocktop_mcp`

Notes
- This is a stub: it does not yet speak MCP JSON-RPC. The entrypoint enforces a key,
  validates basic config, and exits successfully. Replace the TODO block with an MCP
  stdio server when adding the Python SDK.

