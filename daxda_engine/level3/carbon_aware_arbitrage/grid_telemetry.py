r"""
Electricity Grid Marginal Emissions Factor (MEF) Telemetry Engine.
Models regional power grids, real-time carbon intensity (gCO2eq/kWh),
and dynamic renewable generation availability.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import math
import numpy as np


@dataclass(frozen=True)
class GridRegion:
    """Regional power grid node."""
    region_id: str
    grid_name: str
    base_mef_gco2_per_kwh: float  # Baseline marginal emissions factor
    renewable_share_fraction: float
    electricity_price_usd_per_mwh: float
    network_latency_ms: float


class GridTelemetryFeed:
    r"""
    Simulates real-time Marginal Emissions Factor (MEF) telemetry across global regions:
      - US-East (PJM): Fossil-heavy baseline (~ 480 gCO2/kWh)
      - US-West (CAISO): High solar during midday (~ 80 - 150 gCO2/kWh)
      - EU-North (NordPool): Low-carbon hydro/wind (~ 35 - 70 gCO2/kWh)
      - EU-Central (Germany/France): Nuclear/wind mix (~ 120 - 250 gCO2/kWh)
    """

    DEFAULT_REGIONS = [
        GridRegion("us-east", "PJM Interconnection", 480.0, 0.15, 65.0, 15.0),
        GridRegion("us-west", "CAISO California", 280.0, 0.45, 80.0, 35.0),
        GridRegion("eu-north", "NordPool Scandinavia", 45.0, 0.92, 40.0, 95.0),
        GridRegion("eu-central", "ENTSO-E France/Germany", 140.0, 0.65, 55.0, 85.0),
    ]

    def __init__(self, regions: Optional[List[GridRegion]] = None):
        self.regions = {r.region_id: r for r in (regions or self.DEFAULT_REGIONS)}

    def get_hourly_mef_forecast(
        self,
        region_id: str,
        forecast_horizon_hours: int = 24,
    ) -> np.ndarray:
        r"""
        Generates 24-hour diurnal carbon intensity profile:
        MEF(t) = \text{base} \cdot [1 - 0.6 \cdot \text{solar}(t) - 0.2 \cdot \text{wind}(t)].
        """
        if region_id not in self.regions:
            raise KeyError(f"Unknown region {region_id}")

        reg = self.regions[region_id]
        hours = np.arange(forecast_horizon_hours)

        # Diurnal solar pattern (peaks at hour 12-14)
        solar_curve = np.clip(np.sin((hours - 6) * np.pi / 12.0), 0.0, 1.0)

        if region_id == "us-west":
            # Strong solar midday drop (CAISO duck curve)
            mef = reg.base_mef_gco2_per_kwh * (1.0 - 0.70 * solar_curve)
        elif region_id == "eu-north":
            # Consistently ultra-low hydro/wind baseline
            mef = np.full(forecast_horizon_hours, reg.base_mef_gco2_per_kwh) + np.random.default_rng(42).normal(0, 3, forecast_horizon_hours)
        elif region_id == "us-east":
            # Modest solar, peak demand evenings
            mef = reg.base_mef_gco2_per_kwh * (0.9 + 0.25 * (hours >= 17) * (hours <= 21))
        else:
            mef = reg.base_mef_gco2_per_kwh * (1.0 - 0.35 * solar_curve)

        return np.maximum(20.0, mef)
