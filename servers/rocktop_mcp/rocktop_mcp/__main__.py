import os
import sys
from typing import List


APP_NAME = "rocktop-mcp"
VERSION = "0.0.1"


def _parse_allowed_dirs(env_val: str | None) -> List[str]:
    if not env_val:
        return []
    parts = [p.strip() for p in env_val.split(":") if p.strip()]
    # Normalize to absolute paths for clarity; do not create paths here.
    return [os.path.abspath(p) for p in parts]


def main() -> int:
    key = os.environ.get("ROCKTOP_MCP_KEY", "").strip()
    allowed_dirs = _parse_allowed_dirs(os.environ.get("ROCKTOP_ALLOWED_DIRS"))

    if not key:
        print(
            f"[{APP_NAME}] ERROR: ROCKTOP_MCP_KEY is not set. Refusing to start stub.",
            file=sys.stderr,
        )
        return 2

    print(f"[{APP_NAME}] {APP_NAME} v{VERSION} — stub entrypoint", file=sys.stderr)
    if allowed_dirs:
        print(
            f"[{APP_NAME}] Allowed dirs (future sandbox):\n  - "
            + "\n  - ".join(allowed_dirs),
            file=sys.stderr,
        )
    else:
        print(
            f"[{APP_NAME}] No ROCKTOP_ALLOWED_DIRS set; defaulting to read-only stub.",
            file=sys.stderr,
        )

    # TODO: Integrate MCP Python SDK and expose stdio server.
    # Suggested sketch (non-executable placeholder):
    #
    # try:
    #     from mcp.server import MCPApp
    #     from mcp.server.stdio import stdio_server
    # except ImportError:
    #     print("Install the MCP Python SDK to enable stdio server.", file=sys.stderr)
    #     return 1
    #
    # app = MCPApp(APP_NAME)
    #
    # @app.tool()
    # async def hello(key: str, name: str = "world") -> str:
    #     if key != os.environ.get("ROCKTOP_MCP_KEY", ""):
    #         raise PermissionError("unauthorized")
    #     return f"Hello, {name}!"
    #
    # async with stdio_server().run(app):
    #     await anyio.Event().wait()
    #
    # return 0

    print(
        f"[{APP_NAME}] Stub OK — key accepted. Replace TODO with MCP server.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

