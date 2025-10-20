from __future__ import annotations

import os
import subprocess
import sys


def run(cmd: list[str], env: dict[str, str] | None = None) -> int:
    print(f"[mcp-smoke] run: {' '.join(cmd)}")
    try:
        res = subprocess.run(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return int(res.returncode)
    except FileNotFoundError:
        print("Python not found for MCP smoke.", file=sys.stderr)
        return 127


def main() -> int:
    py = sys.executable or "python"

    # Without key (should exit 2)
    code = run([py, "servers/rocktop_mcp/rocktop_mcp/__main__.py"])
    if code != 2:
        print(f"[mcp-smoke] Unexpected exit without key: {code}", file=sys.stderr)
        return 1
    print("[mcp-smoke] OK without key (exit 2)")

    # With key (should exit 0)
    env = os.environ.copy()
    env["ROCKTOP_MCP_KEY"] = "test"
    code = run([py, "servers/rocktop_mcp/rocktop_mcp/__main__.py"], env=env)
    if code != 0:
        print(f"[mcp-smoke] Expected success with key, got: {code}", file=sys.stderr)
        return 1
    print("[mcp-smoke] OK with key (exit 0)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

