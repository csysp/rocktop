from __future__ import annotations

import io
import subprocess
import sys
import wave
from pathlib import Path


def _write_wav(path: Path, sr: int = 48_000, duration_s: float = 0.005) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    n_channels = 1
    sampwidth = 2
    n_frames = int(sr * duration_s)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(n_channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(sr)
        wf.writeframes(b"\x00\x00" * n_frames)


def test_cache_stubs(tmp_path: Path):
    in_dir = tmp_path / "in"
    out_f0 = tmp_path / "f0"
    out_units = tmp_path / "units"
    wav = in_dir / "x.wav"
    _write_wav(wav)

    code = subprocess.call([sys.executable, "tools/cache_f0.py", "--in", str(in_dir), "--out", str(out_f0)])
    assert code == 0
    code = subprocess.call([sys.executable, "tools/cache_units.py", "--in", str(in_dir), "--out", str(out_units), "--model", "hubert-soft"])
    assert code == 0

    f0_file = out_f0 / "x.f0.txt"
    units_file = out_units / "x.units.txt"
    assert f0_file.exists()
    assert units_file.exists()
    assert "stub_f0_digest=" in f0_file.read_text()
    text = units_file.read_text()
    assert "stub_units_model=hubert-soft" in text and "stub_units_digest=" in text

