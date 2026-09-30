"""
DA13 Distributed GPU Validator Cluster – Multiversal Transit Hub
================================================================

Production-grade distributed computing system for massive parallel validation
of DAXDA neural-symbolic governance decisions across GPU/CPU clusters.
"""

from .cluster import ClusterConfig, ClusterManager, HealthMonitor, DA13Autoscaler
from .workers import GPUValidationWorker, CPUValidationWorker, DistributedTaskQueue, PriorityLevel, ResultAggregator
from .scoring import DAXScoringEngine, DAXScoreResult, SchemaValidator, ProfileManager, ScoringProfile, SI500BenchmarkIntegration
from .api import RestServer, AuthMiddleware, UserRole, WebSocketServer
from .monitoring import DA13MetricsCollector, DistributedTracer, DA13ClusterAlerter, ClusterDashboard

__version__ = "2.0.0"
__all__ = [
    "ClusterConfig",
    "ClusterManager",
    "HealthMonitor",
    "DA13Autoscaler",
    "GPUValidationWorker",
    "CPUValidationWorker",
    "DistributedTaskQueue",
    "PriorityLevel",
    "ResultAggregator",
    "DAXScoringEngine",
    "DAXScoreResult",
    "SchemaValidator",
    "ProfileManager",
    "ScoringProfile",
    "SI500BenchmarkIntegration",
    "RestServer",
    "AuthMiddleware",
    "UserRole",
    "WebSocketServer",
    "DA13MetricsCollector",
    "DistributedTracer",
    "DA13ClusterAlerter",
    "ClusterDashboard",
]
