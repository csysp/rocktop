from __future__ import annotations

import pytest

from src.rocktop import invariants as inv


def test_constants():
    assert inv.SAMPLE_RATE_HZ == 48_000
    assert inv.AUDIO_FLOAT_DTYPE == "float32"


def test_enforce_sample_rate_ok():
    inv.enforce_sample_rate(48_000)


def test_enforce_sample_rate_fail():
    with pytest.raises(ValueError):
        inv.enforce_sample_rate(44_100)


def test_enforce_dtype_ok():
    inv.enforce_dtype("float32")


def test_enforce_dtype_fail():
    with pytest.raises(ValueError):
        inv.enforce_dtype("int16")

