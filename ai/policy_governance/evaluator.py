#!/usr/bin/env python3
"""Sovereign Policy Guard and Safety Evaluator."""

from __future__ import annotations
import json
import os
from typing import Any, Dict, Optional, Tuple


class SovereignPolicyGuard:
    def __init__(self, base_path: Optional[str] = None, rules_path: Optional[str] = None):
        self.base_path = base_path or os.path.dirname(__file__)
        self.rules_path = rules_path or os.path.join(self.base_path, "hard_rules", "rigid_avoidances.json")
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        if os.path.exists(self.rules_path):
            with open(self.rules_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def verify_runtime_safety(self, action: str, metrics: Dict[str, float]) -> bool:
        constraints = self.rules.get("hard_constraints", {})
        prohibited = constraints.get("prohibited_actions", [])

        # Check prohibited action strings
        if any(p == action or p in action for p in prohibited):
            return False

        # Check containment thresholds
        thresholds = constraints.get("containment_thresholds", {})
        max_energy = thresholds.get("max_variational_energy")
        if max_energy is not None and metrics.get("variational_energy", 0.0) > max_energy:
            return False

        max_drift = thresholds.get("max_cognitive_drift")
        if max_drift is not None and metrics.get("cognitive_drift", 0.0) > max_drift:
            return False

        return True

    def evaluate_proposal(self, proposal: Dict[str, Any]) -> Tuple[bool, str]:
        action_name = proposal.get("action", proposal.get("command", ""))
        metrics = proposal.get("metrics", {})
        if not self.verify_runtime_safety(action_name, metrics):
            return False, "Runtime safety envelope violated."
        return True, "Policy check passed."

    def evaluate(self, proposal: Any) -> Tuple[bool, str]:
        if isinstance(proposal, dict):
            return self.evaluate_proposal(proposal)
        prop_dict = {
            "action": getattr(proposal, "action_id", ""),
            "command": getattr(proposal, "command", ""),
            "metrics": getattr(proposal, "metrics", {}),
        }
        return self.evaluate_proposal(prop_dict)
