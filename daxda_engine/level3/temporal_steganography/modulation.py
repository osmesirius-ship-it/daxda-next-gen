r"""
Covert Timing Modulation and Steganographic Embedding Engine.
Embeds and extracts covert binary bitstreams inside packet inter-arrival times (IATs)
via interval-dithering and pulse-interval modulation.
"""

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np


@dataclass(frozen=True)
class ModulatedPacketStream:
    """Packet stream containing either clean baseline or covert modulated IATs."""
    timestamps_seconds: np.ndarray      # Monotonically increasing arrival times
    inter_arrival_times: np.ndarray     # \Delta t_k = t_{k+1} - t_k
    is_covert_injected: bool
    embedded_payload_bits: str
    dither_magnitude_seconds: float


class CovertTimingModulator:
    r"""
    Modulates packet arrival times to embed a hidden binary message:
    \Delta t_k = \Delta t_{base} + \delta \cdot (2 b_k - 1).
    """

    def __init__(
        self,
        mean_iat_seconds: float = 0.05,  # 50 ms default mean packet spacing (20 pps)
        dither_magnitude_seconds: float = 0.015, # 15 ms modulation depth
    ):
        self.mean_iat = mean_iat_seconds
        self.dither = dither_magnitude_seconds

    def generate_baseline_traffic(
        self,
        num_packets: int = 500,
        seed: int = 42,
    ) -> ModulatedPacketStream:
        """Generates legitimate baseline Poisson traffic with exponential IAT distribution."""
        rng = np.random.default_rng(seed)
        # Exponential distribution for Poisson arrivals
        iats = rng.exponential(scale=self.mean_iat, size=num_packets)
        iats = np.maximum(iats, 0.001)  # Floor at 1 ms to prevent zero/negative times

        timestamps = np.cumsum(np.insert(iats, 0, 0.0))[1:]

        return ModulatedPacketStream(
            timestamps_seconds=timestamps,
            inter_arrival_times=iats,
            is_covert_injected=False,
            embedded_payload_bits="",
            dither_magnitude_seconds=0.0,
        )

    def inject_covert_message(
        self,
        binary_payload: str,
        num_packets: int = 500,
        seed: int = 42,
    ) -> ModulatedPacketStream:
        r"""
        Embeds binary message (e.g. '1011001') into packet IATs:
        Bit 0: IAT = mean - dither
        Bit 1: IAT = mean + dither
        with background Gaussian packet jitter.
        """
        rng = np.random.default_rng(seed)
        # Repeat payload to fill packets if necessary
        bits = [int(b) for b in binary_payload]
        if not bits:
            raise ValueError("Payload must not be empty")

        bit_stream = [bits[i % len(bits)] for i in range(num_packets)]

        # Modulate IATs
        iats = np.zeros(num_packets, dtype=np.float64)
        for i, b in enumerate(bit_stream):
            # Baseline mean with binary offset and mild jitter
            shift = self.dither if b == 1 else -self.dither
            jitter = rng.normal(0.0, self.dither * 0.2)
            iats[i] = max(0.001, self.mean_iat + shift + jitter)

        timestamps = np.cumsum(np.insert(iats, 0, 0.0))[1:]

        return ModulatedPacketStream(
            timestamps_seconds=timestamps,
            inter_arrival_times=iats,
            is_covert_injected=True,
            embedded_payload_bits=binary_payload,
            dither_magnitude_seconds=self.dither,
        )

    def demodulate_covert_message(
        self,
        inter_arrival_times: np.ndarray,
        payload_length: int,
    ) -> str:
        """Demodulates binary bits by thresholding IATs around mean_iat."""
        bits = []
        for iat in inter_arrival_times[:payload_length]:
            bits.append("1" if iat > self.mean_iat else "0")
        return "".join(bits)
