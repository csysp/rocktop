 Unified Vision

  - Goal: End-to-end singer/voice training + ultra‑clean inference, reproducible
  across AMD (ROCm test) and NVIDIA (A6000 prod), containerized and schedulable
  on Kubernetes.
  - Core stack: PyTorch 2.3+ (ROCm and CUDA builds), torchaudio/librosa/soundfile,
  Hydra configs, Lightning/Accelerate for training, TorchServe or FastAPI+UVicorn
  for inference.
  - Services: training jobs (K8s Job), offline preprocessing (K8s Job), realtime/
  low‑latency inference (Deployment + HPA), experiment tracking (MLflow), object
  storage (MinIO/S3), monitoring (Prometheus/Grafana).
  - Models: voice conversion and/or singing synthesis with emphasis on fidelity:
  RVC (Retrieval‑based Voice Conversion) + BigVGAN 48 kHz vocoder; optionally
  DiffSinger/SoVITS for singing synthesis; precompute content features (HuBERT/
  ContentVec) + high‑quality F0 (RMVPE).

  Audio Quality Principles

  - Sample rate: choose 48 kHz end‑to‑end for studio use; train and serve at 48 kHz
  to avoid SRC at inference.
  - Bit depth: process in 32‑bit float; only dither when exporting to 24/16‑bit PCM
  for delivery.
  - Resampling: use SoX HQ (soxr) linear‑phase, very high quality. Avoid cheap SRC
  in ffmpeg defaults.
  - Loudness: avoid aggressive loudness normalization for training; at most peak
  normalize to −1 dBFS, keep dynamics intact; remove clipping.
  - Cleanup: trim silence smartly; avoid denoise/dereverb unless artifacts are
  clear; do not hard‑de‑ess masters.
  - Features: use RMVPE for F0; use HuBERT/ContentVec for content units; precompute
  and cache.

  ROCm Test Environment (RX 6700 XT)
  Note: RX 6700 XT (Navi 22) may require an override; official support varies by
  ROCm version.

  - Host prerequisites (Ubuntu 22.04/24.04 LTS recommended):
      - ROCm drivers + runtime installed and working (rocminfo, clinfo).
      - Docker + rootless or standard with --group-add video.
      - Confirm devices: /dev/kfd, /dev/dri.
  - Pull a PyTorch ROCm image (adjust to your installed ROCm):
      - docker pull pytorch/pytorch:2.4.1-rocm6.0
  - Run with GPU devices (and optional GFX override if needed):
      - docker run -it --rm --ipc=host --shm-size=16g --ulimit memlock=-1
  --ulimit stack=67108864 --device=/dev/kfd --device=/dev/dri --group-add video
  -e HSA_OVERRIDE_GFX_VERSION=10.3.0 -v $PWD:/workspace -w /workspace pytorch/
  pytorch:2.4.1-rocm6.0 bash
  - Verify inside container:
      - python - <<'PY'\nimport torch\nprint('torch',
  torch.__version__)\nprint('HIP', torch.version.hip)\nprint('cuda_is_available
  (HIP-backed):', torch.cuda.is_available())\nx = torch.randn(1024,1024,
  device='cuda'); y = x @ x; print(y.mean().item())\nPY
  - Install system DSP deps (inside container):
      - apt-get update && apt-get install -y --no-install-recommends ffmpeg
  sox libsox-dev libsox-fmt-all libsndfile1 libsndfile1-dev libsamplerate0
  libsamplerate0-dev rubberband-cli espeak-ng git curl build-essential pkg-config
  - Install Python deps:
      - pip install --no-cache-dir torchaudio==2.4.1 --index-url https://
  download.pytorch.org/whl/rocm6.0
      - pip install --no-cache-dir librosa==0.10.2.post1 soundfile auraloss
  torchmetrics[audio] hydra-core==1.3.2 lightning==2.4.0 mlflow==2.16.0 fastapi
  uvicorn[standard] pydantic==2.*
      - pip install --no-cache-dir phonemizer g2p_en praat-parselmouth pyworld
  ffmpeg-python pesq pystoi
      - Content/F0 feature extractors (choose stack): pip install --no-cache-dir
  rmvpe torchcrepe
  - High‑quality resample/normalize examples:
      - Float 32‑bit, very high quality SRC to 48 kHz: sox in.wav -b 32 -e float -r
  48000 out_48k.wav rate -v -s 48000
      - Peak normalize to −1 dBFS: sox in.wav out_norm.wav gain -n -1
      - Smart silence trim: sox in.wav out_trim.wav silence 1 0.1 0.1% -1 0.3 0.1%

  CUDA Prod Environment (A6000)

  - Install NVIDIA drivers + Container Toolkit on the node.
  - Pull a matching CUDA image:
      - docker pull pytorch/pytorch:2.4.1-cuda12.1-cudnn9-runtime
  - Run with GPU:
      - docker run -it --rm --gpus all --ipc=host --shm-size=16g -v $PWD:/workspace
  -w /workspace pytorch/pytorch:2.4.1-cuda12.1-cudnn9-runtime bash
  - Inside container:
      - apt-get update && apt-get install -y --no-install-recommends ffmpeg
  sox libsox-dev libsox-fmt-all libsndfile1 libsndfile1-dev libsamplerate0
  libsamplerate0-dev rubberband-cli espeak-ng git curl build-essential pkg-config
      - pip install --no-cache-dir torchaudio==2.4.1 librosa==0.10.2.post1
  soundfile auraloss torchmetrics[audio] hydra-core==1.3.2 lightning==2.4.0
  mlflow==2.16.0 fastapi uvicorn[standard] pydantic==2.* phonemizer g2p_en praat-
  parselmouth pyworld ffmpeg-python pesq pystoi rmvpe torchcrepe

  Baseline Models (High Fidelity)

  - Voice conversion (fast + high quality): RVC at 48 kHz with RMVPE F0; BigVGAN/
  Vocos vocoder; precompute HuBERT soft units.
  - Singing synthesis (highest quality, more complex): DiffSinger + NSF‑HiFiGAN at
  44.1/48 kHz, requires score/lyrics/phonemes; excellent clarity and stability.
  - Practical path: start with RVC 48 kHz for your own voice/singer timbre capture;
  add DiffSinger later if you need from‑scratch singing synthesis.

  Data & Preprocessing

  - Target format on disk: WAV, 48 kHz, mono or stereo as needed, 32‑bit float,
  filenames with speaker/session IDs.
  - Recommended steps per file:
      - SRC: sox <in> -b 32 -e float -r 48000 <out>
      - Peak normalize: sox <in> <out> gain -n -1
      - Remove leading/trailing silence (command above).
      - Optional high‑pass at 30 Hz: sox in.wav out.wav highpass 30
  - Avoid: brickwall limiting, broadband denoise, de‑reverb unless necessary (can
  damage phase cues important to timbre).
  - Aligners (if using phonemes/lyrics): Montreal Forced Aligner + phonemizer
  (needs espeak-ng).

  Kubernetes GPU Setup

  - AMD device plugin:
      - Install: kubectl apply -f https://raw.githubusercontent.com/
  RadeonOpenCompute/k8s-device-plugin/master/k8s-ds-amd-gpu.yaml
      - Schedules with: resources: { limits: { amd.com/gpu: "1" } }
      - Label AMD node: kubectl label nodes <amd-node> gpu.vendor=amd
  - NVIDIA device plugin:
      - Install: kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-
  device-plugin/daemonset/nvidia-device-plugin.yml
      - Schedules with: resources: { limits: { nvidia.com/gpu: "1" } }
      - Label NVIDIA node: kubectl label nodes <nvidia-node> gpu.vendor=nvidia
  - Example Job (swap resource per vendor):
      - apiVersion: batch/v1\nkind: Job\nmetadata:\n  name: vc-train\nspec:
  \n  template:\n    spec:\n      nodeSelector:\n        gpu.vendor:
  amd\n      restartPolicy: Never\n      containers:\n      - name: trainer\n
  image: your/rocm-train:latest\n        resources:\n          limits:
  \n            amd.com/gpu: \"1\"\n        volumeMounts:\n        - name: data\n
  mountPath: /data\n        command: [\"python\",\"train.py\",\"hydra.run.dir=/
  runs/$(date +%s)\"]\n      volumes:\n      - name: data\n        hostPath:\n
  path: /mnt/datasets\n          type: Directory

  Inference Service

  - TorchServe (portable across ROCm/CUDA) or FastAPI wrapper that loads your
  PyTorch checkpoint and runs on cuda device (maps to HIP on ROCm images).
  - Realtime tuning:
      - Use 48 kHz end‑to‑end.
      - Small hop sizes (256 at 48 kHz) for F0; chunked streaming with overlap‑add
  (e.g., 50%).
      - Keep model in half precision on A6000 (FP16 or BF16), test on ROCm FP16;
  pin memory, pre‑warm kernels.

  Experiment Tracking & Storage

  - MLflow tracking server:
      - docker run -it --rm -p 5000:5000 -v $PWD/mlruns:/mlruns ghcr.io/mlflow/
  mlflow:latest mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri
  sqlite:///mlruns/mlflow.db --default-artifact-root /mlruns
  - Object storage (MinIO for datasets and artifacts):
      - docker run -p 9000:9000 -p 9001:9001 -v $PWD/minio:/data -e
  MINIO_ROOT_USER=admin -e MINIO_ROOT_PASSWORD=changeit quay.io/minio/minio
  server /data --console-address ":9001"

  Concrete Next Steps (Terminal)

  1. Stand up AMD ROCm container (test math, install DSP deps).

  - Commands provided above (ROCm section). Confirm HIP works and torchaudio can
  load/stream 48 kHz WAVs.

  2. Stand up CUDA container on the A6000 node with the same Python deps.

  - Commands provided above (CUDA section).

  3. Prepare data directory with consistent 48 kHz float WAVs.

  - Batch convert with SoX:
      - find raw_audio -type f -name '*.wav' -print0 | xargs -0 -I{} sox '{}' -b 32
  -e float -r 48000 'data48k/{}' rate -v -s 48000
      - find data48k -type f -name '*.wav' -print0 | xargs -0 -I{} sox '{}' '{}'
  gain -n -1

  4. Precompute features in the container (example placeholders):

  - RMVPE F0 cache: python tools/cache_f0.py --in data48k --out cache/f0
  - HuBERT units: python tools/cache_units.py --in data48k --out cache/units
  --model hubert-soft

  5. Launch a simple FastAPI inference prototype (both images):

  - uvicorn app.infer:app --host 0.0.0.0 --port 8080 and test with 48 kHz WAV I/O.

  6. K8s device plugins, PVCs, and a training Job targeting AMD, later NVIDIA.

  - Apply the device plugin manifests; set up a PersistentVolume for /mnt/datasets.

  Model Choices Summary

  - Start: RVC 48 kHz + RMVPE + BigVGAN/Vocos for the fastest path to high fidelity
  VC.
  - Graduate: DiffSinger 44.1/48 kHz for controllable singing synthesis if you need
  scores/lyrics.
  - Optional: De‑reverb/dereverb training variants if your source material varies.

  Checks For Maximum Clarity

  - Keep everything float‑32 in the pipeline; dither only at export.
  - Keep sample rate fixed (48 kHz) from dataset through training and inference.
  - Prefer linear‑phase very‑high SRC; avoid SRC on‑the‑fly at inference.
  - Use RMVPE for pitch; verify F0 tracks on vibrato and high registers.
  - Validate with PESQ/STOI plus listening tests at 48 kHz.

CI LOADOUT
============================================================
Lint/Format: Ruff + Black + Codespell
Typing: mypy
Secrets: Gitleaks
Python SAST: Bandit (optionally Semgrep add‑on)
Dep vulns: pip‑audit (blocking; optionally OSV)
SBOM: Syft (repo and image, SPDX JSON)
Image scan: Trivy (image; FS optional)
Dockerfile: Hadolint
K8s schema/practices: kubeconform + kube‑linter + OPA/Conftest policies
Testing: pytest (+ asyncio + cov)
Property tests: Hypothesis
Benchmarks: pytest‑benchmark (asv later for labs)
API fuzz: Schemathesis
Load: Locust
MCP checks: stub smoke harness (JSON‑RPC later)
Docs/Notebooks: markdownlint‑cli2 + nbstripout
============================================================

CI Toolchain Status (Monorepo)

- Current state (GitHub Actions):
    - Lint/format: Ruff, Black, Codespell.
    - Typing: mypy on `src/` and `servers/rocktop_mcp/`.
    - Tests: pytest on Ubuntu 24.04, macOS, Windows; graceful skip if none.
    - Security: Gitleaks (secrets), Bandit (Python SAST), pip‑audit (blocking).
    - Docker hygiene: Hadolint.
    - Scans/SBOMs: Trivy filesystem (always); Syft repo SBOM (SPDX + CycloneDX) on PR/push.
    - Images: Buildx matrix across Dockerfiles; Syft image SBOMs (SPDX + CycloneDX); Trivy image scan; GHCR push on main/master; Cosign keyless sign + SBOM attest.
    - Kubernetes: kubeconform (schema), kube‑linter (best practices), OPA/Conftest policies (labels, no :latest, scoped RBAC, non‑root, seccomp, runAsUser >= 1000, drop ALL caps, resources on containers/initContainers).
    - Docs/Notebooks/Scripts: markdownlint, nbstripout check, ShellCheck + shfmt.
    - MCP: stub smoke workflow verifies key‑gated startup.

Future Concerns (Prioritized)

- Reproducibility
  - Expand `uv.lock` to include dev and extras (api) resolution if/when supported; otherwise document constraints and pin transitive deps where critical.
  - Pin GitHub Actions to commit SHAs for supply‑chain hardening (currently pinned by version tags).

- Features & Models
  - Replace RMVPE/units stubs with real extractors; cache formats and provenance; validate RMVPE on vibrato/high registers.
  - Integrate 48 kHz vocoder (BigVGAN/Vocos) and RVC/DiffSinger as needed; standardize model checkpoints and registry.

- Training Pipeline
  - Flesh out Lightning/Accelerate trainer, datasets, augmentations; wire full Hydra config groups (data/model/trainer/experiment).
  - Add golden audio fixtures, PESQ/STOI metrics, property tests (Hypothesis), and benchmarks.

- Kubernetes & Operations
  - Add NetworkPolicies, PodDisruptionBudget, liveness/readiness probes, resource/ephemeral storage limits, dedicated ServiceAccounts and RBAC.
  - Enforce no default namespace; add namespace labels/annotations policies; consider Gatekeeper/kyverno for cluster enforcement.

- Containers & Supply Chain
  - Run containers as non‑root users; drop capabilities by default; add healthcheck.
  - Enforce image verification in cluster (Cosign policy controller/Connaisseur); retain SBOMs and signatures; consider SLSA provenance.

- Security & Secrets
  - Add Semgrep SAST; adopt SOPS/Sealed‑Secrets for K8s secret management; clarify secret rotation and masking.

- Observability
  - Add Prometheus metrics, structured logging, tracing; dashboards in Grafana; error budgets and alerts.

- API & Inference
  - Define streaming contract (chunked OLA), backpressure, batching; auth and rate‑limit policies; CPU fallback; warm‑up and pin‑memory strategies.

- Documentation & DX
  - Expand README with image tag scheme (`cuda-<ver>`, `rocm-<ver>`), trainer usage (Hydra/argparse), and data curation guidance; add Make targets and dev runbook.
