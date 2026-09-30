"""
Unit Tests for Chrono Causal Mapping: DAG construction, topological sort, loop detection.
"""

import pytest
from daxda_engine.chrono.geometry.temporal_space import (
    TemporalCoordinate,
    TemporalState,
    TemporalSpace,
)
from daxda_engine.chrono.validation.causal_mapper import CausalMapper


class TestCausalMapping:

    def test_causal_dag_construction_and_topological_sort(self):
        space = TemporalSpace()
        s1 = TemporalState(state_id="A", coordinate=TemporalCoordinate(t=1.0), decision_vector=[0.1])
        s2 = TemporalState(state_id="B", coordinate=TemporalCoordinate(t=2.0), decision_vector=[0.2])
        s3 = TemporalState(state_id="C", coordinate=TemporalCoordinate(t=3.0), decision_vector=[0.3])
        space.add_state(s1)
        space.add_state(s2)
        space.add_state(s3)

        mapper = CausalMapper(space)
        mapper.add_causal_relation("A", "B", coupling_weight=0.9)
        mapper.add_causal_relation("B", "C", coupling_weight=0.8)

        # Topological order should be A -> B -> C
        topo = mapper.topological_sort()
        assert topo == ["A", "B", "C"]

        # Forward cone of A
        assert mapper.get_forward_cone("A") == {"B", "C"}
        # Backward cone of C
        assert mapper.get_backward_cone("C") == {"A", "B"}

        # Causal coupling from A to C: 0.9 * 0.8 = 0.72
        coupling = mapper.compute_causal_coupling("A", "C")
        assert round(coupling, 4) == 0.72

    def test_causal_loop_detection(self):
        space = TemporalSpace()
        for name in ["N1", "N2", "N3"]:
            space.add_state(TemporalState(state_id=name, coordinate=TemporalCoordinate(t=1.0), decision_vector=[0.5]))

        mapper = CausalMapper(space)
        mapper.add_causal_relation("N1", "N2")
        mapper.add_causal_relation("N2", "N3")
        mapper.add_causal_relation("N3", "N1")  # Cycle!

        loops = mapper.detect_causal_loops()
        assert len(loops) > 0
        # Topological sort on cyclic graph must return None
        assert mapper.topological_sort() is None
