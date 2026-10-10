r"""
DAXDA Level 3: Carbon-Aware Energy Arbitrage Engine.
Implements electricity grid Marginal Emissions Factor (MEF) telemetry ingestion,
spatial-temporal job scheduling, and > 65% carbon intensity reduction verification.
"""

from .grid_telemetry import (
    GridRegion,
    GridTelemetryFeed,
)
from .arbitrage_solver import (
    WorkloadJob,
    ScheduledAssignment,
    ArbitrageOptimizationResult,
    CarbonAwareArbitrageOptimizer,
)

__all__ = [
    "GridRegion",
    "GridTelemetryFeed",
    "WorkloadJob",
    "ScheduledAssignment",
    "ArbitrageOptimizationResult",
    "CarbonAwareArbitrageOptimizer",
]
