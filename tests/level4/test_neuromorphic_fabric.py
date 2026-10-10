"""
Tests for DAXDA Level 4 — Domain 3: Neuromorphic Spiking Fabric & AER Mesh Routing
"""

import numpy as np
import pytest

from daxda_engine.level4.neuromorphic_fabric import (
    NeuromorphicSpikingCore,
    STDPSynapseMatrix,
    AERPacketRouter,
    AERSpikePacket,
)


def test_lif_neuron_spiking_and_refractory():
    core = NeuromorphicSpikingCore(neuron_count=5, model_type="lif")
    
    # Low current -> no spikes
    spikes_sub = core.step_simulation(dt_ms=1.0, current_injections_pA=np.zeros(5))
    assert len(spikes_sub) == 0
    
    # Strong current -> spikes emitted
    spikes_supra = core.step_simulation(
        dt_ms=5.0, current_injections_pA=np.full(5, 1000.0)
    )
    assert len(spikes_supra) > 0
    assert core.spike_counts[0] >= 1


def test_izhikevich_neuron_dynamics():
    core = NeuromorphicSpikingCore(neuron_count=2, model_type="izhikevich")
    spikes = core.step_simulation(
        dt_ms=10.0, current_injections_pA=np.full(2, 50.0)
    )
    assert isinstance(spikes, list)


def test_stdp_synapse_adaptation():
    synapse = STDPSynapseMatrix(n_pre=2, n_post=2, initial_weight=0.5)
    
    # Pre before post (LTP potentiation: dt > 0)
    event_ltp = synapse.apply_stdp_event(
        pre_id=0, post_id=1, pre_spike_time_ms=10.0, post_spike_time_ms=15.0
    )
    assert event_ltp.delta_weight > 0
    assert event_ltp.new_weight > 0.5
    
    # Post before pre (LTD depression: dt < 0)
    event_ltd = synapse.apply_stdp_event(
        pre_id=1, post_id=0, pre_spike_time_ms=25.0, post_spike_time_ms=20.0
    )
    assert event_ltd.delta_weight < 0
    assert event_ltd.new_weight < 0.5


def test_aer_packet_routing_and_scheduling():
    router = AERPacketRouter(mesh_width=4, mesh_height=4)
    
    # Distance between core 0 (0,0) and core 5 (1,1) is 2
    hops = router.compute_xy_hops(0, 5)
    assert hops == 2
    
    p1 = AERSpikePacket(timestamp_ps=300, source_core_id=0, source_neuron_id=1, dest_core_id=5, dest_neuron_id=2)
    p2 = AERSpikePacket(timestamp_ps=100, source_core_id=1, source_neuron_id=3, dest_core_id=2, dest_neuron_id=4)
    
    router.dispatch_packet(p1)
    router.dispatch_packet(p2)
    
    # Earliest timestamp must be popped first
    first = router.pop_next_packet()
    assert first is not None
    assert first.timestamp_ps == 100
    
    second = router.pop_next_packet()
    assert second is not None
    assert second.timestamp_ps == 300
