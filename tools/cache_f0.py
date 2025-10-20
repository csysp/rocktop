#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="Stub RMVPE F0 cache generator")
    p.add_argument("--in", dest="in_dir", required=True, help="Input directory of WAVs")
    p.add_argument("--out", dest="out_dir", required=True, help="Output directory for cache")
    args = p.parse_args()

    in_dir = Path(args.in_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for wav in in_dir.rglob("*.wav"):
        # Stub: write a deterministic placeholder per file
        digest = hashlib.sha256(wav.read_bytes()).hexdigest()[:16]
        out = out_dir / (wav.stem + ".f0.txt")
        out.write_text(f"stub_f0_digest={digest}\n")
        count += 1

    print(f"[cache_f0] wrote {count} placeholders to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

