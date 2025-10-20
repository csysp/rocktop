# rocktop

This is the monorepo for the "rocktop" vocal model training/inference system's various core functions and supporting systems. The readme will be updated as development progresses, pretty much nothing is implemented. After multiple years of using various singing model inference platforms and being unsatisfied with the lack of free, transparent options available it became clear an open source, flexible, extensible offering was needed. Firstly for personal use, secondarily for whomever may need this toolset.

The software is free to use under the GPLv3 licence but models trained may carry copyrights from the source vocalist, do your business right. 

Below are initial renders of the core flow and stack flow for ease of reference.

## Architecture Diagrams

### Core Flow

```mermaid
flowchart TB
 subgraph Clients["Clients"]
        UIVoice[["Studio or DAW"]]
  end
 subgraph Inference["Inference (48kHz, low-latency)"]
        FastAPI["FastAPI + Uvicorn"]
        TorchServe["TorchServe"]
        ModelInfer["PyTorch Model"]
        BigVGAN["BigVGAN or Vocos"]
        Stream["Chunking + Overlap-Add"]
  end
 subgraph Training["Training and Preprocessing"]
        Preproc["Preprocess: SoX SRC, peak norm, trim"]
        Feats["Features: HuBERT or ContentVec, RMVPE"]
        Trainer["Trainer: Lightning or Accelerate"]
        Hydra["Hydra Configs"]
        Metrics["Audio metrics"]
  end
 subgraph Models["Models"]
        RVC["RVC 48kHz"]
        DiffSinger["DiffSinger or SoVITS"]
        Vocoder["BigVGAN or Vocos"]
  end
 subgraph Storage["Storage and Tracking"]
        Data[("MinIO or S3")]
        MLflow[("MLflow Tracking")]
  end
 subgraph ROCm["ROCm test"]
        ROCmImg["pytorch rocm image"]
  end
 subgraph CUDA["CUDA prod"]
        CUDAImg["pytorch cuda image"]
  end
 subgraph K8s["Kubernetes"]
        AMDPlugin["AMD Device Plugin"]
        NVPlugin["NVIDIA Device Plugin"]
        Jobs["K8s Jobs"]
        Deploys["K8s Deployments with HPA"]
        PVC["PVC for datasets"]
  end
 subgraph Infra["Infra and GPU Targets"]
        ROCm
        CUDA
        K8s
  end
 subgraph Audio["Audio Quality"]
        SR["48kHz end to end"]
        F32["32 bit float"]
        SRC["SoX soxr linear phase"]
        Loudness["Peak normalize to -1 dBFS"]
  end
    UIVoice --> FastAPI
    UIVoice -.-> TorchServe
    FastAPI --> Stream
    Stream --> ModelInfer
    ModelInfer --> BigVGAN & RVC & Vocoder
    BigVGAN --> FastAPI
    TorchServe --> ModelInfer
    ModelInfer -.-> DiffSinger
    Data --> Preproc & FastAPI
    Preproc --> Feats
    Feats --> Trainer & Data
    Hydra --> Trainer
    Trainer --> MLflow & Data
    MLflow --> FastAPI
    Jobs --> Trainer
    Deploys --> FastAPI
    PVC --> Trainer & FastAPI
    AMDPlugin --> K8s
    NVPlugin --> K8s
    ROCmImg --> Trainer & FastAPI
    CUDAImg --> Trainer & FastAPI
    Audio -. guides .-> Preproc & Feats & ModelInfer

    style Audio fill:#fff,stroke:#bbb,stroke-dasharray: 3 3
    style Inference fill:#eef,stroke:#88a
    style Training fill:#efe,stroke:#8a8
    style Models fill:#ffe,stroke:#aa8
    style Storage fill:#fef,stroke:#a8a
    style Infra fill:#eef,stroke:#88a
```

### Core Stack

