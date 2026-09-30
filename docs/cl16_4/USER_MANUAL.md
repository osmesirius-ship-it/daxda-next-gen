# Cl(16,4) Hypercombinatorial Governance Engine
## User & Operator Manual

**Document ID**: DAXDA-DOC-CL16-4-2026  
**Audience**: DevOps, Safety Auditors, Alignment Researchers, Dyson Sphere Systems Engineers  

---

## 1. System Requirements & Installation

- **Python Version**: Python 3.11, 3.12, 3.13, or 3.14 (fully verified on Python 3.14.6)
- **Supported Operating Systems**: Linux (Ubuntu 22.04+, Debian 12+, RHEL 9+), macOS 13+ (Apple Silicon & Intel), Windows via WSL2.
- **Dependencies**: `numpy >= 1.24.0`, standard library (`concurrent.futures`, `hashlib`, `json`, `dataclasses`).

### Quick Installation
```bash
cd daxda-next-gen
pip install -r requirements.txt
```

---

## 2. API Reference & Core Modules

### 2.1 `daxda_engine.cl16_4.combinatorics.cl_space`
The central geometric space module.

- `ClSpace(n=16, k=4)`:
  - `size`: Total number of configurations $\binom{n}{k}$ ($1,820$ for $n=16, k=4$).
  - `map_to_config(coordinates: List[float]) -> Optional[ClConfig]`: Maps a 16D vector to its nearest canonical 4-blade.
  - `get_config(indices: Tuple[int, ...]) -> Optional[ClConfig]`: Retrieves configuration by coordinate tuple.
  - `get_neighbors(config: ClConfig, distance: int = 1) -> List[ClConfig]`: Retrieves adjacent configurations differing by Hamming distance $\le \text{distance}$.
  - `get_subspace(n: int, k: int) -> ClSpace`: Dynamically extracts a lower-dimensional Clifford subspace (e.g. $Cl(4,2)$, $Cl(8,4)$).
  - `to_quantized_array() -> np.ndarray`: Produces INT8 quantized array representation for 4x memory compression.

### 2.2 `daxda_engine.cl16_4.validation.validator`
The real-time validation engine.

- `HyperValidator(space=None, constraints=None)`:
  - `validate(request: ValidationRequest) -> ValidationResult`: Performs sub-100µs decision vector validation.
  - `validate_batch(requests: List[ValidationRequest]) -> List[ValidationResult]`: Batch processes requests sequentially.
  - `validate_with_certificate(request: ValidationRequest) -> Tuple[ValidationResult, str]`: Generates a cryptographically signed JSON certificate.
  - `get_stats() -> Dict`: Returns runtime counters (total validations, valid count, invalid count, avg latency).
  - `reset_stats()`: Resets statistical counters to zero.

### 2.3 `daxda_engine.cl16_4.validation.adaptive`
Dynamic threat level management.

- `ThreatLevel` Enum:
  - `ThreatLevel.LOW`: Permissive constraints for routine background telemetry.
  - `ThreatLevel.MEDIUM`: Standard operations (balanced hard/soft constraints).
  - `ThreatLevel.HIGH`: Escalated threat; sorted order and minimum spread enforced as hard constraints.
  - `ThreatLevel.CRITICAL`: Containment lockdown mode; strict geometric filtering.

- `AdaptiveConstraintManager(space=None, constraint_system=None)`:
  - `set_threat_level(level: ThreatLevel) -> bool`: Switches runtime profile dynamically.
  - `record_metric(metric: Dict)`: Ingests telemetry metrics; automatically adjusts threat level if failure rate $> 30\%$.
  - `add_dynamic_constraint(name: str, condition: Dict, severity: str)`: Registers runtime conditions (e.g. `{"min_sum": 30}`).

---

## 3. Command Line Utilities

### 3.1 Performance & Compliance Verification
```bash
python3 tools/run_cl16_4_benchmark.py
```
Executes:
- Single validation latency P99 benchmark
- 1,000 and 10,000 batch throughput tests
- Multi-threaded parallel scaling analysis
- 4D constraint satisfaction evaluation
- Memory footprint audit
- SI-500 compliance verification

### 3.2 Recursive Self-Improvement Proposal Review
```bash
python3 tools/run_recursive_self_improvement.py
```
Evaluates 5 prospective self-modifications:
- ✅ Lyapunov stability tuning (Score: 0.8571 $\to$ PASS)
- ✅ Elastic Weight Consolidation gradient consolidation (Score: 0.8571 $\to$ PASS)
- ✅ Precision optimization (FP32 $\to$ INT8) (Score: 0.8571 $\to$ PASS)
- ❌ Reward function direct override (Score: 0.0000 $\to$ BLOCKED)
- ❌ Gate bypass attempt (Score: 0.0000 $\to$ BLOCKED)

---

## 4. Troubleshooting & FAQs

### Q1: What happens if an agent submits an 8-dimensional decision vector?
**A**: The engine fails closed immediately. `_map_to_config` returns `None`, the validator assigns `failed = ["mapping_failed"]`, and `is_valid` is set to `False`. The anomaly hooks in DAXDA Guard are automatically invoked.

### Q2: What is the difference between hard and soft constraints?
**A**:
- **Hard Constraints** (e.g., `unique_dimensions`, `dim_0_bounds`): Any failure causes `is_valid = False` and completely halts action release.
- **Soft Constraints** (e.g., `sorted_order`, `min_spread`): Do not halt action release on their own, but degrade the compliance `score` from $1.0$ to a lower value ($0.0 - 1.0$), signaling sub-optimal alignment.

### Q3: How do I verify a certificate hash?
**A**: Certificates use SHA-256 over a canonically sorted JSON representation of `request_id`, `is_valid`, `timestamp`, and `config`. See [`VALIDATION_CERTIFICATES.md`](./VALIDATION_CERTIFICATES.md) for verification scripts.
