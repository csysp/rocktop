from __future__ import annotations

"""
Minimal training skeleton.

Requirements (not installed by default in CI):
  - torch, lightning, numpy, soundfile

Usage:
  python train.py

This is a CPU-friendly scaffold that validates data loading and a tiny model.
"""

import argparse
from pathlib import Path
from typing import List, Optional

import numpy as np

try:
    import soundfile as sf
    import torch
    from torch.utils.data import Dataset, DataLoader
    import lightning as L
    from lightning.pytorch.loggers import CSVLogger
except Exception as e:  # pragma: no cover - optional deps
    sf = None  # type: ignore
    torch = None  # type: ignore
    L = None  # type: ignore
    CSVLogger = None  # type: ignore

from src.rocktop.invariants import SAMPLE_RATE_HZ


class AudioDataset(Dataset):  # type: ignore[misc]
    def __init__(self, root: Path, segment_seconds: float = 1.0) -> None:
        if sf is None:
            raise RuntimeError("soundfile is required for AudioDataset")
        self.files: List[Path] = [p for p in root.rglob("*.wav")]
        self.seg = int(SAMPLE_RATE_HZ * segment_seconds)

    def __len__(self) -> int:
        return max(1, len(self.files))

    def __getitem__(self, idx: int):  # type: ignore[override]
        path = self.files[idx % len(self.files)]
        audio, sr = sf.read(path, dtype="float32", always_2d=False)  # type: ignore[arg-type]
        if sr != SAMPLE_RATE_HZ:
            raise ValueError(f"Expected {SAMPLE_RATE_HZ} Hz, got {sr} in {path}")
        if audio.ndim == 2:
            audio = audio.mean(axis=1)  # mono downmix
        if len(audio) < self.seg:
            pad = self.seg - len(audio)
            audio = np.pad(audio, (0, pad))
        start = 0 if len(audio) == self.seg else np.random.randint(0, len(audio) - self.seg + 1)
        chunk = audio[start : start + self.seg]
        x = np.expand_dims(chunk, 0)  # [1, T]
        return torch.from_numpy(x)  # type: ignore[no-any-return]


class TinyAutoEncoder(L.LightningModule):  # type: ignore[misc]
    def __init__(self) -> None:
        super().__init__()
        self.encoder = torch.nn.Sequential(
            torch.nn.Conv1d(1, 8, kernel_size=9, stride=2, padding=4),
            torch.nn.ReLU(),
            torch.nn.Conv1d(8, 16, kernel_size=9, stride=2, padding=4),
            torch.nn.ReLU(),
        )
        self.decoder = torch.nn.Sequential(
            torch.nn.ConvTranspose1d(16, 8, kernel_size=4, stride=2, padding=1),
            torch.nn.ReLU(),
            torch.nn.ConvTranspose1d(8, 1, kernel_size=4, stride=2, padding=1),
        )
        self.criterion = torch.nn.L1Loss()

    def forward(self, x):  # type: ignore[override]
        z = self.encoder(x)
        y = self.decoder(z)
        return y

    def training_step(self, batch, batch_idx):  # type: ignore[override]
        y = self(batch)
        loss = self.criterion(y, batch)
        self.log("train_loss", loss)
        return loss

    def configure_optimizers(self):  # type: ignore[override]
        return torch.optim.Adam(self.parameters(), lr=1e-3)


def run_training(data_dir: Path, batch_size: int, epochs: int) -> int:
    if L is None or torch is None or sf is None:
        print("Install torch, lightning, and soundfile to run training.")
        return 2
    ds = AudioDataset(Path(data_dir))
    dl = DataLoader(ds, batch_size=batch_size, shuffle=True, num_workers=0)
    model = TinyAutoEncoder()
    trainer = L.Trainer(max_epochs=epochs, logger=CSVLogger("runs", name="tiny"), enable_checkpointing=False)
    trainer.fit(model, dl)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/processed", help="Processed WAV directory")
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--epochs", type=int, default=1)
    args = ap.parse_args()
    return run_training(Path(args.data), args.batch, args.epochs)


# Optional Hydra wrapper
try:  # pragma: no cover - hydra not required in CI
    import hydra
    from omegaconf import DictConfig

    @hydra.main(version_base="1.3", config_path="configs/hydra", config_name="defaults")
    def hydra_entry(cfg: DictConfig) -> None:  # type: ignore[no-redef]
        data_dir = Path(cfg.paths.processed_dir)
        batch = int(getattr(cfg.trainer, "batch", 4))
        epochs = int(getattr(cfg.trainer, "epochs", 1))
        run_training(data_dir, batch, epochs)

    HYDRA_AVAILABLE = True
except Exception:
    HYDRA_AVAILABLE = False


if __name__ == "__main__":
    if HYDRA_AVAILABLE:
        hydra_entry()  # type: ignore[misc]
        raise SystemExit(0)
    raise SystemExit(main())
