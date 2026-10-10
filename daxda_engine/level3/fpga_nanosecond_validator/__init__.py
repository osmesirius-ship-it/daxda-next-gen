r"""
DAXDA Level 3: FPGA Nanosecond Validator Engine.
Implements synthesizable Verilog RTL generator, cycle-accurate pipeline simulation,
and PCIe Gen4 x16 AXI4-Stream DMA manager.
"""

from .rtl_generator import (
    RTLGenerationConfig,
    FPGARTLGenerator,
)
from .cycle_accurate_sim import (
    PipelineRunMetrics,
    CycleAccurateFPGASimulator,
)
from .dma_interface import (
    DMADescriptor,
    PCIeGen4x16DMAManager,
    PCIE_GEN4_X16_THEORETICAL_GB_S,
)

__all__ = [
    "RTLGenerationConfig",
    "FPGARTLGenerator",
    "PipelineRunMetrics",
    "CycleAccurateFPGASimulator",
    "DMADescriptor",
    "PCIeGen4x16DMAManager",
    "PCIE_GEN4_X16_THEORETICAL_GB_S",
]
