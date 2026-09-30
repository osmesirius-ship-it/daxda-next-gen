"""
SUNGUR-OMNI: Tri-Propulsion Hybrid Drive Subsystem
==================================================
Author: arch-yunus | 2026 Sovereign Systems Initiative
Governed by: DAXDA Next-Gen Cl(16,4) Invariants
"""

import math
from typing import Dict, Any, Tuple
from ..core.types import OperationalDomain, PropulsionMode, TelemetryVector


class TriPropulsionSubsystem:
    """
    Unified Tri-Propulsion Engine executing four domain drive regimes:
    1. Supercavitating Hydro-Rocket Jet (Sea: 95 kts)
    2. Active-Torque Planetary Hubs (Land: 120 km/h)
    3. Dual-Mode Scramjet + Plasma MHD (Air: Mach 6.2+)
    4. Magnetoplasmadynamic (MPD) Plasma Thruster (Space: 15 km/s Delta-V)
    """

    def __init__(self, total_propellant_kg: float = 2400.0, core_capacity_mw: float = 50.0):
        self.total_propellant_kg = total_propellant_kg
        self.remaining_propellant_kg = total_propellant_kg
        self.core_capacity_mw = core_capacity_mw
        self.active_mode = PropulsionMode.IDLE_SILENT
        self.current_thrust_kn = 0.0
        self.specific_impulse_s = 0.0

    def compute_cavitation_number(self, depth_m: float, velocity_mps: float) -> float:
        """
        Calculates cavitation index sigma:
        sigma = (P_ambient - P_vapor) / (0.5 * rho * v^2)
        Supercavitation initiates when sigma < 0.1.
        """
        if velocity_mps <= 1.0:
            return 10.0
        rho_water = 1025.0  # kg/m^3 (sea water)
        p_ambient = 101325.0 + (rho_water * 9.80665 * abs(depth_m))
        p_vapor = 2338.0  # Pa at 20°C
        q_dynamic = 0.5 * rho_water * (velocity_mps ** 2)
        return (p_ambient - p_vapor) / q_dynamic

    def calculate_speed_of_sound_air(self, altitude_m: float) -> float:
        """Standard ISA speed of sound calculation up to 50 km."""
        if altitude_m < 11000.0:
            temp_k = 288.15 - (0.0065 * altitude_m)
        elif altitude_m < 25000.0:
            temp_k = 216.65
        else:
            temp_k = 216.65 + (0.0028 * (altitude_m - 25000.0))
        return math.sqrt(1.4 * 287.05 * max(150.0, temp_k))

    def evaluate_propulsion_command(
        self,
        target_mode: PropulsionMode,
        throttle_pct: float,
        telemetry: TelemetryVector
    ) -> Dict[str, Any]:
        """
        Calculates thrust, power draw, and fuel burn based on domain physics.
        Returns command parameters and domain compatibility flags.
        """
        throttle = max(0.0, min(1.0, throttle_pct / 100.0))

        # Check domain compatibility
        is_compatible = True
        violation_reason = "NONE"

        if target_mode == PropulsionMode.SUPERCITY_HYDROJET:
            if telemetry.domain != OperationalDomain.SEA or telemetry.altitude_m > 0:
                is_compatible = False
                violation_reason = "HYDROJET_DRY_ATMOSPHERIC_FIRE_HAZARD"
            else:
                self.active_mode = target_mode
                self.specific_impulse_s = 480.0
                # Hydro-rocket boosted cavitation jet: up to 180 kN thrust
                self.current_thrust_kn = 180.0 * throttle
                power_mw = 18.0 * throttle
                sigma = self.compute_cavitation_number(telemetry.altitude_m, telemetry.velocity_mps)
                return {
                    "compatible": True,
                    "mode": self.active_mode.value,
                    "thrust_kn": self.current_thrust_kn,
                    "power_mw": power_mw,
                    "cavitation_index": sigma,
                    "supercavitation_stable": sigma < 0.15,
                    "max_speed_kts": 95.0,
                    "violation": violation_reason
                }

        elif target_mode == PropulsionMode.PLANETARY_ELECTRIC:
            if telemetry.domain != OperationalDomain.LAND:
                is_compatible = False
                violation_reason = "GROUND_DRIVE_DISENGAGED_IN_NON_TERRESTRIAL_MEDIUM"
            else:
                self.active_mode = target_mode
                self.specific_impulse_s = float("inf")  # Pure electric direct drive
                # Active in-wheel high-torque motors: 45 kN ground tractive effort
                self.current_thrust_kn = 45.0 * throttle
                power_mw = 4.5 * throttle
                return {
                    "compatible": True,
                    "mode": self.active_mode.value,
                    "thrust_kn": self.current_thrust_kn,
                    "power_mw": power_mw,
                    "max_speed_kmh": 120.0,
                    "tractive_torque_nm": 6400.0 * throttle,
                    "violation": violation_reason
                }

        elif target_mode == PropulsionMode.SCRAMJET_MHD:
            if telemetry.domain != OperationalDomain.AIR or telemetry.altitude_m < 0 or telemetry.altitude_m > 55000:
                is_compatible = False
                violation_reason = "SCRAMJET_REQUIRES_COMPRESSIBLE_ATMOSPHERIC_COLUMN"
            elif telemetry.velocity_mps < 450.0:  # Below Mach 1.5 ram compression
                is_compatible = False
                violation_reason = "RAM_COMPRESSION_INSUFFICIENT_REQUIRES_ROCKET_BOOST"
            else:
                self.active_mode = target_mode
                self.specific_impulse_s = 2200.0  # High air-breathing Isp
                # Scramjet + MHD accelerator produces up to 320 kN thrust
                self.current_thrust_kn = 320.0 * throttle
                power_mw = 35.0 * throttle
                speed_of_sound = self.calculate_speed_of_sound_air(telemetry.altitude_m)
                mach = telemetry.velocity_mps / max(1.0, speed_of_sound)
                return {
                    "compatible": True,
                    "mode": self.active_mode.value,
                    "thrust_kn": self.current_thrust_kn,
                    "power_mw": power_mw,
                    "mach_number": mach,
                    "mhd_plasma_active": mach >= 4.5,
                    "max_mach": 6.2,
                    "violation": violation_reason
                }

        elif target_mode == PropulsionMode.MPD_PLASMA:
            if telemetry.domain != OperationalDomain.SPACE and telemetry.altitude_m < 80000:
                is_compatible = False
                violation_reason = "MPD_ARC_QUENCHING_IN_DENSE_ATMOSPHERE"
            else:
                self.active_mode = target_mode
                self.specific_impulse_s = 6200.0  # Ultra-high Isp vacuum plasma
                # MPD continuous high-efficiency plasma thrust (continuous 12 kN in vacuum)
                self.current_thrust_kn = 12.0 * throttle
                power_mw = 42.0 * throttle
                # Tsiolkovsky delta-V capacity: v_e * ln(m0 / mf)
                v_exhaust = self.specific_impulse_s * 9.80665
                delta_v_total_kms = (v_exhaust * math.log(5200.0 / 2800.0)) / 1000.0
                return {
                    "compatible": True,
                    "mode": self.active_mode.value,
                    "thrust_kn": self.current_thrust_kn,
                    "power_mw": power_mw,
                    "isp_seconds": self.specific_impulse_s,
                    "total_delta_v_kms": delta_v_total_kms,
                    "violation": violation_reason
                }

        elif target_mode == PropulsionMode.IDLE_SILENT:
            self.active_mode = target_mode
            self.current_thrust_kn = 0.0
            return {
                "compatible": True,
                "mode": self.active_mode.value,
                "thrust_kn": 0.0,
                "power_mw": 0.5,
                "violation": "NONE"
            }

        return {
            "compatible": False,
            "mode": target_mode.value,
            "thrust_kn": 0.0,
            "power_mw": 0.0,
            "violation": violation_reason
        }
