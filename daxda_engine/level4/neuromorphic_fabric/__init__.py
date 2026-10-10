"""
DAXDA Level 4 — Domain 3: Neuromorphic Spiking Fabric
=====================================================

Hardware-accelerated spiking neural fabric with sub-microsecond event resolution,
STDP plasticity adaptation, and Address-Event Representation (AER) NoC mesh routing.
"""

from .spiking_neuron import NeuromorphicSpikingCore, SpikingNeuronState
from .stdp_synapse import STDPSynapseMatrix, STDPSynapticEvent
from .aer_mesh import AERPacketRouter, AERSpikePacket

__all__ = [
    "NeuromorphicSpikingCore",
    "SpikingNeuronState",
    "STDPSynapseMatrix",
    "STDPSynapticEvent",
    "AERPacketRouter",
    "AERSpikePacket",
]
