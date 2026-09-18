"""
vault/graph.py
Bridge module connecting Platform 79 Hz control plane to networkXG's SovereignRelationalMesh.
Maintains strict DAG state transition invariants alongside relational mesh dynamics.
"""

from __future__ import annotations
import sys
import os
import contextlib
import io
from typing import Tuple, Dict, Any

# Ensure networkXG is accessible on sys.path
NETWORKXG_DIR = os.path.expanduser("~/networkXG")
if NETWORKXG_DIR not in sys.path:
    sys.path.insert(0, NETWORKXG_DIR)

# Suppress un-guarded top-level prints in legacy demo files during import
with contextlib.redirect_stdout(io.StringIO()):
    try:
        from networkxg.relational_mesh import SovereignRelationalMesh
    except ImportError:
        from relational_mesh import SovereignRelationalMesh  # type: ignore

import networkx as nx

class StateTopologyObserver:
    def __init__(self, pulse_freq: float = 79.79) -> None:
        self.mesh = SovereignRelationalMesh()
        self.mesh.pulse_freq = pulse_freq
        self.causal_dag = nx.DiGraph()
        self.transition_log = []
        self.latest_seq = None
        self.latest_node = None

    def record_transition(
        self,
        action_id: str,
        seq: int,
        damping: float,
        anchor: str
    ) -> Tuple[bool, str, Dict[str, Any]]:
        # Invariant 1: Strict Monotonic Sequence Progression
        if self.latest_seq is not None and seq <= self.latest_seq:
            return False, f"Sequence monotonicity violation: {seq} <= {self.latest_seq}", {}

        node_name = f"seq_{seq}:{action_id}"

        # 1. Update directed causal lineage graph (Forward DAG strictly)
        self.causal_dag.add_node(
            node_name,
            seq=seq,
            action_id=action_id,
            damping=damping,
            anchor=str(anchor)[:16]
        )
        if self.latest_node is not None:
            self.causal_dag.add_edge(self.latest_node, node_name, weight=damping)

        # Invariant 2: Structural Acyclicity
        if not nx.is_directed_acyclic_graph(self.causal_dag):
            return False, "Causal cycle detected in state lineage", {}

        # 2. Update bidirectional relational mesh & propagate soliton
        prev_mesh_node = self.latest_node if self.latest_node is not None else "root_genesis"
        self.mesh.add_relational_unit(
            agent1=prev_mesh_node,
            agent2=node_name,
            context=f"anchor={str(anchor)[:12]}",
            obligation=float(damping)
        )
        self.mesh.propagate_soliton(source=node_name, strength=1.0 - min(1.0, damping))

        self.latest_seq = seq
        self.latest_node = node_name
        self.transition_log.append((seq, action_id, damping, anchor))

        stats = {
            "dag_nodes": self.causal_dag.number_of_nodes(),
            "dag_edges": self.causal_dag.number_of_edges(),
            "mesh_reciprocity": round(float(self.mesh.mesh_reciprocity_score()), 4),
            "latest_seq": seq,
            "damping": damping,
        }
        return True, "NOMINAL", stats
