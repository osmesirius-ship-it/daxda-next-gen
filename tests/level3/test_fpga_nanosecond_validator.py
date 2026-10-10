r"""
Tests for FPGA Nanosecond Policy Validator.
Verifies synthesizable Verilog RTL generation, cycle-accurate pipeline simulation,
deterministic latency bounds (<= 100 ns), and PCIe Gen4 x16 DMA transfers.
"""

import pytest

from daxda_engine.level3.fpga_nanosecond_validator import (
    RTLGenerationConfig,
    FPGARTLGenerator,
    PipelineRunMetrics,
    CycleAccurateFPGASimulator,
    DMADescriptor,
    PCIeGen4x16DMAManager,
    PCIE_GEN4_X16_THEORETICAL_GB_S,
)


def test_rtl_verilog_generation():
    r"""Verify synthesizable Verilog generation contains required ports and timing definitions."""
    cfg = RTLGenerationConfig(
        module_name="daxda_core_v1",
        data_width_bits=64,
        pipeline_stages=5,
        clock_frequency_mhz=250.0,
    )
    generator = FPGARTLGenerator(cfg)
    v_code = generator.generate_verilog_source()

    assert "module daxda_core_v1" in v_code
    assert "s_axis_tdata" in v_code
    assert "s_axis_tvalid" in v_code
    assert "s_axis_tready" in v_code
    assert "m_axis_tdata" in v_code
    assert "m_axis_tvalid" in v_code
    assert "m_axis_tready" in v_code
    assert "endmodule" in v_code
    assert generator.deterministic_latency_ns == 20.0  # 5 cycles * 4 ns


def test_cycle_accurate_pipeline_latency_bound():
    r"""Verify pipeline execution respects deterministic sub-100ns latency bound."""
    # 25 stages at 250 MHz (4 ns clock) = 100 ns
    sim_100ns = CycleAccurateFPGASimulator(pipeline_stages=25, clock_frequency_mhz=250.0)
    assert sim_100ns.deterministic_latency_ns == 100.0

    inputs = [0xDEADBEEF, 0x12345678, 0xCAFEBABE, 0x55AA55AA]
    out, metrics = sim_100ns.run_simulation(inputs)

    assert metrics.meets_100ns_bound is True
    assert metrics.decision_latency_ns == 100.0
    assert metrics.frames_processed == len(inputs)


def test_pipeline_execution_and_throughput():
    r"""Verify cycle-accurate simulation processes continuous streams at high throughput."""
    sim = CycleAccurateFPGASimulator(pipeline_stages=5, clock_frequency_mhz=250.0)
    inputs = [i * 101 + 7 for i in range(200)]

    out, metrics = sim.run_simulation(inputs)

    assert metrics.frames_processed == 200
    assert metrics.pipeline_stalls == 0
    assert metrics.throughput_mpps > 200.0  # > 200 Million packets per second
    assert len(out) == 200


def test_pcie_dma_manager():
    r"""Verify PCIe Gen4 x16 DMA descriptor queueing and bandwidth calculation."""
    dma = PCIeGen4x16DMAManager(ring_capacity=512)

    desc1 = dma.submit_dma_transfer(source_addr=0x1000, dest_addr=0x2000, length_bytes=4096)
    desc2 = dma.submit_dma_transfer(source_addr=0x3000, dest_addr=0x4000, length_bytes=8192)

    assert desc1.is_completed is False
    assert desc2.is_completed is False

    completed = dma.execute_transfers()
    assert completed == 2
    assert desc1.is_completed is True
    assert desc2.is_completed is True
    assert dma.total_bytes_transferred == 12288

    # Check transfer time for 4 KB: ~ 130 ns at 31.5 GB/s
    t_ns = dma.calculate_transfer_time_ns(4096)
    assert 100.0 < t_ns < 150.0
    assert PCIE_GEN4_X16_THEORETICAL_GB_S > 30.0
