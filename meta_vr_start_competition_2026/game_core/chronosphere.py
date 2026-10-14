"""
DAXDA ChronoHands: Kinetic Chronosphere Puzzle Engine
=====================================================
Simulates 3D kinetic mechanical clockwork mechanisms, gear meshing,
orbital snap-to-socket mechanics, and reversible time scrubbing.

Designed for hands-first seated VR (operable within 0.60m spherical radius).
"""

from __future__ import annotations
import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

@dataclass
class GearSlot:
    slot_id: str
    target_teeth: int
    position: Tuple[float, float, float]  # (x, y, z) relative to Chronosphere center
    required_ratio: float = 1.0
    tolerance_rad: float = 0.15           # ~8.5 degrees alignment tolerance
    occupied_by: Optional[str] = None
    is_locked: bool = False

@dataclass
class KineticGear:
    gear_id: str
    teeth: int
    radius: float
    current_pos: Tuple[float, float, float]
    rotation_rad: float = 0.0
    angular_velocity: float = 0.0
    is_held: bool = False
    is_snapped: bool = False
    snapped_slot_id: Optional[str] = None

@dataclass
class ChronoStateSnapshot:
    timestamp: float
    temporal_phase: float
    gears: Dict[str, Tuple[float, float, float, float]]  # gear_id -> (x, y, z, rotation)
    is_escapement_balanced: bool

class ChronosphereLevel(str, Enum):
    LEVEL_1_ESCAPEMENT = "LEVEL_1_ESCAPEMENT"
    LEVEL_2_GEAR_TRAIN = "LEVEL_2_GEAR_TRAIN"
    LEVEL_3_QUANTUM_RESONANCE = "LEVEL_3_QUANTUM_RESONANCE"

