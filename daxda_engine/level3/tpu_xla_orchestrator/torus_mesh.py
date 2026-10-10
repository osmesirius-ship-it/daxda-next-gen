r"""
2D Toroidal Mesh Interconnect Engine for Google Cloud TPU v4/v5e Pods.
Models wrap-around torus topology, optical circuit switch (OCS) interconnects,
and collective communication latencies across up to 256 TPU chips.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import math
import numpy as np


TPU_V4_LINK_BANDWIDTH_TBPS: float = 4.8   # 4.8 Terabits/sec per TPU v4 optical link
TPU_INTERCONNECT_HOP_LATENCY_US: float = 0.45 # 450 ns per torus hop


@dataclass(frozen=True)
class CollectiveCommunicationResult:
    """Outcome of collective communication primitive on 2D torus."""
    operation_name: str
    total_payload_bytes: int
    collective_latency_ms: float
    max_hops_traversed: int
    effective_bandwidth_gb_s: float
    meets_15ms_p99_target: bool


class TPU2DTorusMesh:
    r"""
    Models a 2D toroidal mesh interconnect for Google Cloud TPU Pods:
    dim_x \times dim_y chips with periodic wrap-around boundary conditions.
    """

    def __init__(
        self,
        mesh_shape: Tuple[int, int] = (16, 16), # Default 256 TPU chips
        link_bandwidth_tbps: float = TPU_V4_LINK_BANDWIDTH_TBPS,
        hop_latency_us: float = TPU_INTERCONNECT_HOP_LATENCY_US,
    ):
        self.nx, self.ny = mesh_shape
        self.total_chips = self.nx * self.ny
        self.bandwidth_gb_s = (link_bandwidth_tbps * 1e12) / (8.0 * 1e9) # Convert to GB/s
        self.hop_latency_ms = hop_latency_us * 1e-3

    def torus_distance(self, chip_a: int, chip_b: int) -> int:
        r"""
        Shortest distance between two chips on periodic 2D torus:
        d = \min(|x_a - x_b|, N_x - |x_a - x_b|) + \min(|y_a - y_b|, N_y - |y_a - y_b|).
        """
        x_a, y_a = chip_a % self.nx, chip_a // self.nx
        x_b, y_b = chip_b % self.nx, chip_b // self.nx

        dx = abs(x_a - x_b)
        dx_wrap = min(dx, self.nx - dx)

        dy = abs(y_a - y_b)
        dy_wrap = min(dy, self.ny - dy)

        return int(dx_wrap + dy_wrap)

    def max_torus_diameter(self) -> int:
        """Maximum shortest-path distance across any two nodes on the torus."""
        return (self.nx // 2) + (self.ny // 2)

    def simulate_ring_all_reduce(
        self,
        tensor_size_bytes: int,
        num_participants: Optional[int] = None,
    ) -> CollectiveCommunicationResult:
        r"""
        Ring All-Reduce latency model on 2D torus:
        T_{all_reduce} = 2 (P - 1) \alpha + 2 \frac{P - 1}{P} \frac{S}{B}
        where \alpha is hop latency, S is tensor size, B is ring bandwidth.
        """
        P = num_participants or self.total_chips
        if P <= 1:
            raise ValueError("All-reduce requires at least 2 chips")

        alpha_ms = self.hop_latency_ms
        # Transmitted bytes per ring step
        transfer_bytes = 2.0 * ((P - 1.0) / float(P)) * tensor_size_bytes
        transfer_time_s = transfer_bytes / (self.bandwidth_gb_s * 1e9)
        transfer_time_ms = transfer_time_s * 1e3

        latency_ms = 2.0 * (P - 1) * alpha_ms + transfer_time_ms
        diameter = self.max_torus_diameter()

        effective_bw = (tensor_size_bytes / 1e9) / (latency_ms * 1e-3) if latency_ms > 0 else 0.0

        return CollectiveCommunicationResult(
            operation_name="Ring All-Reduce",
            total_payload_bytes=tensor_size_bytes,
            collective_latency_ms=latency_ms,
            max_hops_traversed=diameter,
            effective_bandwidth_gb_s=effective_bw,
            meets_15ms_p99_target=latency_ms < 15.0,
        )

    def simulate_all_to_all(
        self,
        tensor_size_bytes: int,
    ) -> CollectiveCommunicationResult:
        r"""
        All-to-all transpose exchange on 2D torus:
        T_{all_to_all} = (P - 1) \alpha + \frac{P - 1}{P} \frac{S}{B}.
        """
        P = self.total_chips
        alpha_ms = self.hop_latency_ms
        transfer_bytes = ((P - 1.0) / float(P)) * tensor_size_bytes
        transfer_time_ms = (transfer_bytes / (self.bandwidth_gb_s * 1e9)) * 1e3

        latency_ms = (P - 1) * alpha_ms + transfer_time_ms
        diameter = self.max_torus_diameter()
        effective_bw = (tensor_size_bytes / 1e9) / (latency_ms * 1e-3) if latency_ms > 0 else 0.0

        return CollectiveCommunicationResult(
            operation_name="All-to-All",
            total_payload_bytes=tensor_size_bytes,
            collective_latency_ms=latency_ms,
            max_hops_traversed=diameter,
            effective_bandwidth_gb_s=effective_bw,
            meets_15ms_p99_target=latency_ms < 15.0,
        )
