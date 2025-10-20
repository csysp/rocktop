## Global invariants for audio processing and training
from __future__ import annotations

SAMPLE_RATE_HZ: int = 48_000
AUDIO_FLOAT_DTYPE: str = "float32"
PEAK_NORMALIZE_DBFS: float = -1.0


def enforce_sample_rate(sr: int) -> None:
    if sr != SAMPLE_RATE_HZ:
        raise ValueError(f"Sample rate must be {SAMPLE_RATE_HZ} Hz, got {sr}")


def enforce_dtype(dtype: str) -> None:
    if dtype.lower() != AUDIO_FLOAT_DTYPE:
        raise ValueError(
            f"Audio dtype must be {AUDIO_FLOAT_DTYPE}, got {dtype}"
        )

