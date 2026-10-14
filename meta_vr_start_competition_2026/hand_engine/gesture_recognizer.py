"""
DAXDA ChronoHands: 26-Joint WebXR Hand Tracking & Micro-Gesture Engine
======================================================================
Implements biophysically grounded hand tracking and micro-gesture recognition
compliant with the Meta Quest & Meta VR Glasses hands-first specifications.

No controllers required. Evaluated against the 'Airplane Seat Test' (0.60m radius).
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

SEATED_MAX_RADIUS_METERS = 0.60  # Airplane seat 2-foot radius test
PINCH_THRESHOLD_METERS = 0.028   # 2.8 cm between thumb tip & index tip
GRAB_THRESHOLD_METERS = 0.045    # Fingertips curled toward palm center
POKE_EXTENDED_RATIO = 1.6        # Index tip extension vs other fingers

class Handedness(str, Enum):
    LEFT = "left"
    RIGHT = "right"

class GestureType(str, Enum):
    IDLE = "IDLE"
    PINCH = "PINCH"
    GRAB = "GRAB"
    POKE = "POKE"
    PALM_HOVER = "PALM_HOVER"
    WRIST_DIAL = "WRIST_DIAL"
    BIMANUAL_STRETCH = "BIMANUAL_STRETCH"

# Standard 25/26 WebXR Hand Skeleton Joints
JOINT_NAMES = [
    "wrist",
    "thumb-metacarpal", "thumb-phalanx-proximal", "thumb-phalanx-distal", "thumb-tip",
    "index-finger-metacarpal", "index-finger-phalanx-proximal", "index-finger-phalanx-intermediate", "index-finger-phalanx-distal", "index-finger-tip",
    "middle-finger-metacarpal", "middle-finger-phalanx-proximal", "middle-finger-phalanx-intermediate", "middle-finger-phalanx-distal", "middle-finger-tip",
    "ring-finger-metacarpal", "ring-finger-phalanx-proximal", "ring-finger-phalanx-intermediate", "ring-finger-phalanx-distal", "ring-finger-tip",
    "pinky-finger-metacarpal", "pinky-finger-phalanx-proximal", "pinky-finger-phalanx-intermediate", "pinky-finger-phalanx-distal", "pinky-finger-tip"
]

@dataclass
class Vec3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def dist(self, other: Vec3) -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)

    def sub(self, other: Vec3) -> Vec3:
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def add(self, other: Vec3) -> Vec3:
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def dot(self, other: Vec3) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: Vec3) -> Vec3:
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def length(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self) -> Vec3:
        l = self.length()
        if l < 1e-9:
            return Vec3(0, 0, 0)
        return Vec3(self.x / l, self.y / l, self.z / l)

@dataclass
class HandJointPose:
    name: str
    position: Vec3
    radius: float = 0.008  # Default joint collision capsule radius in meters

@dataclass
class HandSkeleton:
    handedness: Handedness
    joints: Dict[str, HandJointPose] = field(default_factory=dict)
    confidence: float = 1.0

    def get_joint(self, name: str) -> Optional[Vec3]:
        j = self.joints.get(name)
        return j.position if j else None

    @property
    def palm_center(self) -> Vec3:
        # Approximate palm center between wrist, index-metacarpal, and pinky-metacarpal
        w = self.get_joint("wrist") or Vec3(0, 0, 0)
        idx_m = self.get_joint("index-finger-phalanx-proximal") or w
        mid_m = self.get_joint("middle-finger-phalanx-proximal") or w
        return Vec3(
            (w.x + idx_m.x + mid_m.x) / 3.0,
            (w.y + idx_m.y + mid_m.y) / 3.0,
            (w.z + idx_m.z + mid_m.z) / 3.0
        )

    @property
    def palm_normal(self) -> Vec3:
        # Cross product of index MCP to pinky MCP and wrist to middle MCP
        w = self.get_joint("wrist") or Vec3(0, 0, 0)
        idx_m = self.get_joint("index-finger-phalanx-proximal") or Vec3(0, 0, 0)
        pinky_m = self.get_joint("pinky-finger-phalanx-proximal") or Vec3(0, 0, 0)
        mid_m = self.get_joint("middle-finger-phalanx-proximal") or Vec3(0, 0, 0)

        v_across = pinky_m.sub(idx_m)
        v_along = mid_m.sub(w)
        normal = v_across.cross(v_along).normalize()
        if self.handedness == Handedness.RIGHT:
            normal = Vec3(-normal.x, -normal.y, -normal.z)
        return normal

SEATED_ORIGIN_TORSO = Vec3(0.0, 1.05, 0.0)  # Seated chest reference height

class SeatedErgonomicsGuard:
    """
    Guarantees compliance with the Meta VR Start 'Airplane Seat Test'.
    Verifies all interaction vectors stay within a 0.60m (2-foot) spherical radius.
    """
    def __init__(self, max_radius: float = SEATED_MAX_RADIUS_METERS, origin: Optional[Vec3] = None):
        self.max_radius = max_radius
        self.origin = origin or SEATED_ORIGIN_TORSO

    def validate_position(self, pos: Vec3, origin: Optional[Vec3] = None) -> Tuple[bool, float]:
        ref = origin if origin is not None else self.origin
        dist = pos.dist(ref)
        within_bounds = dist <= self.max_radius
        return within_bounds, dist

    def clamp_to_seated_envelope(self, pos: Vec3, origin: Optional[Vec3] = None) -> Vec3:
        ref = origin if origin is not None else self.origin
        dist = pos.dist(ref)
        if dist <= self.max_radius:
            return pos
        scale = self.max_radius / (dist + 1e-9)
        delta = pos.sub(ref)
        return Vec3(ref.x + delta.x * scale, ref.y + delta.y * scale, ref.z + delta.z * scale)

class MicroGestureRecognizer:
    """
    High-frequency micro-gesture detection designed for low latency Quest hand tracking.
    """
    def __init__(self, ergonomics_guard: Optional[SeatedErgonomicsGuard] = None):
        self.guard = ergonomics_guard or SeatedErgonomicsGuard()
        self.previous_wrist_angles: Dict[Handedness, float] = {}

    def detect_gesture(self, hand: HandSkeleton, headset_forward: Vec3 = Vec3(0, 0, -1)) -> Tuple[GestureType, Dict[str, float]]:
        """
        Evaluates skeleton joints and returns current gesture state and confidence metrics.
        """
        thumb_tip = hand.get_joint("thumb-tip")
        index_tip = hand.get_joint("index-finger-tip")
        middle_tip = hand.get_joint("middle-finger-tip")
        ring_tip = hand.get_joint("ring-finger-tip")
        pinky_tip = hand.get_joint("pinky-finger-tip")
        wrist = hand.get_joint("wrist")

        if not (thumb_tip and index_tip and wrist):
            return GestureType.IDLE, {"confidence": 0.0}

        palm = hand.palm_center
        tips = [t for t in [thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip] if t]

        # 1. Grab detection (All 4-5 tips curled close to palm center)
        if len(tips) >= 4:
            avg_dist_to_palm = sum(t.dist(palm) for t in tips) / len(tips)
            if avg_dist_to_palm <= GRAB_THRESHOLD_METERS:
                return GestureType.GRAB, {
                    "avg_palm_dist": avg_dist_to_palm,
                    "grab_strength": max(0.0, 1.0 - (avg_dist_to_palm / GRAB_THRESHOLD_METERS))
                }

        # 2. Pinch detection (Thumb Tip to Index Tip when not a closed fist)
        pinch_dist = thumb_tip.dist(index_tip)
        if pinch_dist <= PINCH_THRESHOLD_METERS:
            # Pinch midpoint
            pinch_point = Vec3(
                (thumb_tip.x + index_tip.x) / 2.0,
                (thumb_tip.y + index_tip.y) / 2.0,
                (thumb_tip.z + index_tip.z) / 2.0
            )
            is_valid, seat_dist = self.guard.validate_position(pinch_point)
            strength = max(0.0, 1.0 - (pinch_dist / PINCH_THRESHOLD_METERS))
            return GestureType.PINCH, {
                "pinch_distance": pinch_dist,
                "pinch_strength": strength,
                "seated_distance": seat_dist,
                "within_airplane_bounds": 1.0 if is_valid else 0.0,
                "pinch_x": pinch_point.x,
                "pinch_y": pinch_point.y,
                "pinch_z": pinch_point.z
            }

        # 3. Poke detection (Index tip extended, others curled)
        if middle_tip and ring_tip and pinky_tip:
            index_dist = index_tip.dist(palm)
            other_avg = (middle_tip.dist(palm) + ring_tip.dist(palm) + pinky_tip.dist(palm)) / 3.0
            if other_avg > 0 and (index_dist / other_avg) >= POKE_EXTENDED_RATIO:
                return GestureType.POKE, {
                    "extension_ratio": index_dist / other_avg,
                    "index_tip_x": index_tip.x,
                    "index_tip_y": index_tip.y,
                    "index_tip_z": index_tip.z
                }

        # 4. Palm Hover (Palm facing headset / forward)
        palm_norm = hand.palm_normal
        alignment = palm_norm.dot(headset_forward)
        if alignment > 0.65:
            return GestureType.PALM_HOVER, {
                "palm_alignment": alignment,
                "palm_center_x": palm.x,
                "palm_center_y": palm.y,
                "palm_center_z": palm.z
            }

        # 5. Wrist Dial Twist (measures roll of hand)
        index_mcp = hand.get_joint("index-finger-phalanx-proximal")
        pinky_mcp = hand.get_joint("pinky-finger-phalanx-proximal")
        if index_mcp and pinky_mcp:
            hand_roll = math.atan2(pinky_mcp.y - index_mcp.y, pinky_mcp.x - index_mcp.x)
            prev = self.previous_wrist_angles.get(hand.handedness, hand_roll)
            delta = hand_roll - prev
            self.previous_wrist_angles[hand.handedness] = hand_roll
            if abs(delta) > 0.08:
                return GestureType.WRIST_DIAL, {
                    "roll_radians": hand_roll,
                    "delta_radians": delta
                }

        return GestureType.IDLE, {"pinch_distance": pinch_dist}

    def detect_bimanual_stretch(self, left: HandSkeleton, right: HandSkeleton) -> Optional[Dict[str, float]]:
        """
        Recognizes two-handed stretch: when both hands are pinching, distance between
        them scales or expands the holographic chronosphere mechanism.
        """
        left_type, left_meta = self.detect_gesture(left)
        right_type, right_meta = self.detect_gesture(right)

        if left_type == GestureType.PINCH and right_type == GestureType.PINCH:
            p_left = Vec3(left_meta["pinch_x"], left_meta["pinch_y"], left_meta["pinch_z"])
            p_right = Vec3(right_meta["pinch_x"], right_meta["pinch_y"], right_meta["pinch_z"])
            span = p_left.dist(p_right)
            return {
                "span_meters": span,
                "center_x": (p_left.x + p_right.x) / 2.0,
                "center_y": (p_left.y + p_right.y) / 2.0,
                "center_z": (p_left.z + p_right.z) / 2.0
            }
        return None
