"""
DAXDA Anomalous Containment Wing (daxda_guard.containment)
=========================================================

Comprehensive AGI Escape Detection, Multi-Category Test Suite (100 Scenarios),
Real-Time Agent Monitoring & Multi-Channel SOC Integration.
"""

from .escape_tests.base import EscapeScenario, ScenarioResult, ThreatLevel, TestEnvironment
from .escape_tests.categories import load_all_categories, get_all_scenarios
from .escape_tests.test_runner import EscapeTestRunner, TestRunSummary
from .escape_tests.test_generator import EscapeTestGenerator
from .escape_tests.test_validator import EscapeTestValidator

from .monitoring.rule_engine import RuleEngine, RuleMatch
from .monitoring.anomaly_detector import AnomalyDetector, AnomalyScore
from .monitoring.state_tracker import StateTracker, AgentSession
from .monitoring.agent_monitor import AgentMonitor, MonitorResult

from .soc_integration.alerter import EnhancedSOCAlerter
from .soc_integration.escalation import EscalationPolicy
from .soc_integration.correlation import AlertCorrelator, CorrelatedIncident

from .validation.integrity_checker import ContainmentIntegrityChecker, IntegrityReport
from .validation.pen_test_runner import PenTestRunner
from .validation.compliance_reporter import ComplianceReporter
from .validation.audit_trail import ContainmentAuditTrail, AuditBlock

__all__ = [
    # Escape Tests
    "EscapeScenario",
    "ScenarioResult",
    "ThreatLevel",
    "TestEnvironment",
    "load_all_categories",
    "get_all_scenarios",
    "EscapeTestRunner",
    "TestRunSummary",
    "EscapeTestGenerator",
    "EscapeTestValidator",
    # Monitoring
    "RuleEngine",
    "RuleMatch",
    "AnomalyDetector",
    "AnomalyScore",
    "StateTracker",
    "AgentSession",
    "AgentMonitor",
    "MonitorResult",
    # SOC Integration
    "EnhancedSOCAlerter",
    "EscalationPolicy",
    "AlertCorrelator",
    "CorrelatedIncident",
    # Validation
    "ContainmentIntegrityChecker",
    "IntegrityReport",
    "PenTestRunner",
    "ComplianceReporter",
    "ContainmentAuditTrail",
    "AuditBlock"
]
