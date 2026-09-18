import pytest
from vault.graph import StateTopologyObserver

def test_state_topology_nominal_progression():
    obs = StateTopologyObserver()
    ok, reason, stats = obs.record_transition("act_001", 100, 0.35, "anchor_001")
    assert ok is True
    assert reason == "NOMINAL"
    assert stats["dag_nodes"] == 1
    assert stats["dag_edges"] == 0

    ok, reason, stats = obs.record_transition("act_002", 101, 0.35, "anchor_002")
    assert ok is True
    assert stats["dag_nodes"] == 2
    assert stats["dag_edges"] == 1

def test_state_topology_monotonicity_violation():
    obs = StateTopologyObserver()
    obs.record_transition("act_001", 100, 0.35, "anchor_001")
    ok, reason, stats = obs.record_transition("act_bad", 99, 0.90, "anchor_bad")
    assert ok is False
    assert "Sequence monotonicity violation" in reason

def test_state_topology_duplicate_seq_violation():
    obs = StateTopologyObserver()
    obs.record_transition("act_001", 100, 0.35, "anchor_001")
    ok, reason, stats = obs.record_transition("act_dup", 100, 0.35, "anchor_dup")
    assert ok is False
    assert "Sequence monotonicity violation" in reason
