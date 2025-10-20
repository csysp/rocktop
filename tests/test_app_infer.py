from __future__ import annotations

import io
import wave

from fastapi.testclient import TestClient

from app.infer import app
from src.rocktop.invariants import SAMPLE_RATE_HZ


client = TestClient(app)


def _make_wav_bytes(sr: int = SAMPLE_RATE_HZ, duration_s: float = 0.01, channels: int = 1) -> bytes:
    buf = io.BytesIO()
    sampwidth = 2  # 16-bit PCM
    n_frames = int(sr * duration_s)
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(sr)
        # silence
        wf.writeframes(b"\x00\x00" * n_frames * channels)
    return buf.getvalue()


def _probe_wav_bytes(data: bytes):
    with wave.open(io.BytesIO(data), "rb") as wf:
        return wf.getframerate(), wf.getnchannels(), wf.getnframes(), wf.getsampwidth()


def test_healthz():
    res = client.get("/healthz")
    assert res.status_code == 200
    body = res.json()
    assert body.get("status") == "ok"
    assert body.get("sample_rate_hz") == SAMPLE_RATE_HZ


def test_infer_echo_wav_properties():
    wav_bytes = _make_wav_bytes(channels=2)
    files = {"audio": ("test.wav", wav_bytes, "audio/wav")}
    res = client.post("/infer", files=files)
    assert res.status_code == 200
    assert res.headers.get("content-type", "").startswith("audio/wav")
    sr_out, ch_out, frames_out, sampwidth_out = _probe_wav_bytes(res.content)
    assert sr_out == SAMPLE_RATE_HZ
    assert ch_out == 2
    # Output is float32 WAV, so sample width 4 bytes
    assert sampwidth_out == 4
