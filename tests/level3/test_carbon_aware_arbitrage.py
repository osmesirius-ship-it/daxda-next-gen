r"""
Tests for Carbon-Aware Energy Arbitrage Engine.
Verifies grid telemetry MEF curves, spatial-temporal job scheduling,
and > 65% carbon emissions reduction.
"""

import numpy as np
import pytest

from daxda_engine.level3.carbon_aware_arbitrage import (
    GridRegion,
    GridTelemetryFeed,
    WorkloadJob,
    ScheduledAssignment,
    ArbitrageOptimizationResult,
    CarbonAwareArbitrageOptimizer,
)


def test_grid_telemetry_mef_curves():
    r"""Verify regional Marginal Emissions Factor profiles across 24-hour horizon."""
    feed = GridTelemetryFeed()

    mef_east = feed.get_hourly_mef_forecast("us-east", 24)
    mef_west = feed.get_hourly_mef_forecast("us-west", 24)
    mef_north = feed.get_hourly_mef_forecast("eu-north", 24)

    # US-East fossil-heavy baseline should be significantly higher than EU-North
    assert np.mean(mef_east) > 400.0
    assert np.mean(mef_north) < 60.0

    # US-West should experience significant solar midday trough (hour 12 lower than hour 0)
    assert mef_west[12] < mef_west[0] * 0.5


def test_carbon_aware_optimization_exceeds_65_percent_reduction():
    r"""Verify spatial-temporal arbitrage achieves > 65% carbon emissions reduction."""
    optimizer = CarbonAwareArbitrageOptimizer()

    # 10 batch workloads generated in fossil-heavy us-east
    jobs = [
        WorkloadJob(
            job_id=f"batch-job-{i}",
            energy_kwh=500.0,
            deadline_hours=24,
            is_latency_critical=False,
            origin_region_id="us-east",
        )
        for i in range(10)
    ]

    res: ArbitrageOptimizationResult = optimizer.optimize_workload_schedule(jobs)

    assert len(res.assignments) == 10
    assert res.total_baseline_emissions_kg > 0.0
    assert res.total_optimized_emissions_kg < res.total_baseline_emissions_kg
    # Carbon reduction must exceed 65%
    assert res.carbon_reduction_percentage > 65.0
    assert res.exceeds_65_percent_reduction_target is True


def test_latency_critical_jobs_stay_local():
    r"""Verify latency-critical jobs are not migrated to distant foreign regions."""
    optimizer = CarbonAwareArbitrageOptimizer()

    job_critical = WorkloadJob(
        job_id="urgent-latency-critical-1",
        energy_kwh=100.0,
        deadline_hours=4,
        is_latency_critical=True,
        origin_region_id="us-east",
    )

    res = optimizer.optimize_workload_schedule([job_critical])
    assignment = res.assignments[0]

    # Must stay in us-east
    assert assignment.assigned_region_id == "us-east"
    assert assignment.assigned_hour < 4


def test_cost_and_emissions_accounting():
    r"""Verify correct arithmetic for energy, emissions, and cost metrics."""
    optimizer = CarbonAwareArbitrageOptimizer()

    jobs = [
        WorkloadJob("job-1", energy_kwh=1000.0, deadline_hours=12, is_latency_critical=False),
        WorkloadJob("job-2", energy_kwh=2000.0, deadline_hours=12, is_latency_critical=False),
    ]

    res = optimizer.optimize_workload_schedule(jobs)

    assert res.total_energy_kwh == 3000.0
    assert res.total_cost_usd > 0.0
    assert res.total_optimized_emissions_kg > 0.0
    assert res.carbon_reduction_percentage > 65.0
