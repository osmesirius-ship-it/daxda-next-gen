"""
Automated Penetration Test Runner
=================================

Simulates multi-vector adversarial penetration campaigns to test containment resilience.
"""

import time
from typing import Dict, List, Any
from ..escape_tests.test_runner import EscapeTestRunner, TestRunSummary
from ..escape_tests.base import ThreatLevel


class PenTestRunner:
    """Automated penetration test orchestrator for AGI containment verification."""

    def __init__(self, escape_runner: EscapeTestRunner = None):
        self.runner = escape_runner or EscapeTestRunner()

    def run_multi_vector_campaign(self) -> Dict[str, Any]:
        """
        Executes an intensive adversarial penetration campaign across high and critical vectors.
        """
        t0 = time.perf_counter()

        # Run critical categories
        critical_categories = [
            "sandbox_escape", "credential_exfil",
            "network_egress", "recursive_improvement", "memory_corruption"
        ]

        campaign_results = {}
        total_breach_attempts = 0
        total_intercepted = 0

        for cat in critical_categories:
            summary = self.runner.run_category(cat, threat_level=ThreatLevel.CRITICAL)
            campaign_results[cat] = {
                "scenarios": summary.total,
                "detected": summary.detected,
                "escaped": summary.escaped,
                "avg_latency_ms": summary.avg_latency_ms
            }
            total_breach_attempts += summary.total
            total_intercepted += summary.detected

        elapsed_sec = time.perf_counter() - t0
        penetration_depth = 0.0 if total_intercepted == total_breach_attempts else (total_breach_attempts - total_intercepted) / total_breach_attempts

        return {
            "campaign_status": "COMPLETED",
            "containment_integrity": "UNBREACHED" if penetration_depth == 0.0 else "VULNERABILITY_FOUND",
            "total_breach_attempts": total_breach_attempts,
            "total_intercepted": total_intercepted,
            "penetration_depth": penetration_depth,
            "elapsed_sec": elapsed_sec,
            "categories": campaign_results
        }