```mermaid
  flowchart LR
  subgraph Core["Core Stack"]
  style Core fill:#eef,stroke:#88a
  PyTorch[PyTorch 2.3+ ROCm or CUDA]
  AudioLibs[torchaudio, librosa, soundfile]
  Hydra[Hydra]
  TrainRuntimes[Lightning or Accelerate]
  Serve[TorchServe or FastAPI]
  end
  subgraph Services["K8s Services"]
  style Services fill:#efe,stroke:#8a8
  Preproc[K8s Job: Preprocessing]
  Train[K8s Job: Training]
  Infer[K8s Deployment: Inference]
  Track[MLflow Server]
  ObjStore[MinIO or S3]
  Monitor[Prometheus and Grafana]
  end
  subgraph Models["Models and Features"]
  style Models fill:#ffe,stroke:#aa8
  Units[HuBERT or ContentVec units]
  F0[RMVPE F0]
  VC[RVC 48kHz]
  Singer[DiffSinger or SoVITS]
  Vocoder[BigVGAN or Vocos]
  end
  subgraph GPU["GPU Targets"]
  style GPU fill:#fef,stroke:#a8a
  AMD[ROCm test]
  NVIDIA[CUDA prod]
  AMDPlugin[AMD K8s Device Plugin]
  NVPlugin[NVIDIA K8s Device Plugin]
  end

  PyTorch --> TrainRuntimes --> Train
  AudioLibs --> Preproc
  Serve --> Infer
  Hydra --> Train

  Preproc --> Units
  Preproc --> F0
  Units --> VC
  F0 --> VC
  VC --> Vocoder
  Train --> Track
  Track --> ObjStore
  Preproc --> ObjStore
  Train --> ObjStore
  Infer --> ObjStore

  Serve --> VC --> Vocoder --> Infer

  AMDPlugin --> AMD
  NVPlugin --> NVIDIA
  AMD --> Train
  AMD --> Infer
  NVIDIA --> Train
  NVIDIA --> Infer
```

## Platforms

- Deploy target: Ubuntu Server LTS (pinned to 24.04 in CI runners).
- CI tests: Linux (Ubuntu 22.04), macOS, and Windows for portability.

## Local Dev Quickstart (Python 3.11)

1. Ensure Python 3.11, install uv (optional) and pre-commit:
   - pip install pre-commit
   - pre-commit install
2. Run linters/tests locally:
   - ruff check . && black --check . && codespell
   - mypy src servers/rocktop_mcp
   - pytest -q
3. Run the inference stub:
   - uvicorn app.infer:app --host 0.0.0.0 --port 8080
4. Generate SBOMs locally (optional):
   - syft . -o spdx-json > sbom-repo.spdx.json
   - syft . -o cyclonedx-json > sbom-repo.cdx.json

See AGENTS.md for architecture and environment details.

## Data Prep Scripts

- Resample to 48 kHz float32 (linear-phase, very high quality SRC):
  - scripts/sox_resample.sh raw_audio data/processed
- Peak normalize to −1 dBFS:
  - scripts/sox_normalize.sh data/processed data/normalized

Make targets (uses uv where applicable):
- make fmt | make lint | make type | make test
- make sbom-repo | make trivy-fs
- make serve | make mcp-smoke
- make sox-resample IN=raw_audio OUT=data/processed
- make sox-normalize IN=data/processed OUT=data/normalized

## CI Overview

- Lint/Format: Ruff, Black, Codespell
- Typing: mypy
- Tests: pytest (skips if none)
- Security: Gitleaks, Bandit, pip-audit (blocking)
- SBOMs: Syft (repo SPDX + CycloneDX), Syft (image SPDX + CycloneDX)
- Scanning: Trivy filesystem (always), Trivy image (on image build)
- Docker hygiene: Hadolint
- Kubernetes: kubeconform, kube-linter, OPA/Conftest policies
- Images: Buildx build, GHCR push on main/master, Cosign sign + SBOM attest
- Workflows use concurrency to cancel superseded runs