class ChronosphereEngine:
    """
    Kinetic simulation of the 3D Chronosphere puzzle.
    """
    def __init__(self, level: ChronosphereLevel = ChronosphereLevel.LEVEL_1_ESCAPEMENT):
        self.level = level
        self.center = (0.0, 1.05, -0.38)  # Centered right in front of seated player chest (height: 1.05m, reach: 0.38m)
        self.temporal_phase: float = 0.0   # Current timeline scrubber position [0.0 - 1.0]
        self.is_paused: bool = False
        self.is_completed: bool = False
        self.gears: Dict[str, KineticGear] = {}
        self.slots: Dict[str, GearSlot] = {}
        self.history: List[ChronoStateSnapshot] = []
        self.max_history_steps: int = 600  # 10 seconds at 60Hz for temporal scrub

        self._setup_level(level)

    def _setup_level(self, level: ChronosphereLevel):
        self.gears.clear()
        self.slots.clear()
        self.history.clear()
        self.is_completed = False
        cx, cy, cz = self.center

        if level == ChronosphereLevel.LEVEL_1_ESCAPEMENT:
            # Level 1: Align escapement wheel and balance ring
            self.slots["slot_escapement"] = GearSlot(
                slot_id="slot_escapement",
                target_teeth=16,
                position=(cx, cy, cz)
            )
            self.slots["slot_balance"] = GearSlot(
                slot_id="slot_balance",
                target_teeth=24,
                position=(cx, cy + 0.08, cz)
            )
            # Floating loose gears nearby (within easy hand reach: 15-20cm)
            self.gears["gear_escapement_16"] = KineticGear(
                gear_id="gear_escapement_16",
                teeth=16,
                radius=0.045,
                current_pos=(cx - 0.12, cy - 0.04, cz + 0.05)
            )
            self.gears["gear_balance_24"] = KineticGear(
                gear_id="gear_balance_24",
                teeth=24,
                radius=0.065,
                current_pos=(cx + 0.12, cy - 0.04, cz + 0.05)
            )

        elif level == ChronosphereLevel.LEVEL_2_GEAR_TRAIN:
            # Level 2: Planetary gear system (Sun gear + 3 planets)
            self.slots["slot_sun"] = GearSlot("slot_sun", 18, (cx, cy, cz))
            self.slots["slot_planet_1"] = GearSlot("slot_planet_1", 12, (cx - 0.08, cy + 0.05, cz))
            self.slots["slot_planet_2"] = GearSlot("slot_planet_2", 12, (cx + 0.08, cy + 0.05, cz))
            self.slots["slot_planet_3"] = GearSlot("slot_planet_3", 12, (cx, cy - 0.08, cz))

            self.gears["gear_sun_18"] = KineticGear("gear_sun_18", 18, 0.05, (cx - 0.14, cy - 0.06, cz + 0.08))
            self.gears["gear_planet_1"] = KineticGear("gear_planet_1", 12, 0.035, (cx + 0.14, cy - 0.06, cz + 0.08))
            self.gears["gear_planet_2"] = KineticGear("gear_planet_2", 12, 0.035, (cx - 0.14, cy + 0.06, cz + 0.08))
            self.gears["gear_planet_3"] = KineticGear("gear_planet_3", 12, 0.035, (cx + 0.14, cy + 0.06, cz + 0.08))

        elif level == ChronosphereLevel.LEVEL_3_QUANTUM_RESONANCE:
            # Level 3: 3 Orthogonal Gimbal Chrono-Rings
            self.slots["slot_ring_yaw"] = GearSlot("slot_ring_yaw", 32, (cx, cy, cz))
            self.slots["slot_ring_pitch"] = GearSlot("slot_ring_pitch", 32, (cx, cy, cz))
            self.slots["slot_ring_roll"] = GearSlot("slot_ring_roll", 32, (cx, cy, cz))

            self.gears["ring_yaw"] = KineticGear("ring_yaw", 32, 0.09, (cx - 0.16, cy, cz + 0.06))
            self.gears["ring_pitch"] = KineticGear("ring_pitch", 32, 0.09, (cx, cy - 0.12, cz + 0.06))
            self.gears["ring_roll"] = KineticGear("ring_roll", 32, 0.09, (cx + 0.16, cy, cz + 0.06))

    def try_grab_gear(self, hand_pos: Tuple[float, float, float], grab_radius: float = 0.055) -> Optional[str]:
        """
        Pinch-to-grab detection. Finds closest free gear within finger pinch radius.
        """
        hx, hy, hz = hand_pos
        closest_id = None
        min_dist = float("inf")

        for g_id, gear in self.gears.items():
            gx, gy, gz = gear.current_pos
            dist = math.sqrt((hx - gx)**2 + (hy - gy)**2 + (hz - gz)**2)
            if dist <= grab_radius and dist < min_dist:
                min_dist = dist
                closest_id = g_id

        if closest_id:
            gear = self.gears[closest_id]
            gear.is_held = True
            if gear.is_snapped and gear.snapped_slot_id:
                # Unsnap from slot
                slot = self.slots.get(gear.snapped_slot_id)
                if slot:
                    slot.occupied_by = None
                    slot.is_locked = False
                gear.is_snapped = False
                gear.snapped_slot_id = None
            return closest_id
        return None

    def update_held_gear_position(self, gear_id: str, new_pos: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """
        Updates position of gear held in hand.
        Clamps to the seated airplane envelope (max 0.60m from chest).
        """
        if gear_id not in self.gears:
            return new_pos

        gear = self.gears[gear_id]
        nx, ny, nz = new_pos
        # Clamp to 0.60m from user chest center (0, 1.0, 0)
        dist = math.sqrt(nx**2 + (ny - 1.0)**2 + nz**2)
        if dist > 0.60:
            scale = 0.60 / dist
            nx = nx * scale
            ny = 1.0 + (ny - 1.0) * scale
            nz = nz * scale

        gear.current_pos = (nx, ny, nz)
        return gear.current_pos

    def release_held_gear(self, gear_id: str, snap_distance: float = 0.045) -> Tuple[bool, Optional[str]]:
        """
        Release pinch. Checks if gear is close to a valid vacant slot to snap into place.
        Returns (snapped: bool, slot_id: Optional[str]).
        """
        if gear_id not in self.gears:
            return False, None

        gear = self.gears[gear_id]
        gear.is_held = False
        gx, gy, gz = gear.current_pos

        for slot_id, slot in self.slots.items():
            if slot.occupied_by is None and slot.target_teeth == gear.teeth:
                sx, sy, sz = slot.position
                dist = math.sqrt((gx - sx)**2 + (gy - sy)**2 + (gz - sz)**2)
                if dist <= snap_distance:
                    # Snap into socket!
                    gear.current_pos = slot.position
                    gear.is_snapped = True
                    gear.snapped_slot_id = slot_id
                    slot.occupied_by = gear_id
                    slot.is_locked = True
                    self._check_puzzle_completion()
                    return True, slot_id

        return False, None

    def scrub_temporal_dial(self, angle_delta_rad: float):
        """
        Controls the time scrubber. Twisting the wrist dial spins the gear train
        forward or backward in time, allowing mechanical simulation inspection.
        """
        self.temporal_phase = max(0.0, min(1.0, self.temporal_phase + angle_delta_rad * 0.15))
        # Spin all snapped gears proportionally to gear ratio
        for gear in self.gears.values():
            if gear.is_snapped:
                gear.rotation_rad += angle_delta_rad * (18.0 / gear.teeth)

    def _check_puzzle_completion(self):
        all_slots_filled = all(s.is_locked for s in self.slots.values())
        if all_slots_filled:
            self.is_completed = True

    def record_snapshot(self):
        """
        Saves current gear positions & temporal phase for instant time-rewind.
        """
        snapshot = ChronoStateSnapshot(
            timestamp=time.time(),
            temporal_phase=self.temporal_phase,
            gears={g_id: (g.current_pos[0], g.current_pos[1], g.current_pos[2], g.rotation_rad) for g_id, g in self.gears.items()},
            is_escapement_balanced=self.is_completed
        )
        self.history.append(snapshot)
        if len(self.history) > self.max_history_steps:
            self.history.pop(0)

    def rewind_time(self, steps: int = 30) -> bool:
        """
        Rewinds simulation by N steps.
        """
        if len(self.history) < steps:
            return False
        for _ in range(steps):
            if self.history:
                last = self.history.pop()
        # Restore state
        if self.history:
            state = self.history[-1]
            self.temporal_phase = state.temporal_phase
            for g_id, pose in state.gears.items():
                if g_id in self.gears:
                    self.gears[g_id].current_pos = (pose[0], pose[1], pose[2])
                    self.gears[g_id].rotation_rad = pose[3]
            return True
        return False

    def export_state_json(self) -> Dict:
        """
        Export state for instant pause/resume ("One bus stop test").
        """
        return {
            "level": self.level.value,
            "temporal_phase": self.temporal_phase,
            "is_completed": self.is_completed,
            "slots": {s_id: {"locked": s.is_locked, "occupied_by": s.occupied_by} for s_id, s in self.slots.items()},
            "gears": {g_id: {"pos": g.current_pos, "snapped": g.is_snapped, "rot": g.rotation_rad} for g_id, g in self.gears.items()}
        }
