import time
import json
import os
import sys
import numpy as np
from core.octagonal_fpt_agent import OctagonalFPTAgent

class MVPOchestrator:
    def __init__(self):
        self.agent = OctagonalFPTAgent()
        # Simple inline governance evaluator parser
        self.avoid_path = "policy_governance/hard_rules/rigid_avoidances.json"
        self.max_energy = self._load_threshold()

    def _load_threshold(self) -> float:
        if os.path.exists(self.avoid_path):
            with open(self.avoid_path, 'r') as f:
                return json.load(f)["hard_constraints"]["containment_thresholds"]["max_variational_energy"]
        return 5.0

    def start_sync_loop(self):
        print("🔥 MVP ORCHESTRATOR ONLINE — 79 Hz MASTER TICK ACTIVE")
        state = np.array([0.4, 0.3, 0.3])
        step = 0

        while True:
            # Generate a fluctuating task trajectory vector
            task_burst = np.array([np.sin(time.time()), -0.1, 0.2])
            
            # 1. Compute Phase Step (Compute Node Execution)
            output = self.agent.compute_phase_step(state, task_burst)
            energy = output["energy"]
            state = np.array(output["state"])

            # 2. Safety Intercept (Governance Evaluation)
            print(f"[Pulse {step}] Energy: {energy:.4f} | State: {[round(x, 3) for x in output['state']]}")
            
            if energy > self.max_energy:
                print(f"\n🚨 [CRITICAL HALT] Energy spike ({energy:.2f} > {self.max_energy:.1f}). Circuit broken.")
                print("🛡️ LLC DEAD-MAN SWITCH ACTIVATED — GROUNDING STATE TO 0 K.")
                sys.exit(1)

            step += 1
            # Maintain the 79 Hz Time-Operator Frequency Tracking cadence
            time.sleep(1 / 79)

if __name__ == "__main__":
    # Ensure folder scaffolding is present dynamically
    os.makedirs("policy_governance/hard_rules", exist_ok=True)
    os.makedirs("core", exist_ok=True)
    
    orchestrator = MVPOchestrator()
    try:
        orchestrator.start_sync_loop()
    except KeyboardInterrupt:
        print("\nSKODEN — The flame is sustained cleanly.")
