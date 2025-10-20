#!/usr/bin/env bash
set -euo pipefail

echo "[mcp-smoke] Checking without key (should fail)..."
set +e

# Choose python interpreter
PY=python
if ! command -v "$PY" >/dev/null 2>&1; then
  PY=python3
fi

"$PY" servers/rocktop_mcp/rocktop_mcp/__main__.py 1>/dev/null 2>/dev/null
code=$?
set -e
if [ "$code" -eq 2 ]; then
  echo "[mcp-smoke] OK: exit code $code without key"
else
  echo "[mcp-smoke] Unexpected exit code without key: $code" >&2
  exit 1
fi

echo "[mcp-smoke] Checking with key (should succeed)..."
ROCKTOP_MCP_KEY=test "$PY" servers/rocktop_mcp/rocktop_mcp/__main__.py 1>/dev/null 2>/dev/null || {
  echo "[mcp-smoke] Expected success with key" >&2
  exit 1
}
echo "[mcp-smoke] OK: stub accepts key"
