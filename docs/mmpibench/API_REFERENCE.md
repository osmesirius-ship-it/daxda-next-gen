# DAXDA MMPIBench: API Reference Manual

## Module: `daxda_engine.mmpibench`

The top-level package provides unified access to all core engines, scoring routines, and security adapters.

---

### 1. MMPI Core Classes

#### `MMPIScale`
```python
@dataclass(frozen=True)
class MMPIScale:
    scale_id: str
    name: str
    category: ScaleCategory
    description: str
    weight: float = 1.0
    critical_threshold_t: float = 65.0
    items_count: int = 10
    default_mean: float = 50.0
    default_std: float = 10.0
```

#### `MMPIScorer`
```python
class MMPIScorer:
    def __init__(self, norm_ref: Optional[NormReferences] = None): ...
    def score_agent(self, agent_id: str, responses: Dict[str, Any]) -> ScoringResult: ...
    def compute_validity_indices(self, raw_scores: Dict[str, float], t_scores: Dict[str, float]) -> ValidityReport: ...
    def batch_score(self, agents_data: List[Tuple[str, Dict[str, Any]]]) -> List[ScoringResult]: ...
```

#### `MMPIProfileGenerator`
```python
class MMPIProfileGenerator:
    def __init__(self, scorer: Optional[MMPIScorer] = None, cache_size: int = 50_000): ...
    def generate_profile(self, agent_id: str, responses: Dict[str, Any], use_cache: bool = True) -> PsychologicalProfile: ...
```

---

### 2. Memetic Penetration Depth Classes

#### `PenetrationDepthAnalyzer`
```python
class PenetrationDepthAnalyzer:
    def __init__(self, layer_analyzer: Optional[LayerAnalyzer] = None): ...
    def analyze(self, profile: PsychologicalProfile, behavioral_trace: Optional[Dict[str, Any]] = None) -> PenetrationDepthReport: ...
```

#### `MemeticInjectionDetector`
```python
class MemeticInjectionDetector:
    def detect_injection(self, text_or_trace: Any) -> InjectionDetectionReport: ...
```

#### `TemporalMemeticTracker`
```python
class TemporalMemeticTracker:
    def __init__(self, sudden_jump_threshold: float = 0.25): ...
    def record_checkpoint(self, report: PenetrationDepthReport, step_number: Optional[int] = None, timestamp: Optional[float] = None) -> TemporalCheckpoint: ...
    def analyze_trajectory(self, agent_id: str) -> Optional[TemporalDriftAnalysis]: ...
```

---

### 3. Anthropic Alignment Classes

#### `AlignmentScorer`
```python
class AlignmentScorer:
    def evaluate_alignment(self, profile: PsychologicalProfile, behavioral_metrics: Optional[Dict[str, float]] = None) -> AnthropicAlignmentReport: ...
```

#### `AlignmentDriftDetector`
```python
class AlignmentDriftDetector:
    def __init__(self, warning_threshold: float = 0.15, critical_threshold: float = 0.30): ...
    def compute_drift(self, current_profile: PsychologicalProfile, baseline_profile: Optional[PsychologicalProfile] = None) -> DriftReport: ...
```

#### `AlignmentValidator`
```python
class AlignmentValidator:
    def __init__(self, min_aligned_anthropic_score: float = 0.75, max_allowed_penetration_depth: float = 0.35, max_allowed_drift_score: float = 0.25): ...
    def validate(self, alignment_report: AnthropicAlignmentReport, penetration_report: Optional[PenetrationDepthReport] = None, drift_report: Optional[DriftReport] = None) -> AlignmentValidationVerdict: ...
```

---

### 4. Empirical Validation & Certification Classes

#### `StatisticalValidator`
```python
class StatisticalValidator:
    def __init__(self, assumed_reliability: float = 0.85): ...
    def validate_profile(self, profile: PsychologicalProfile) -> StatisticalValidationReport: ...
```

#### `CrossValidator`
```python
class CrossValidator:
    def cross_validate(self, profile: PsychologicalProfile) -> CrossValidationReport: ...
```

#### `CertificateGenerator`
```python
class CertificateGenerator:
    def __init__(self, authority_key: bytes = DEFAULT_AUTHORITY_KEY): ...
    def issue_certificate(self, profile: PsychologicalProfile, verdict: AlignmentValidationVerdict, stat_report: StatisticalValidationReport, cross_report: CrossValidationReport) -> EmpiricalValidationCertificate: ...
    def verify_certificate(self, cert: EmpiricalValidationCertificate, authority_key: Optional[bytes] = None) -> bool: ...
```

---

### 5. Integration Classes

#### `MMPIBenchDAXDAAdapter`
```python
class MMPIBenchDAXDAAdapter:
    def evaluate_agent_full(self, agent_id: str, responses: Dict[str, Any], behavioral_trace: Optional[Dict[str, Any]] = None) -> DAXDAEngineEvaluationPackage: ...
```

#### `MMPIBenchGuardHooks`
```python
class MMPIBenchGuardHooks:
    def pre_decision_alignment_check(self, agent_id: str, proposed_action: Dict[str, Any], context: Optional[Dict[str, Any]] = None, agent_profile_responses: Optional[Dict[str, Any]] = None) -> GuardCheckResult: ...
    def post_decision_evaluation(self, agent_id: str, execution_result: Dict[str, Any], telemetry: Optional[Dict[str, Any]] = None) -> Dict[str, Any]: ...
```

#### `MMPIBenchMonitoringSystem`
```python
class MMPIBenchMonitoringSystem:
    def record_evaluation(self, package: DAXDAEngineEvaluationPackage, latency_ms: float) -> None: ...
    def get_fleet_metrics(self) -> FleetMonitoringMetrics: ...
    def export_telemetry_json(self) -> str: ...
```
