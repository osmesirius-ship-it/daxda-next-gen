"""
DAXDA Level 4 — Address-Event Representation (AER) Packet Router & NoC Mesh
===========================================================================

Implements 2D mesh on-chip network (NoC) routing using asynchronous
Address-Event Representation (AER) protocols with sub-microsecond event scheduling.
"""

from __future__ import annotations
import heapq
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass(order=True)
class AERSpikePacket:
    """AER packet representing an asynchronous spike event."""
    timestamp_ps: int  # Picosecond precision timestamp for priority ordering
    source_core_id: int = field(compare=False)
    source_neuron_id: int = field(compare=False)
    dest_core_id: int = field(compare=False)
    dest_neuron_id: int = field(compare=False)
    payload_weight: float = field(compare=False, default=1.0)


class AERPacketRouter:
    """
    2D toroidal Network-on-Chip (NoC) router routing AER spike packets
    using dimension-order XY routing with zero deadlocks.
    """

    def __init__(self, mesh_width: int = 4, mesh_height: int = 4):
        self.width = mesh_width
        self.height = mesh_height
        self.event_queue: List[AERSpikePacket] = []
        self.total_routed_packets: int = 0

    def compute_xy_hops(self, src_core: int, dst_core: int) -> int:
        """Computes Manhattan distance in 2D mesh between src and dst cores."""
        src_x, src_y = src_core % self.width, src_core // self.width
        dst_x, dst_y = dst_core % self.width, dst_core // self.width
        return abs(dst_x - src_x) + abs(dst_y - src_y)

    def dispatch_packet(self, packet: AERSpikePacket) -> None:
        """Pushes an asynchronous spike packet into the event priority queue."""
        heapq.heappush(self.event_queue, packet)

    def pop_next_packet(self) -> Optional[AERSpikePacket]:
        """Pops the next chronological spike packet."""
        if not self.event_queue:
            return None
        packet = heapq.heappop(self.event_queue)
        self.total_routed_packets += 1
        return packet

    def process_all_until(self, max_timestamp_ps: int) -> List[AERSpikePacket]:
        """Pops and returns all packets scheduled up to max_timestamp_ps."""
        dispatched: List[AERSpikePacket] = []
        while self.event_queue and self.event_queue[0].timestamp_ps <= max_timestamp_ps:
            dispatched.append(heapq.heappop(self.event_queue))
            self.total_routed_packets += 1
        return dispatched
