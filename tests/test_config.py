from __future__ import annotations

import os
import pytest

from src.rocktop.config import get_settings, reset_settings_cache


def test_default_settings():
    reset_settings_cache()
    s = get_settings()
    assert s.sample_rate_hz == 48_000
    assert s.audio_float_dtype == "float32"
    assert str(s.paths.processed_dir) == "data/processed"


def test_env_override_sample_rate_invalid(monkeypatch):
    reset_settings_cache()
    monkeypatch.setenv("ROCKTOP_SAMPLE_RATE_HZ", "44100")
    with pytest.raises(SystemExit):
        get_settings()
    # cleanup
    monkeypatch.delenv("ROCKTOP_SAMPLE_RATE_HZ", raising=False)
    reset_settings_cache()
