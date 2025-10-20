"""Simple data catalog abstraction for audio datasets.
Indexes WAV files, validates global invariants, and emits a JSON index.
"""
from __future__ import annotations

import json
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from .config import Settings, get_settings
from .invariants import enforce_sample_rate


@dataclass(frozen=True)
class AudioItem:
    path: Path
    sample_rate: int
    channels: int
    frames: int
    duration_s: float
    bit_depth: Optional[int] = None
    speaker: Optional[str] = None

    def to_json(self) -> dict:
        return {
            "path": str(self.path),
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "frames": self.frames,
            "duration_s": self.duration_s,
            "bit_depth": self.bit_depth,
            "speaker": self.speaker,
        }


def _probe_wav(path: Path) -> AudioItem:
    # Minimal header probe via stdlib; assumes uncompressed WAV.
    with wave.open(str(path), "rb") as wf:
        sr = wf.getframerate()
        ch = wf.getnchannels()
        frames = wf.getnframes()
        sampwidth = wf.getsampwidth()  # bytes per sample
        bit_depth = sampwidth * 8 if sampwidth > 0 else None
        duration = float(frames) / float(sr) if sr else 0.0
    return AudioItem(path=path, sample_rate=sr, channels=ch, frames=frames, duration_s=duration, bit_depth=bit_depth)


def scan_audio(root: Path, *, settings: Optional[Settings] = None) -> List[AudioItem]:
    settings = settings or get_settings()
    items: List[AudioItem] = []
    for p in root.rglob("*.wav"):
        item = _probe_wav(p)
        # Enforce global sample rate invariant
        enforce_sample_rate(item.sample_rate)
        items.append(item)
    return items


def save_catalog(items: Iterable[AudioItem], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8") as f:
        json.dump([it.to_json() for it in items], f, indent=2)


def index_default_dataset(*, settings: Optional[Settings] = None) -> Path:
    settings = settings or get_settings()
    processed = settings.paths.processed_dir
    catalog_path = processed / "catalog.json"
    items = scan_audio(processed, settings=settings)
    save_catalog(items, catalog_path)
    return catalog_path

