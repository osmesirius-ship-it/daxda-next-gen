r"""
PCIe Gen4 x16 Direct Memory Access (DMA) Descriptor Interface.
Models ring buffer DMA descriptors, high-bandwidth burst transfers (up to 31.5 GB/s),
and packet framing for the FPGA validator core.
"""

from dataclasses import dataclass
from typing import List, Optional
import math
import numpy as np


PCIE_GEN4_X16_THEORETICAL_GB_S: float = 31.508  # 16 lanes * 16 GT/s * (128/130) / 8


@dataclass
class DMADescriptor:
    """PCIe DMA transfer descriptor."""
    descriptor_id: int
    source_address: int
    destination_address: int
    length_bytes: int
    is_completed: bool = False
    error_flags: int = 0


class PCIeGen4x16DMAManager:
    r"""
    Manages host-to-FPGA DMA transfers over PCIe Gen4 x16 interconnects.
    """

    def __init__(self, ring_capacity: int = 1024):
        self.capacity = ring_capacity
        self.descriptors: List[DMADescriptor] = []
        self.head_ptr = 0
        self.tail_ptr = 0
        self.total_bytes_transferred = 0

    def submit_dma_transfer(
        self,
        source_addr: int,
        dest_addr: int,
        length_bytes: int,
    ) -> DMADescriptor:
        """Enqueues a DMA descriptor into the ring buffer."""
        desc_id = len(self.descriptors)
        desc = DMADescriptor(
            descriptor_id=desc_id,
            source_address=source_addr,
            destination_address=dest_addr,
            length_bytes=length_bytes,
            is_completed=False,
        )
        self.descriptors.append(desc)
        self.head_ptr = (self.head_ptr + 1) % self.capacity
        return desc

    def execute_transfers(self) -> int:
        """Processes all pending DMA descriptors and marks them completed."""
        completed_count = 0
        for desc in self.descriptors:
            if not desc.is_completed:
                desc.is_completed = True
                self.total_bytes_transferred += desc.length_bytes
                completed_count += 1
        self.tail_ptr = self.head_ptr
        return completed_count

    def calculate_transfer_time_ns(self, total_bytes: int) -> float:
        """Computes minimum PCIe transmission time in nanoseconds."""
        bandwidth_bytes_per_ns = PCIE_GEN4_X16_THEORETICAL_GB_S  # GB/s == bytes/ns
        return float(total_bytes / bandwidth_bytes_per_ns)
