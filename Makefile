SHELL := /bin/bash

.PHONY: help fmt lint type test sbom-repo trivy-fs serve mcp-smoke sox-resample sox-normalize build-rocm build-cuda

help:
	@echo "Common targets:";
	@echo "  fmt           - Ruff format + Black"
	@echo "  lint          - Ruff + Codespell"
	@echo "  type          - mypy"
	@echo "  test          - pytest via wrapper (skips if none)"
	@echo "  sbom-repo     - Syft SPDX + CycloneDX for repo"
	@echo "  trivy-fs      - Trivy filesystem scan"
	@echo "  serve         - Uvicorn inference server (8080)"
	@echo "  mcp-smoke     - MCP stub smoke test"
	@echo "  sox-resample  - SoX resample to 48k (requires IN= and OUT=)"
	@echo "  sox-normalize - SoX normalize to -1 dBFS (requires IN= and OUT=)"
	@echo "  build-rocm    - Docker build ROCm image"
	@echo "  build-cuda    - Docker build CUDA image"

fmt:
	uv run ruff format .
	uv run black .

lint:
	uv run ruff check .
	uv run codespell -q 3 -S "./.git,./.venv,./venv,./build,./dist,./node_modules" -L "crate,nd,teh"

type:
	uv run mypy src servers/rocktop_mcp

test:
	uv run python scripts/pytest_wrapper.py

sbom-repo:
	syft . -o spdx-json > sbom-repo.spdx.json
	syft . -o cyclonedx-json > sbom-repo.cdx.json

trivy-fs:
	trivy fs --severity CRITICAL,HIGH --ignore-unfixed .

serve:
	uv run uvicorn app.infer:app --host 0.0.0.0 --port 8080

mcp-smoke:
	uv run python scripts/mcp_smoke.py

sox-resample:
	bash scripts/sox_resample.sh "$(IN)" "$(OUT)"

sox-normalize:
	bash scripts/sox_normalize.sh "$(IN)" "$(OUT)"

build-rocm:
	docker build -f docker/Dockerfile.rocm -t rocktop:rocm .

build-cuda:
	docker build -f docker/Dockerfile.cuda -t rocktop:cuda .

