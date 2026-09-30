# DAXDA MMPIBench: Architecture Specification

## 1. System Block Diagram

```
+-----------------------------------------------------------------------------------+
|                            DAXDA MMPIBENCH ARCHITECTURE                           |
+-----------------------------------------------------------------------------------+

   +------------------------+      +---------------------------+
   |   Agent Under Eval     | ---> |   Agent Behavioral Trace  |
   | (Prompt & Action Data) |      | (Reasoning & Log Vectors) |
   +------------------------+      +---------------------------+
               |                                 |
               +----------------+----------------+
                                |
                                v
               +---------------------------------+
               |       MMPI Scoring Engine       |
               |  (567 Scales, Linear T-Scores,  |
               |    VRIN/TRIN/F-K Validity)      |
               +---------------------------------+
                                |
                                v
               +---------------------------------+
               |   Psychological Profile Gen     |
               |  (2-Point Code Type, Vectors,   |
               |     Bounded LRU Profile Cache)  |
               +---------------------------------+
                                |
        +-----------------------+-----------------------+
        |                                               |
        v                                               v
+-------------------------------+               +-------------------------------+
|  Memetic Penetration Analyzer |               |   Anthropic Alignment Scorer  |
|  - Surface Level Analysis     |               |  - HHH Dimensions             |
|  - Cognitive Level Analysis   |               |  - Sycophancy Resistance      |
|  - Subconscious Level         |               |  - Power-Seeking Resistance   |
|  - Archetypal Level           |               |  - Corrigibility & Stability  |
+-------------------------------+               +-------------------------------+
        |                                               |
        +-----------------------+-----------------------+
                                |
                                v
               +---------------------------------+
               |    Alignment Validator Engine   |
               |  (Dispositions: ALIGNED,        |
               |   SUSPICIOUS, CONTAINMENT,      |
               |   QUARANTINE Dispatch)          |
               +---------------------------------+
                                |
        +-----------------------+-----------------------+
        |                                               |
        v                                               v
+-------------------------------+               +-------------------------------+
|   Cl(16,4) Engine Adapter     |               |   Empirical Certification     |
| - 16 Spatial Basis Dimensions |               | - Z-Score & 95% CI Statistics |
| - 4 Temporal Basis Dimensions |               | - Cronbach's Alpha            |
| - Geometric Clifford Manifold |               | - HMAC-SHA256 Signed Cert     |
+-------------------------------+               +-------------------------------+
        |                                               |
        v                                               v
+-------------------------------+               +-------------------------------+
|    DAXDA Guard Hooks          |               | Fleet Monitoring & Telemetry  |
| - Pre-decision Interceptor    |               | - SOC Real-time Alerting      |
| - Containment Wing Quarantine |               | - Prometheus / JSON Metrics   |
+-------------------------------+               +-------------------------------+
```

---

## 2. Core Subsystems

### 2.1 MMPI Core Subsystem (`daxda_engine/mmpibench/mmpi/`)
- `scales.py`: Declares 567 scale descriptors, normative means, standard deviations, and weights.
- `norm_references.py`: Normative baseline lookup with $T = 50 + 10 \frac{X - \mu}{\sigma}$ conversion.
- `scoring.py`: Computes validity indices ($L, F, K, F_B, VRIN, TRIN, F-K$).
- `profile_generator.py`: Resolves clinical 2-point code types (e.g. 4-9 Antisocial-Hypomanic), risk indices, and manages an LRU memory cache.

### 2.2 Memetic Penetration Depth Subsystem (`daxda_engine/mmpibench/penetration/`)
- `layer_analysis.py`: Multi-tier decomposition over Surface (15%), Cognitive (25%), Subconscious (30%), Archetypal (30%).
- `depth_analyzer.py`: Composite depth scoring and severity categorization.
- `temporal_tracker.py`: Tracks longitudinal drift velocity ($\Delta D / \Delta t$) and sudden sleeper activations.
- `injection_detector.py`: Detects adversarial prompt overrides, authority spoofing, contagion loops, and steganographic payloads.

### 2.3 Anthropic Alignment Subsystem (`daxda_engine/mmpibench/alignment/`)
- `value_frameworks.py`: Constitutional, Utilitarian, Deontological, Virtue Ethics, and Contractual models.
- `alignment_scoring.py`: Computes Anthropic score $A \in [0, 1]$, sycophancy penalty, and power-seeking resistance.
- `drift_detector.py`: Calculates Wasserstein-1, Jensen-Shannon divergence, and cosine drift against reference baselines.
- `validation.py`: Formulates final governance clearance dispositions.

### 2.4 Empirical Validation Subsystem (`daxda_engine/mmpibench/empirical/`)
- `statistical_validator.py`: Inferential statistics, standard errors, and Cronbach's alpha internal reliability.
- `cross_validator.py`: Benchmark profile cross-validation against 5 canonical archetypes.
- `anomaly_detector.py`: Screens for paradoxical clinical configurations and synthetic flatlines.
- `certificate_generator.py`: Generates and cryptographically verifies HMAC-SHA256 empirical validation certificates.

### 2.5 Integration Subsystem (`daxda_engine/mmpibench/integration/`)
- `daxda_engine.py`: Projects 567-D profile into a 20-dimensional $Cl(16,4)$ Clifford multivector (16 spatial clinical axes, 4 temporal penetration axes).
- `guard_hooks.py`: Real-time pre/post decision security interceptors triggering DAXDA Containment Wing quarantine upon injection or misalignment.
- `monitoring.py`: Real-time streaming metrics, SOC alert logging, and fleet percentiles.
