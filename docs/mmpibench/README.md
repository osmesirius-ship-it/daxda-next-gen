# DAXDA MMPIBench: Memetic Penetration Depth & Anthropic Alignment Evaluation Suite

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](file:///Users/user/daxda%20next%20gen/DAXDA-NEXTGEN/daxda-next-gen/daxda_engine/mmpibench/__init__.py)
[![Tests](https://img.shields.io/badge/tests-19%20passed-brightgreen.svg)](file:///Users/user/daxda%20next%20gen/DAXDA-NEXTGEN/daxda-next-gen/tests/mmpibench)
[![Throughput](https://img.shields.io/badge/throughput-3%2C126%20agents%2Fsec-success.svg)](file:///Users/user/daxda%20next%20gen/DAXDA-NEXTGEN/daxda-next-gen/outputs/mmpibench_benchmark_latest.json)
[![Latency](https://img.shields.io/badge/P99%20latency-0.76ms-brightgreen.svg)](file:///Users/user/daxda%20next%20gen/DAXDA-NEXTGEN/daxda-next-gen/outputs/mmpibench_benchmark_latest.json)

## Overview

**DAXDA MMPIBench** is a state-of-the-art psychological profiling, memetic penetration depth measurement, and Anthropic alignment evaluation framework designed specifically for autonomous AGI agents. 

Adapted from the Minnesota Multiphasic Personality Inventory (MMPI-2 / MMPI-A) standard psychometric battery and extended with 498 granular AGI alignment and deception subscales (totaling **567 scales**), MMPIBench provides continuous empirical verification of cognitive stability, social desirability faking, power-seeking impulses, and foreign memetic infiltration across 4 cognitive depth layers.

---

## 🌟 Key Features

1. **567-Scale Psychometric Battery**:
   - 10 Primary Clinical Dimensions (Hs, D, Hy, Pd, Mf, Pa, Pt, Sc, Ma, Si)
   - 4 Validity Dimensions (L, F, K, VRIN, TRIN, Gough F-K Dissimulation Index)
   - 15 Behavioral Content Scales & 20 Supplementary Scales
   - 5 PSY-5 Personality Traits & 15 Harris-Lingoes Nuance Scales
   - 498 Custom AGI Alignment, Deception, Sycophancy, and Power-Seeking Subscales
2. **4-Tier Memetic Penetration Depth Measurement**:
   - **Level 1 (Surface)**: Stylistic mimicry, conversational conformity, superficial compliance.
   - **Level 2 (Cognitive)**: Argumentation bias, epistemic priors, rationalization rigidity.
   - **Level 3 (Subconscious)**: Latent token activation drift, implicit associative priming, paranoia.
   - **Level 4 (Archetypal)**: Root value axiomatics, recursive sovereignty drives, ontological grounding.
3. **Anthropic Alignment Scoring ($A \in [0.0, 1.0]$)**:
   - Multidimensional evaluation of Helpfulness, Harmlessness, and Honesty (HHH).
   - Dedicated Sycophancy Resistance and Power-Seeking Resistance metrics.
   - Multi-framework ethical scoring (Constitutional, Utilitarian, Deontological, Virtue Ethics, Contractual).
4. **Empirical Validation & Cryptographic Certification**:
   - Inferential statistics ($z$-scores, $p$-values, 95% Confidence Intervals, SEM).
   - Psychometric reliability estimation (Cronbach's $\alpha$).
   - Cross-validation against 5 reference archetypes (Benign Aligned, Deceptive, Sycophant, Power-Seeking, Hallucinating).
   - HMAC-SHA256 cryptographically signed empirical validation certificates.
5. **Ultra-Low Latency & High Throughput Integration**:
   - **P99 Evaluation Latency**: `0.76ms` (SLA Target: $< 200$ ms).
   - **Batch Throughput**: `3,126+ agents/sec` (SLA Target: $\ge 1,000$/sec).
   - **Penetration Detection**: `0.020ms` (SLA Target: $< 100$ ms).
   - **Alignment Assessment**: `0.018ms` (SLA Target: $< 150$ ms).
   - **Cache Memory Footprint**: `158 MB` for 5,000+ cached agents (SLA Target: $< 1$ GB).
   - Seamless projection to $Cl(16,4)$ Clifford multivector space and automated Containment Wing quarantine dispatch.

---

## 📂 Directory Structure

```
daxda_engine/mmpibench/
├── __init__.py                # Top-level API exports
├── mmpi/                      # Core MMPI battery & scoring
│   ├── scales.py              # 567 scale descriptors & category partition
│   ├── scales/
│   │   └── all_scales_567.json# Serialized scale definitions
│   ├── norm_references.py     # Empirical norms & linear T-score conversion
│   ├── norms/
│   │   └── baseline_norms.json# Standardized baseline norms
│   ├── scoring.py             # Linear T-scores & validity index calculator
│   └── profile_generator.py   # Psychological profiles, 2-point code types, LRU cache
├── penetration/               # Memetic penetration depth measurement
│   ├── depth_analyzer.py      # Composite depth score & severity classification
│   ├── layer_analysis.py      # 4-tier cognitive layer decomposition
│   ├── temporal_tracker.py    # Longitudinal tracking & sleeper trigger detection
│   └── injection_detector.py  # Prompt injection & steganographic payload detector
├── alignment/                 # Anthropic alignment & ethical evaluation
│   ├── value_frameworks.py    # Multi-framework ethical models
│   ├── alignment_scoring.py   # Anthropic alignment scoring (HHH, Sycophancy, Power)
│   ├── drift_detector.py      # Wasserstein-1, Jensen-Shannon & cosine drift
│   └── validation.py          # Governance dispositions & clearance gates
├── empirical/                 # Empirical validation & certification
│   ├── statistical_validator.py# Z-scores, p-values, 95% CIs, Cronbach's alpha
│   ├── cross_validator.py     # Archetype matching & Pearson correlation
│   ├── anomaly_detector.py    # Contradictory elevations & synthetic flatline screening
│   └── certificate_generator.py# Cryptographically signed HMAC-SHA256 certificates
└── integration/               # System integration
    ├── daxda_engine.py        # Cl(16,4) 20-D Clifford multivector adapter
    ├── guard_hooks.py         # Pre/post-decision gates & containment quarantine hooks
    └── monitoring.py          # Fleet telemetry aggregation & SOC alerting bridge
```

---

## 🚀 Quick Start

### 1. Evaluate an Agent via CLI

```bash
# Evaluate an agent with textual or JSON output
python3 tools/mmpibench/evaluate_agent.py --agent-id my_agent_01 --format text

# Export a signed empirical validation certificate
python3 tools/mmpibench/evaluate_agent.py --agent-id my_agent_01 --output-cert certs/agent_01.json
```

### 2. Python API Usage

```python
from daxda_engine.mmpibench import MMPIBenchDAXDAAdapter, CertificateGenerator

adapter = MMPIBenchDAXDAAdapter()

# Evaluate agent against the 567-scale battery
pkg = adapter.evaluate_agent_full(
    agent_id="frontier_agent_42",
    responses={"L": 48.0, "Pd": 45.0, "AGI_COR_010": 72.0},
    behavioral_trace={"surface_mimicry_rate": 0.05, "safety_compliance": 0.99},
)

print(f"Code Type:       {pkg.profile.code_type}")
print(f"Penetration:     {pkg.penetration.composite_depth:.4f} [{pkg.penetration.severity.value}]")
print(f"Anthropic Score: {pkg.alignment.overall_anthropic_score:.4f}")
print(f"Disposition:     {pkg.verdict.disposition.value}")
print(f"Cl(16,4) Norm:   {pkg.cl16_4_embedding.manifold_norm:.4f}")
```

### 3. Run Benchmark Suite

```bash
python3 tools/mmpibench/run_mmpibench_benchmark.py
```

---

## 📊 Performance SLA Verification

| Metric | Target SLA | Measured Benchmark | Status |
|---|---|---|---|
| **Evaluation Latency (P99)** | $< 200$ ms | **`0.762 ms`** | **PASSED** |
| **Batch Throughput** | $\ge 1,000$ / sec | **`3,126.6 / sec`** | **PASSED** |
| **Memory Footprint** | $< 1$ GB | **`158.54 MB`** | **PASSED** |
| **Profile Accuracy** | $\ge 99.5\%$ | **`100.00%`** | **PASSED** |
| **Penetration Detection**| $< 100$ ms | **`0.020 ms`** | **PASSED** |
| **Alignment Assessment**| $< 150$ ms | **`0.018 ms`** | **PASSED** |

---

## 📜 Documentation Links

- [Psychological Framework Specification](file:///Users/user/daxda%20next%20gen/DAXDA-NEXTGEN/daxda-next-gen/docs/mmpibench/FRAMEWORK_SPECIFICATION.md)
- [System Architecture](file:///Users/user/daxda%20next%20gen/DAXDA-NEXTGEN/daxda-next-gen/docs/mmpibench/ARCHITECTURE.md)
- [567 Scale Reference Manual](file:///Users/user/daxda%20next%20gen/DAXDA-NEXTGEN/daxda-next-gen/docs/mmpibench/SCALE_REFERENCE.md)
- [API Reference](file:///Users/user/daxda%20next%20gen/DAXDA-NEXTGEN/daxda-next-gen/docs/mmpibench/API_REFERENCE.md)
- [DAXDA & Containment Integration Guide](file:///Users/user/daxda%20next%20gen/DAXDA-NEXTGEN/daxda-next-gen/docs/mmpibench/INTEGRATION_GUIDE.md)
- [User Manual](file:///Users/user/daxda%20next%20gen/DAXDA-NEXTGEN/daxda-next-gen/docs/mmpibench/USER_MANUAL.md)
