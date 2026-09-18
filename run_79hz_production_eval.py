from vault.graph import StateTopologyObserver
import sys
import os
import time

sys.path.insert(0, os.path.expanduser("~/GitHub_Workspace/Platform"))

from vault.client import VaultClient
from vault.schemas import ActionProposal, MetricSnapshot
import core.loop_79hz as loop_module

class ProductionPlatformState(loop_module.PlatformState):
    def __init__(self):
        self.applied = []
        self.denied = []

    def collect_metrics(self) -> list[MetricSnapshot]:
        return [MetricSnapshot(
            source="loop_79hz",
            timestamp=time.time(),
            metrics={"tick_hz": 79.0, "latency_ms": 12.65}
        )]

    def log_gate_denial(self, action: ActionProposal, reason: str) -> None:
        self.denied.append((action.action_id, reason))

    def log_gate_modify(self, original: ActionProposal, patched: ActionProposal, reason: str) -> None:
        pass

def propose_actions(state, metrics):
    idx = len(state.applied) + len(state.denied)
    # Trip boundary protection on cycle 30
    if idx == 30:
        return [ActionProposal(
            action_id=f"eval_act_{idx:03d}",
            actor="orchestrator",
            action_type="PRIVILEGED_PROBE",
            params={"command": "cat /etc/passwd", "target_path": "/etc", "risk_tier": 2}
        )]
    return [ActionProposal(
        action_id=f"eval_act_{idx:03d}",
        actor="orchestrator",
        action_type="CYCLE_STEP",
        params={"command": f"echo STEP_{idx:03d}", "target_path": "./workspace", "risk_tier": 1}
    )]

def apply_action(state, action: ActionProposal):
    state.applied.append(action.action_id)

loop_module.propose_actions = propose_actions
loop_module.apply_action = apply_action

client = VaultClient.from_uds(timeout=0.75)
state = ProductionPlatformState()
obs = StateTopologyObserver()
buffer = []

print("[*] Dispatching 79 cycles across Platform loop_79hz -> FPT -> Heterosis...")
t_start = time.time()

for t in range(79):
    t0 = time.time()
    state = loop_module.tick(state, client, buffer)
    if client.latest_substrate_seq is not None:
        ok, reason, gstats = obs.record_transition(
            action_id=f"tick_{t:03d}",
            seq=client.latest_substrate_seq,
            damping=client.latest_damping,
            anchor=getattr(client, "latest_egress_receipt", "none") or "none"
        )
        if not ok:
            print(f"[!] Topology invariant violation at tick {t}: {reason}")
    dt = (time.time() - t0) * 1000.0
    if t % 10 == 0 or t in (30, 31):
        print(
            f"Tick {t:2d} | dt={dt:5.2f}ms | Damping={client.latest_damping:.3f} | "
            f"Substrate Seq={client.latest_substrate_seq} | Applied={len(state.applied)} | Denied={len(state.denied)}"
        )
    time.sleep(0.012)

total_elapsed = time.time() - t_start
print(f"\n[+] Completed 79 cycles in {total_elapsed:.2f}s.")
print(f"[+] Total Applied: {len(state.applied)} | Total Denied: {len(state.denied)}")
