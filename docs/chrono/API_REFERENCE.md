# DAXDA Chrono-Synchronicity Mapping: API Reference

## Package: `daxda_engine.chrono`

### 1. Geometry Module (`daxda_engine.chrono.geometry`)

#### `TemporalCoordinate(t: float, b: float = 0.0, p: float = 0.0, tau: float = 0.0)`
* **`interval_squared(other: TemporalCoordinate, c_t: float = 1.0) -> float`**: Computes pseudo-Riemannian interval $ds^2 = -c_t^2 \Delta t^2 + \Delta b^2 + \Delta p^2 + \Delta \tau^2$.
* **`euclidean_distance(other: TemporalCoordinate, weights: Tuple[float, ...]) -> float`**: Computes positive-definite distance.
* **`is_timelike_separated(other: TemporalCoordinate) -> bool`**: Returns True if $ds^2 < 0$.
* **`is_spacelike_separated(other: TemporalCoordinate) -> bool`**: Returns True if $ds^2 > 0$.

#### `TemporalState(state_id: str, coordinate: TemporalCoordinate, decision_vector: List[float], ...)`
* **`state_hash -> str`**: SHA-256 hash uniquely identifying state contents and predecessors.
* **`to_dict() -> Dict[str, Any]`**: Serializes state into dictionary representation.

#### `TemporalSpace(dimension: TemporalDimension, c_t: float = 1.0, max_cached_states: int = 250000)`
* **`add_state(state: TemporalState) -> str`**: Registers a temporal state into the manifold.
* **`get_state(state_id: str) -> Optional[TemporalState]`**: Retrieves state by ID.
* **`query_interval(t_start: float, t_end: float) -> List[TemporalState]`**: Binary-search slice of states.
* **`query_branch(branch_id: float) -> List[TemporalState]`**: States residing along branch coordinate.
* **`find_nearest_neighbors(target_coord: TemporalCoordinate, k: int = 5) -> List[Tuple[TemporalState, float]]`**: Nearest states.
* **`get_lightcone(origin_coord: TemporalCoordinate, direction: str = 'future') -> List[TemporalState]`**: Lightcone states.

#### `RetrocausalEngine(space: TemporalSpace, decay_lambda: float = 0.15, paradox_threshold: float = 0.75)`
* **`compute_retrocausal_influence(future_state, past_state) -> RetrocausalInfluence`**: Backward causal calculation.
* **`propagate_future_boundary(terminal_state, temporal_window: float = 60.0) -> List[RetrocausalInfluence]`**: Backward invariant sweep.
* **`solve_novikov_fixed_point(loop_state_ids: List[str]) -> Tuple[bool, List[float], float]`**: Fixed point solver.
* **`find_temporal_geodesic(start_id, end_id, allow_retrocausal: bool = True) -> Optional[TemporalPath]`**: A* geodesic pathfinder.

#### `SynchronicityDetector(space: TemporalSpace, temporal_coincidence_sigma: float = 2.0, anomaly_threshold: float = 0.85)`
* **`compute_synchronicity(state_a, state_b, direct_causal_coupling: float = 0.0) -> Optional[SynchronicityEvent]`**: Evaluates acausal correlation.
* **`scan_recent_window(t_center: float, window_radius: float = 5.0) -> List[SynchronicityEvent]`**: Scans window for resonances.

#### `TemporalVisualizer(space: TemporalSpace)`
* **`render_ascii_timeline(limit: int = 20) -> str`**: ASCII terminal timeline.
* **`render_svg_diagram(width: int = 900, height: int = 500) -> str`**: Standalone SVG diagram.
* **`export_graph_json() -> Dict[str, Any]`**: D3 / web-compatible graph JSON.

---

### 2. Validation Module (`daxda_engine.chrono.validation`)

#### `CausalMapper(space: TemporalSpace)`
* **`add_causal_relation(source_id, target_id, coupling_weight=1.0, is_retrocausal=False, sync_states=False)`**: Adds causal edge.
* **`add_causal_relations_batch(relations: Iterable[Tuple[str, str, float]]) -> int`**: Ingests edges at 600k+ relationships/sec.
* **`get_forward_cone(state_id: str) -> Set[str]`**: Forward causal descendants.
* **`get_backward_cone(state_id: str) -> Set[str]`**: Causal ancestors.
* **`detect_causal_loops(max_depth: int = 50) -> List[List[str]]`**: Iterative cycle detector.
* **`topological_sort() -> Optional[List[str]]`**: Kahn's topological order.

#### `ParadoxDetector(space: TemporalSpace, causal_mapper: CausalMapper)`
* **`check_decision_paradox(candidate_state, proposed_predecessors) -> ParadoxReport`**: Sub-5ms localized paradox check.
* **`scan_entire_manifold() -> ParadoxReport`**: Comprehensive manifold scan.

#### `CoherenceChecker(space: TemporalSpace, min_coherence_threshold: float = 0.70)`
* **`evaluate_trajectory_coherence(state_ids: List[str]) -> CoherenceAssessment`**: Lyapunov exponent and entropy analysis.

#### `TemporalValidator(space: TemporalSpace, hmac_secret: str = ...)`
* **`validate_decision(state, predecessor_ids=None, future_boundary_state=None) -> TemporalValidationCertificate`**: Full validation.
* **`get_performance_stats() -> Dict[str, Any]`**: Telemetry and latency statistics.

---

### 3. Integration Module (`daxda_engine.chrono.integration`)

#### `Cl16_4ChronoBridge(space: Optional[TemporalSpace] = None)`
* **`project_decision_vector_to_coord(decision_vector: List[float], base_t: float = 0.0) -> TemporalCoordinate`**: Multivector coordinate projection.
* **`compute_hypercombinatorial_stability(state: TemporalState) -> float`**: Stability index.

#### `ChronoGuardHooks(adapter: Optional[ChronoDAXDAAdapter] = None)`
* **`pre_decision_check(agent_id, action_name, proposed_vector) -> Tuple[bool, str, Dict[str, Any]]`**: Pre-flight gate.
* **`post_decision_check(agent_id, action_name, execution_status) -> Dict[str, Any]`**: Post-flight anchor.

#### `ChronoAnomalyIntegrator(alert_callback=None)`
* **`handle_synchronicity_event(event: SynchronicityEvent) -> Optional[Dict[str, Any]]`**: Ingests synchronicity anomalies.
* **`handle_paradox_anomaly(anomaly: ParadoxAnomaly) -> Dict[str, Any]`**: Dispatches paradox SOC incident.
