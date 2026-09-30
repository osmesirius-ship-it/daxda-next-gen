"""
Unit Tests for Chrono Geometry: TemporalSpace, RetrocausalEngine, SynchronicityDetector, Visualizer.
"""

import pytest
import math
from daxda_engine.chrono.geometry.temporal_space import (
    TemporalCoordinate,
    TemporalDimension,
    TemporalState,
    TemporalSpace,
)
from daxda_engine.chrono.geometry.retrocausal_engine import RetrocausalEngine
from daxda_engine.chrono.geometry.synchronicity import SynchronicityDetector
from daxda_engine.chrono.geometry.visualization import TemporalVisualizer


class TestChronoGeometry:

    def test_temporal_coordinate_intervals(self):
        c1 = TemporalCoordinate(t=10.0, b=0.0, p=0.0, tau=0.0)
        c2 = TemporalCoordinate(t=12.0, b=0.0, p=0.0, tau=0.0)
        # ds^2 = - (2)^2 = -4.0 (Timelike)
        assert c1.interval_squared(c2, c_t=1.0) == -4.0
        assert c1.is_timelike_separated(c2, c_t=1.0) is True
        assert c1.is_spacelike_separated(c2, c_t=1.0) is False

        # Spacelike separation: dt = 0, db = 3
        c3 = TemporalCoordinate(t=10.0, b=3.0, p=0.0, tau=0.0)
        assert c1.interval_squared(c3, c_t=1.0) == 9.0
        assert c1.is_spacelike_separated(c3, c_t=1.0) is True

    def test_temporal_space_indexing_and_queries(self):
        space = TemporalSpace(dimension=TemporalDimension.D4_HYPERTEMPORAL)

        for i in range(10):
            st = TemporalState(
                state_id=f"st_{i}",
                coordinate=TemporalCoordinate(t=float(i), b=float(i % 2), p=0.0, tau=0.1 * i),
                decision_vector=[0.1 * i, 0.5, 0.2],
            )
            space.add_state(st)

        assert len(space) == 10
        # Interval query [2.5, 7.5] -> states 3, 4, 5, 6, 7
        interval_states = space.query_interval(2.5, 7.5)
        assert len(interval_states) == 5
        assert [s.state_id for s in interval_states] == ["st_3", "st_4", "st_5", "st_6", "st_7"]

        # Branch query
        branch_1_states = space.query_branch(1.0)
        assert len(branch_1_states) == 5

        # Nearest neighbors
        target = TemporalCoordinate(t=4.2, b=0.0, p=0.0, tau=0.4)
        neighbors = space.find_nearest_neighbors(target, k=3)
        assert len(neighbors) == 3
        assert neighbors[0][0].state_id == "st_4"

    def test_retrocausal_influence_and_novikov_solver(self):
        space = TemporalSpace()
        s_past = TemporalState(
            state_id="past_0",
            coordinate=TemporalCoordinate(t=10.0),
            decision_vector=[0.5, 0.5, 0.5],
        )
        s_future = TemporalState(
            state_id="future_0",
            coordinate=TemporalCoordinate(t=15.0),
            decision_vector=[0.55, 0.48, 0.52],
        )
        space.add_state(s_past)
        space.add_state(s_future)

        retro_engine = RetrocausalEngine(space)
        influence = retro_engine.compute_retrocausal_influence(s_future, s_past)

        assert influence.source_state_id == "future_0"
        assert influence.target_state_id == "past_0"
        assert influence.influence_strength > 0.0
        assert influence.is_novikov_consistent is True

        # Novikov fixed point test
        loop_ids = ["past_0", "future_0"]
        is_consistent, eq_vec, res = retro_engine.solve_novikov_fixed_point(loop_ids)
        assert is_consistent is True
        assert len(eq_vec) == 3
        assert res < 0.01

    def test_synchronicity_detector(self):
        space = TemporalSpace()
        # Two states at approximately same time, spacelike separated along different parallel timelines
        s1 = TemporalState(
            state_id="agent_alpha",
            coordinate=TemporalCoordinate(t=100.0, b=0.0, p=1.0),
            decision_vector=[0.9, 0.8, 0.7, 0.6],
        )
        s2 = TemporalState(
            state_id="agent_beta",
            coordinate=TemporalCoordinate(t=100.2, b=0.0, p=2.0),
            decision_vector=[0.88, 0.82, 0.69, 0.58],  # Strongly aligned vector
        )
        space.add_state(s1)
        space.add_state(s2)

        detector = SynchronicityDetector(space, anomaly_threshold=0.70)
        event = detector.compute_synchronicity(s1, s2, direct_causal_coupling=0.0)

        assert event is not None
        assert event.cosine_similarity > 0.95
        assert event.synchronicity_score > 0.70
        assert event.is_anomaly is True

    def test_temporal_visualizer(self):
        space = TemporalSpace()
        st1 = TemporalState(state_id="s1", coordinate=TemporalCoordinate(t=1.0), decision_vector=[0.1, 0.2])
        st2 = TemporalState(state_id="s2", coordinate=TemporalCoordinate(t=2.0), decision_vector=[0.2, 0.3])
        st1.successors.add("s2")
        space.add_state(st1)
        space.add_state(st2)

        viz = TemporalVisualizer(space)
        ascii_out = viz.render_ascii_timeline()
        assert "DAXDA CHRONO-TEMPORAL TIMELINE" in ascii_out

        svg_out = viz.render_svg_diagram()
        assert "<svg" in svg_out
        assert "s1" in svg_out

        graph_json = viz.export_graph_json()
        assert graph_json["metadata"]["total_nodes"] == 2
        assert len(graph_json["links"]) == 1
