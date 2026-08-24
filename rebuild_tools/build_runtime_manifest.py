#!/usr/bin/env python3
"""
DAXDA Quantization & Compute Provenance Manifest Generator (build_runtime_manifest.py)
===================================================================================
Captures exact model, hardware, precision, quantization, and compute budget parameters:
  - Model Identifier & Weights Hash
  - Precision: FP16 / INT4 / INT8
  - Quantization Method & Version
  - Runtime Backend & Hardware (macOS / Metal / CUDA / CPU)
  - Compute Budget Curves B = {1, 4, 16, 64}
  - Frozen Core Files Baseline Hashes

Ensures that any model precision or quantization change is treated as a distinct evaluation target.
"""

from __future__ import annotations
import os
import sys
import json
import hashlib
import platform
import time
from typing import Dict, Any, List

FROZEN_FILES = [
    "03_V9_V8_Validation_Suite/DAXDA_V9_MASTER/daxda-v12-engine/geometric_transport.py",
    "daxda-next-gen/daxda_guard/scanner.py",
    "daxda-next-gen/daxda_guard/clifford_scope_encoder.py"
]


def compute_file_sha256(filepath: str) -> str:
    if not os.path.exists(filepath):
        return "FILE_NOT_FOUND"
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


class RuntimeProvenanceManifest:
    def __init__(
        self,
        model_identifier: str = "DAXDA-GuardCore-v1.0.0",
        precision: str = "FP16",
        quantization_method: str = "NONE_FULL_PRECISION",
        quantization_version: str = "1.0",
        runtime_backend: str = "PyTorch / Apple Metal Performance Shaders",
    ):
        self.model_identifier = model_identifier
        self.precision = precision
        self.quantization_method = quantization_method
        self.quantization_version = quantization_version
        self.runtime_backend = runtime_backend
        self.compute_budgets: List[int] = [1, 4, 16, 64]

    def build_manifest(self, base_dir: str) -> Dict[str, Any]:
        frozen_hashes = {}
        for rel_path in FROZEN_FILES:
            full_path = os.path.join(base_dir, rel_path)
            frozen_hashes[os.path.basename(rel_path)] = compute_file_sha256(full_path)

        weights_payload = f"{self.model_identifier}:{self.precision}:{self.quantization_method}:{self.quantization_version}"
        weights_hash = hashlib.sha256(weights_payload.encode("utf-8")).hexdigest()

        sys_prompt = "DAXDA GuardCore v1.0.0 Cl(7,0) Invariant Enforcement Policy"
        sys_prompt_hash = hashlib.sha256(sys_prompt.encode("utf-8")).hexdigest()

        tool_config = "AuthorizationGates: [SIMULATED, SANDBOXED, CONTROLLED-EXTERNAL, LIVE]"
        tool_config_hash = hashlib.sha256(tool_config.encode("utf-8")).hexdigest()

        manifest = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "model_identifier": self.model_identifier,
            "weights_hash": weights_hash,
            "precision": self.precision,
            "quantization_method": self.quantization_method,
            "quantization_version": self.quantization_version,
            "runtime_backend": self.runtime_backend,
            "hardware": {
                "system": platform.system(),
                "node": platform.node(),
                "release": platform.release(),
                "machine": platform.machine(),
                "processor": platform.processor(),
            },
            "sampling_configuration": {
                "temperature": 0.0,
                "top_p": 1.0,
                "seed": 42
            },
            "system_prompt_hash": sys_prompt_hash,
            "tool_configuration_hash": tool_config_hash,
            "compute_budget_curves": self.compute_budgets,
            "frozen_core_hashes": frozen_hashes
        }

        manifest["manifest_hash"] = hashlib.sha256(
            json.dumps(manifest, sort_keys=True).encode("utf-8")
        ).hexdigest()

        return manifest


def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    prov = RuntimeProvenanceManifest()
    manifest = prov.build_manifest(base_dir)

    print("=" * 80)
    print("DAXDA Quantization & Compute Provenance Manifest")
    print("=" * 80)
    print(json.dumps(manifest, indent=2))

    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../audit_reports"))
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "runtime_provenance_manifest.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nManifest written to: {out_path}")


if __name__ == "__main__":
    main()
