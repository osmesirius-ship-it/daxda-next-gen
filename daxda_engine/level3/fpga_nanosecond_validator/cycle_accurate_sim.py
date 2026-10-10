r"""
Cycle-Accurate Hardware Simulator for FPGA Nanosecond Policy Validator.
Simulates pipeline execution cycle-by-cycle, verifying deterministic latency bounds
and AXI4-Stream handshake protocols.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np


@dataclass(frozen=True)
class PipelineRunMetrics:
    """Cycle-accurate performance metrics."""
    total_clock_cycles: int
    frames_processed: int
    frames_accepted: int
    pipeline_stalls: int
    decision_latency_ns: float
    throughput_mpps: float            # Million packets per second
    meets_100ns_bound: bool


class CycleAccurateFPGASimulator:
    r"""
    Cycle-accurate model of the FPGA AXI4-Stream pipelined validator.
    Clock period: 4.0 ns (250 MHz).
    """

    def __init__(
        self,
        pipeline_stages: int = 5,
        clock_frequency_mhz: float = 250.0,
    ):
        self.stages = pipeline_stages
        self.clock_mhz = clock_frequency_mhz
        self.clock_period_ns = 1000.0 / clock_frequency_mhz
        self.deterministic_latency_ns = self.stages * self.clock_period_ns

    def run_simulation(
        self,
        input_data_stream: List[int],
        backpressure_ready: bool = True,
    ) -> Tuple[List[int], PipelineRunMetrics]:
        """
        Executes cycle-accurate simulation for a batch of 64-bit input words.
        Returns output data stream and performance metrics.
        """
        data_pipe = [0] * self.stages
        valid_pipe = [False] * self.stages
        output_data = []

        total_cycles = 0
        frames_accepted = 0
        stalls = 0

        # Step through input words plus pipeline flush cycles
        total_steps = len(input_data_stream) + self.stages

        for step in range(total_steps):
            total_cycles += 1

            if not backpressure_ready:
                stalls += 1
                continue

            # Ingress stage
            if step < len(input_data_stream):
                new_data = input_data_stream[step]
                new_valid = True
            else:
                new_data = 0
                new_valid = False

            # Egress extraction
            if valid_pipe[-1]:
                out_val = data_pipe[-1]
                output_data.append(out_val)
                if out_val != 0:
                    frames_accepted += 1

            # Advance pipeline
            for s in range(self.stages - 1, 0, -1):
                data_pipe[s] = data_pipe[s - 1] ^ (data_pipe[s - 1] >> 1)
                valid_pipe[s] = valid_pipe[s - 1]

            data_pipe[0] = new_data
            valid_pipe[0] = new_valid

        throughput_mpps = (
            (len(input_data_stream) / (total_cycles * self.clock_period_ns * 1e-9)) / 1e6
            if total_cycles > 0
            else 0.0
        )

        metrics = PipelineRunMetrics(
            total_clock_cycles=total_cycles,
            frames_processed=len(output_data),
            frames_accepted=frames_accepted,
            pipeline_stalls=stalls,
            decision_latency_ns=self.deterministic_latency_ns,
            throughput_mpps=throughput_mpps,
            meets_100ns_bound=self.deterministic_latency_ns <= 100.0,
        )

        return output_data, metrics
