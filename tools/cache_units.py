#!/usr/bin/env python
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="Stub HuBERT/ContentVec units cache generator")
    p.add_argument("--in", dest="in_dir", required=True, help="Input directory of WAVs")
    p.add_argument("--out", dest="out_dir", required=True, help="Output directory for cache")
    p.add_argument("--model", default="hubert-soft", help="Units model name (stub)")
    args = p.parse_args()

    in_dir = Path(args.in_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for wav in in_dir.rglob("*.wav"):
        digest = hashlib.md5(wav.read_bytes()).hexdigest()[:16]
        out = out_dir / (wav.stem + ".units.txt")
        out.write_text(f"stub_units_model={args.model}\nstub_units_digest={digest}\n")
        count += 1

    print(f"[cache_units] wrote {count} placeholders to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

