# DAXDA DA13 Distributed GPU Validator Cluster — Deployment Guide
## Kubernetes Helm, Docker Compose & Ray Distributed Cluster Deployment

[![Deploy Tool](https://img.shields.io/badge/Kubernetes-Helm%20v3-blue.svg)](helm/da13-validator/)
[![Container](https://img.shields.io/badge/Docker-Dockerfile.da13-brightgreen.svg)](Dockerfile.da13)

---

## 1. Hardware & System Prerequisites

| Component | Minimum Specification | Production Recommended | Maximum Scaled |
|---|---|---|---|
| **Head Node CPU** | 8 Cores (x86_64 / ARM64) | 16 Cores | 32 Cores |
| **Head Node RAM** | 16 GB | 32 GB | 128 GB |
| **GPU Workers** | 1 Worker | 4 to 8 Workers | Up to 1024 Workers |
| **GPU per Worker** | 1 GPU (NVIDIA T4 / A10) | 1 to 4 GPUs (A100 / H100) | 8 GPUs per Node |
| **GPU VRAM** | 8 GB | 16 GB+ | 80 GB |
| **Network** | 10 Gbps | 25 Gbps+ | 100 Gbps InfiniBand |
| **Storage** | 100 GB SSD | 1 TB NVMe | 10 TB NVMe |

---

## 2. Kubernetes Helm Deployment

The official Helm chart is located in [`helm/da13-validator/`](file:///Users/user/daxda%20next%20gen/DAXDA-NEXTGEN/daxda-next-gen/helm/da13-validator/).

### Step 1: Add or Review Helm Chart
```bash
cd /path/to/daxda-next-gen
helm lint helm/da13-validator
```

### Step 2: Configure Secrets and Values
Review and adjust [`helm/da13-validator/values.yaml`](file:///Users/user/daxda%20next%20gen/DAXDA-NEXTGEN/daxda-next-gen/helm/da13-validator/values.yaml):
```yaml
replicaCount:
  head: 1
  minWorkers: 4
  maxWorkers: 1024

resources:
  worker:
    limits:
      nvidia.com/gpu: 1
```

### Step 3: Install the Chart
```bash
# Create dedicated namespace
kubectl create namespace daxda-governance

# Install Helm release
helm install da13-validator helm/da13-validator -n daxda-governance
```

### Step 4: Verify Cluster Pods & GPU Affinity
```bash
kubectl get pods -n daxda-governance -o wide
kubectl logs -f deployment/da13-validator-head -n daxda-governance
```

---

## 3. Docker & Docker Compose Deployment

### Option A: Standalone Docker Run
```bash
# Build production image
docker build -t daxda/da13-validator:2.0.0 -f Dockerfile.da13 .

# Run head node
docker run -d \
  --name da13-head \
  --gpus all \
  -p 8000:8000 \
  -p 9090:9090 \
  -p 8765:8765 \
  -e DA13_INITIAL_WORKERS=4 \
  daxda/da13-validator:2.0.0
```

### Option B: Docker Compose
```bash
docker compose -f docker-compose.da13.yml up -d
```
Verify container status:
```bash
docker compose -f docker-compose.da13.yml ps
```

---

## 4. Ray Cluster Native Integration

When deploying directly on physical GPU nodes using native Ray:

### 1. Launch Head Node:
```bash
ray start --head --port=6379 --num-cpus=16 --num-gpus=0
```

### 2. Connect GPU Worker Nodes:
```bash
ray start --address='<HEAD_NODE_IP>:6379' --num-cpus=8 --num-gpus=8
```

### 3. Launch DA13 Cluster Manager in Ray Environment:
```bash
export DA13_RAY_ADDRESS="auto"
python3 tools/run_da13_benchmark.py
```
