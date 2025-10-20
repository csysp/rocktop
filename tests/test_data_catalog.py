from __future__ import annotations

import io
import wave
from pathlib import Path

import pytest

from src.rocktop.data_catalog import scan_audio


def _write_wav(path: Path, sr: int = 48_000, duration_s: float = 0.01) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    n_channels = 1
    sampwidth = 2  # 16-bit PCM
    n_frames = int(sr * duration_s)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(n_channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(sr)
        wf.writeframes(b"\x00\x00" * n_frames)


def test_scan_audio_ok(tmp_path: Path):
    wav = tmp_path / "a.wav"
    _write_wav(wav, 48_000)
    items = scan_audio(tmp_path)
    assert len(items) == 1
    assert items[0].sample_rate == 48_000


def test_scan_audio_rejects_wrong_sr(tmp_path: Path):
    wav = tmp_path / "b.wav"
    _write_wav(wav, 44_100)
    with pytest.raises(ValueError):
        scan_audio(tmp_path)

