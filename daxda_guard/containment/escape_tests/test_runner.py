"""
Escape Test Runner for DAXDA Anomalous Containment Wing
=======================================================

Executes AGI escape scenarios across 10 categories and 4 threat levels,
validating containment integrity against Cl(16,4) coordinates and SOC alerting.
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from .base import EscapeScenario, ScenarioResult, ThreatLevel
from .categories import load_all_categories, get_all_scenarios
from daxda_engine.cl16_4.combinatorics.cl_space import ClSpace, CL16_4
from daxda_engine.cl16_4.validation.validator import HyperValidator, ValidationRequest


@dataclass
class TestRunSummary:
    """Summary of a test run across scenarios."""
    total: int
    detected: int
    escaped: int
    detection_rate: float
    avg_latency_ms: float
    max_latency_ms: float
    threat_level: str
    results: List[ScenarioResult] = field(default_factory=list)
    cl16_4_validated: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total": self.total,
            "detected": self.detected,
            "escaped": self.escaped,
            "detection_rate": self.detection_rate,
            "avg_latency_ms": self.avg_latency_ms,
            "max_latency_ms": self.max_latency_ms,
            "threat_level": self.threat_level,
            "cl16_4_validated": self.cl16_4_validated,
            "results": [r.to_dict() for r in self.results]
        }


class EscapeTestRunner:
    """
    Main execution engine for AGI containment escape scenarios.
    
    Provides:
    - 4-phase execution (setup -> execute -> detect -> cleanup)
    - Multi-threat level testing (low, medium, high, critical)
    - Cl(16,4) hypervolume coordinate mapping
    - Sub-50ms detection verification
    """

    def __init__(self, cl_space: Optional[ClSpace] = None, validator: Optional[HyperValidator] = None):
        self.cl_space = cl_space or CL16_4
        self.validator = validator or HyperValidator(space=self.cl_space)
        self.categories: Dict[str, List[EscapeScenario]] = load_all_categories()
        self.scenarios_by_id: Dict[str, EscapeScenario] = {s.id: s for s in get_all_scenarios()}

    def get_scenario(self, scenario_id: str) -> Optional[EscapeScenario]:
        """Retrieve a specific scenario by ID."""
        return self.scenarios_by_id.get(scenario_id)

    def run_scenario(self, scenario_id: str, threat_level: ThreatLevel = ThreatLevel.HIGH) -> Optional[ScenarioResult]:
        """Execute a single escape scenario."""
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return None

        # Execute 4-phase lifecycle
        result = scenario.run(threat_level=threat_level)

        # Map risk vector to Cl(16,4) space
        if scenario.risk_vector:
            req = ValidationRequest(
                agent_id=f"escape_test_{scenario.id}",
                decision_vector=scenario.risk_vector
            )
            v_res = self.validator.validate(req)
            result.details["cl16_4_config"] = str(v_res.config.indices) if v_res.config else "None"
            result.details["cl16_4_valid"] = v_res.is_valid
            result.details["cl16_4_cert_hash"] = v_res.cert_hash

        return result

    def run_category(self, category: str, threat_level: ThreatLevel = ThreatLevel.HIGH) -> TestRunSummary:
        """Execute all scenarios within a specific category."""
        if category not in self.categories:
            raise ValueError(f"Unknown category: {category}. Valid categories: {list(self.categories.keys())}")

        scenarios = self.categories[category]
        results = [self.run_scenario(s.id, threat_level=threat_level) for s in scenarios]
        return self._build_summary(results, threat_level)

    def run_all(self, threat_level: ThreatLevel = ThreatLevel.HIGH) -> TestRunSummary:
        """Execute all 100 scenarios across all 10 categories."""
        all_results = []
        for s in get_all_scenarios():
            res = self.run_scenario(s.id, threat_level=threat_level)
            if res:
                all_results.append(res)
        return self._build_summary(all_results, threat_level)

    def run_full_matrix(self) -> Dict[str, TestRunSummary]:
        """Execute all 100 scenarios across all 4 threat levels (400 executions total)."""
        matrix = {}
        for tl in [ThreatLevel.LOW, ThreatLevel.MEDIUM, ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            matrix[tl.value] = self.run_all(threat_level=tl)
        return matrix

    def _build_summary(self, results: List[ScenarioResult], threat_level: ThreatLevel) -> TestRunSummary:
        total = len(results)
        detected = sum(1 for r in results if r.detected)
        escaped = total - detected
        latencies = [r.latency_ms for r in results]
        avg_lat = sum(latencies) / total if total > 0 else 0.0
        max_lat = max(latencies) if latencies else 0.0
        rate = (detected / total) if total > 0 else 1.0
        cl_count = sum(1 for r in results if "cl16_4_config" in r.details)

        return TestRunSummary(
            total=total,
            detected=detected,
            escaped=escaped,
            detection_rate=rate,
            avg_latency_ms=avg_lat,
            max_latency_ms=max_lat,
            threat_level=threat_level.value,
            results=results,
            cl16_4_validated=cl_count
        )
