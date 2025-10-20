from __future__ import annotations

import io
from typing import Tuple

import numpy as np
import soundfile as sf
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response, JSONResponse

from src.rocktop.invariants import SAMPLE_RATE_HZ


app = FastAPI(title="Rocktop Inference Stub", version="0.0.1")


def _read_wav_bytes(data: bytes) -> Tuple[np.ndarray, int]:
    buf = io.BytesIO(data)
    try:
        audio, sr = sf.read(buf, dtype="float32", always_2d=False)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid WAV: {e}") from e
    return audio, sr


def _write_wav_bytes(audio: np.ndarray, sr: int) -> bytes:
    buf = io.BytesIO()
    sf.write(buf, audio, sr, subtype="FLOAT", format="WAV")
    return buf.getvalue()


@app.get("/healthz")
def healthz() -> JSONResponse:
    return JSONResponse({"status": "ok", "sample_rate_hz": SAMPLE_RATE_HZ})


@app.post("/infer")
async def infer(audio: UploadFile = File(...)) -> Response:
    if audio.content_type not in ("audio/wav", "audio/x-wav", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Unsupported content type; expected WAV")

    data = await audio.read()
    audio_np, sr = _read_wav_bytes(data)
    if sr != SAMPLE_RATE_HZ:
        raise HTTPException(status_code=400, detail=f"Sample rate must be {SAMPLE_RATE_HZ} Hz")

    if audio_np.dtype != np.float32:
        audio_np = audio_np.astype(np.float32, copy=False)

    # Stub inference: passthrough float32 audio
    out_bytes = _write_wav_bytes(audio_np, SAMPLE_RATE_HZ)
    return Response(content=out_bytes, media_type="audio/wav")
