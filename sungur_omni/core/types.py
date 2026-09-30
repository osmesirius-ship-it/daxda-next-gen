"""
SUNGUR-OMNI: Trans-Domain Sovereign Platform - Core Types
=========================================================
Author: arch-yunus | 2026 Sovereign Systems Initiative
Governed by: DAXDA Next-Gen Cl(16,4) Engine
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import time
import hashlib
import json


class OperationalDomain(str, Enum):
    """The four operational physical mediums of SUNGUR-OMNI."""
    SEA = "SEA"
    LAND = "LAND"
    AIR = "AIR"
    SPACE = "SPACE"


class PropulsionMode(str, Enum):
    """Propulsion modes mapped to physical domains."""
    SUPERCITY_HYDROJET = "SUPERCITY_HYDROJET"    # Sea: Supercavitating Hydro-Rocket Jet (95 kts)
    PLANETARY_ELECTRIC = "PLANETARY_ELECTRIC"    # Land: Active-Torque Planetary Hub Motors (120 km/h)
    SCRAMJET_MHD = "SCRAMJET_MHD"                # Air: Dual-Mode Scramjet + Plasma Accelerator (Mach 6+)
    MPD_PLASMA = "MPD_PLASMA"                    # Space: Magnetoplasmadynamic Plasma Thruster (15 km/s dV)
    IDLE_SILENT = "IDLE_SILENT"                  # Dormant acoustic/thermal silence


class HullMorphologyState(str, Enum):
    """Morphological states of the Universal Skeleton."""
    BATHYPELAGIC_CAVITATING = "BATHYPELAGIC_CAVITATING" # Nose bubble ring active, hydrofoils swept
    TERRAIN_ROVER = "TERRAIN_ROVER"                     # Wheels deployed, high clearance
    HYPERSONIC_WAVERIDER = "HYPERSONIC_WAVERIDER"       # Sharp shock diffuser, flush bays
    EXO_ORBITAL_SHIELD = "EXO_ORBITAL_SHIELD"           # Radiative metamaterial panels exposed


class CommChannel(str, Enum):
    """Multi-medium communication channels for Swarm-Sync."""
    BLUE_GREEN_LASER = "BLUE_GREEN_LASER"  # Sualtı - 532 nm optical penetrate water column
    MILLIMETRIC_RF = "MILLIMETRIC_RF"      # Atmosfer / Kara - Directional phased-array RF
    SPACE_OPTICAL_LINK = "SPACE_OPTICAL"   # Yörünge - High-bandwidth laser intersatellite link
    ACOUSTIC_ANALOG = "ACOUSTIC_ANALOG"    # Ultra-deep submarine fallback


@dataclass
class TelemetryVector:
    """Comprehensive real-time telemetry snapshot of SUNGUR-OMNI."""
    domain: OperationalDomain
    altitude_m: float           # Positive for altitude, negative for depth (m)
    velocity_mps: float         # Velocity in meters per second
    mach_number: float          # Current Mach number relative to medium
    hydrostatic_pressure_bar: float # Ambient hydrostatic pressure (bar)
    hull_temperature_c: float   # Stagnation hull temperature (°C)
    qins_drift_error_m: float   # Quantum inertial navigation integrated drift (m)
    propellant_kg: float        # Remaining reaction mass (kg)
    core_power_mw: float        # Power draw from energy core (MW)
    structural_integrity_pct: float # Self-healing composite status (0 - 100%)
    timestamp: float = field(default_factory=time.time)

    @property
    def velocity_knots(self) -> float:
        return self.velocity_mps * 1.94384

    @property
    def velocity_kmh(self) -> float:
        return self.velocity_mps * 3.6


@dataclass
class SwarmMessage:
    """Swarm-Sync telemetry and tactical synchronization packet."""
    sender_id: str
    target_id: str
    channel: CommChannel
    domain_origin: OperationalDomain
    payload: Dict[str, Any]
    daxda_seal: str = ""
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self):
        if not self.daxda_seal:
            data = f"{self.sender_id}:{self.target_id}:{self.domain_origin}:{json.dumps(self.payload, sort_keys=True)}"
            self.daxda_seal = hashlib.sha256(data.encode()).hexdigest()[:16]
