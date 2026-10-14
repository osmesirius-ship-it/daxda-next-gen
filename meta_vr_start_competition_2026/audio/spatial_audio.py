"""
DAXDA ChronoHands: Procedural 3D Spatial Audio & Haptic Feedback Engine
========================================================================
Defines synthesis parameters and event mappings for WebXR spatial audio.
Produces zero-external-asset procedural audio:
- Metallic gear ratchet clicks
- Resonance crystal chimes
- Sub-bass magnetic hums
- Temporal Doppler sweeps
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

class AudioEventType(str, Enum):
    SNAP_CLICK = "SNAP_CLICK"
    GEAR_RATCHET = "GEAR_RATCHET"
    RESONANCE_CHIME = "RESONANCE_CHIME"
    PALM_MAGNET_HUM = "PALM_MAGNET_HUM"
    TIME_WARP_SWEEP = "TIME_WARP_SWEEP"
    PINCH_GRAB = "PINCH_GRAB"

@dataclass
class SynthPatch:
    event_type: AudioEventType
    oscillator_type: str        # 'sine', 'square', 'triangle', 'sawtooth'
    base_frequency_hz: float
    frequency_envelope: List[Tuple[float, float]]  # (time_offset_sec, freq_multiplier)
    gain_envelope: List[Tuple[float, float]]       # (time_offset_sec, gain_level)
    filter_cutoff_hz: float = 2400.0
    resonance_q: float = 4.0
    duration_sec: float = 0.25

class SpatialAudioEngine:
    """
    Manages procedural 3D audio synthesizers for hands-first feedback.
    """
    def __init__(self):
        self.patches: Dict[AudioEventType, SynthPatch] = self._init_patches()

    def _init_patches(self) -> Dict[AudioEventType, SynthPatch]:
        return {
            AudioEventType.SNAP_CLICK: SynthPatch(
                event_type=AudioEventType.SNAP_CLICK,
                oscillator_type="triangle",
                base_frequency_hz=880.0,
                frequency_envelope=[(0.0, 1.0), (0.015, 2.4), (0.08, 0.6)],
                gain_envelope=[(0.0, 0.9), (0.02, 1.0), (0.08, 0.0)],
                filter_cutoff_hz=4200.0,
                resonance_q=8.0,
                duration_sec=0.09
            ),
            AudioEventType.GEAR_RATCHET: SynthPatch(
                event_type=AudioEventType.GEAR_RATCHET,
                oscillator_type="sawtooth",
                base_frequency_hz=220.0,
                frequency_envelope=[(0.0, 1.0), (0.02, 1.2), (0.04, 0.8)],
                gain_envelope=[(0.0, 0.6), (0.02, 0.8), (0.05, 0.0)],
                filter_cutoff_hz=1600.0,
                duration_sec=0.05
            ),
            AudioEventType.RESONANCE_CHIME: SynthPatch(
                event_type=AudioEventType.RESONANCE_CHIME,
                oscillator_type="sine",
                base_frequency_hz=528.0,  # Solfeggio 528Hz Harmonic DNA frequency
                frequency_envelope=[(0.0, 1.0), (0.2, 1.5), (0.6, 2.0)],
                gain_envelope=[(0.0, 0.8), (0.1, 1.0), (1.2, 0.0)],
                filter_cutoff_hz=3200.0,
                resonance_q=12.0,
                duration_sec=1.4
            ),
            AudioEventType.PALM_MAGNET_HUM: SynthPatch(
                event_type=AudioEventType.PALM_MAGNET_HUM,
                oscillator_type="sine",
                base_frequency_hz=55.0,  # A1 sub-bass
                frequency_envelope=[(0.0, 1.0), (0.3, 1.05), (0.8, 1.0)],
                gain_envelope=[(0.0, 0.4), (0.2, 0.6), (0.8, 0.0)],
                filter_cutoff_hz=280.0,
                duration_sec=0.8
            ),
            AudioEventType.TIME_WARP_SWEEP: SynthPatch(
                event_type=AudioEventType.TIME_WARP_SWEEP,
                oscillator_type="sawtooth",
                base_frequency_hz=180.0,
                frequency_envelope=[(0.0, 1.0), (0.2, 3.5), (0.5, 0.5)],
                gain_envelope=[(0.0, 0.7), (0.25, 0.9), (0.6, 0.0)],
                filter_cutoff_hz=2200.0,
                resonance_q=6.5,
                duration_sec=0.65
            ),
            AudioEventType.PINCH_GRAB: SynthPatch(
                event_type=AudioEventType.PINCH_GRAB,
                oscillator_type="sine",
                base_frequency_hz=440.0,
                frequency_envelope=[(0.0, 1.0), (0.02, 1.3), (0.05, 0.9)],
                gain_envelope=[(0.0, 0.7), (0.02, 0.9), (0.06, 0.0)],
                filter_cutoff_hz=2800.0,
                duration_sec=0.07
            )
        }

    def compute_3d_spatial_panning(
        self,
        source_pos: Tuple[float, float, float],
        listener_pos: Tuple[float, float, float] = (0.0, 1.6, 0.0)
    ) -> Dict[str, float]:
        """
        Computes distance attenuation and azimuth angle for WebXR AudioListener / PannerNode.
        """
        sx, sy, sz = source_pos
        lx, ly, lz = listener_pos
        dx = sx - lx
        dy = sy - ly
        dz = sz - lz
        dist = math.sqrt(dx**2 + dy**2 + dz**2)

        # Attenuation (Inverse square with reference distance 0.3m)
        gain = 1.0 / max(1.0, (dist / 0.3)**2)
        azimuth = math.atan2(dx, -dz)  # radians relative to listener head

        return {
            "distance_meters": dist,
            "gain_multiplier": round(gain, 4),
            "azimuth_radians": round(azimuth, 4),
            "panning_x": round(math.sin(azimuth), 3),
            "panning_z": round(-math.cos(azimuth), 3)
        }
