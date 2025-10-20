from __future__ import annotations

import sys


def main() -> int:
    try:
        import pytest  # type: ignore
    except Exception as e:  # pragma: no cover
        print(f"pytest not available: {e}", file=sys.stderr)
        return 2

    code = pytest.main(["-q"])  # type: ignore[arg-type]
    # Exit code 5 means no tests collected; treat as success.
    if code == 5:
        print("No tests collected; skipping.")
        return 0
    return int(code)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

