from __future__ import annotations
from cryptography.hazmat.primitives.asymmetric import ed25519

import json
import socket
import uuid
import logging
from typing import Optional

from vault.client import VaultClient
from vault.schemas import ActionProposal, GateDecision, MetricSnapshot, ALLOW, DENY, MODIFY
from heterosis import SubstrateIPCClient

log = logging.getLogger(__name__)

class FPTIPCClientAdapter(VaultClient):
    """
    Subclasses VaultClient to route 79 Hz actions directly through the
    FPT Admission Kernel and modulate Heterosis Substrate drive in real-time.
    """

    def __init__(
        self,
        fpt_socket_path: str = "/data/data/com.termux/files/usr/tmp/fpt_kernel.sock",
        het_socket_path: str = "/data/data/com.termux/files/usr/tmp/heterosis.sock",
        sovereign_id: str = "platform_79hz_agent",
        authority_tag: str = "authority:human_in_the_loop",
        base_drive: float = 0.50,
        timeout: float = 0.05,
        context_window: int = 10,
        fail_open: bool = False,
    ) -> None:
        self.fpt_socket_path = fpt_socket_path
        self.het_socket_path = het_socket_path
        self.sovereign_id = sovereign_id
        self.authority_tag = authority_tag
        self.base_drive = base_drive
        self._timeout = timeout
        self._context_window = context_window
        self._fail_open = fail_open
        self.latest_damping = 0.50
        self.latest_substrate_seq = None

        self.substrate_client = SubstrateIPCClient(self.het_socket_path)
        self._private_key = ed25519.Ed25519PrivateKey.generate()
        self._public_key_hex = self._private_key.public_key().public_bytes_raw().hex()
        self.latest_egress_receipt = "0" * 64
        self.handshake_token = json.dumps({
            "authority_tag": self.authority_tag,
            "sovereign_id": self.sovereign_id,
        })

    def push_metrics(self, snapshots: list[MetricSnapshot]) -> bool:
        if not snapshots:
            return True
        try:
            snap = snapshots[-1]
            pulse_val = snap.metrics.get("tick_latency", 1.0) if hasattr(snap, "metrics") else 1.0
            self.substrate_client.send_intent({
                "intent_id": str(uuid.uuid4()),
                "action": "METRIC_PULSE",
                "params": {"pulse": float(pulse_val), "source": getattr(snap, "source", "platform")},
                "signature": "platform_telemetry"
            })
            return True
        except Exception as e:
            log.warning("push_metrics intent failed: %s", e)
            return True

    def gate_action(
        self,
        action: ActionProposal,
        recent_metrics: list[MetricSnapshot],
    ) -> GateDecision:
        # Map Platform ActionProposal to FPT kernel command format
        cmd = action.params.get("command", f"echo ACTION_{action.action_type}")
        target = action.params.get("target_path", "./workspace")
        tier = action.params.get("risk_tier", 1)

        fpt_payload = {
            "action_id": action.action_id,
            "command": cmd,
            "target_path": target,
            "risk_tier": tier,
            "approval_token": self.handshake_token,
        }

        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.settimeout(self._timeout)
                s.connect(self.fpt_socket_path)
                s.sendall((json.dumps(fpt_payload) + "\n").encode("utf-8"))
                raw = s.recv(4096).decode("utf-8")
                res = json.loads(raw)

            status = res.get("status")
            executed = res.get("executed", False)
            tel = res.get("fpt_telemetry", {})
            self.latest_damping = tel.get("damping", self.latest_damping)

            # Apply inverse damping to Substrate drive throttle
            effective_drive = max(0.01, self.base_drive * (1.0 - self.latest_damping))
            def _dispatch_with_anchor(anchor_val):
                intent_obj = {
                    "intent_id": str(uuid.uuid4()),
                    "action": "DRIVE_STEP",
                    "params": {"external_drive": float(effective_drive)},
                    "manifold_constraints": {
                        "max_acceptable_shear": 12.0,
                        "pressure_ingress": float(min(40.0, max(0.01, effective_drive)))
                    },
                    "fpt_authority": {
                        "public_key_hex": self._public_key_hex,
                        "sovereign_id": self.sovereign_id,
                        "action_id": action.action_id,
                        "lineage_anchor": str(anchor_val)
                    }
                }
                # Ensure canonical serialization without signature key
                unsigned = json.loads(json.dumps(intent_obj))
                unsigned["fpt_authority"].pop("signature", None)
                c_bytes = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode("utf-8")
                intent_obj["fpt_authority"]["signature"] = self._private_key.sign(c_bytes).hex()
                return self.substrate_client.send_intent(intent_obj)

            het_res = _dispatch_with_anchor(self.latest_egress_receipt)
            # Re-lock lineage anchor on mismatch
            if het_res.get("error", {}).get("code") == "LINEAGE_MISMATCH":
                detail = het_res["error"].get("detail", "")
                if "!=" in detail:
                    expected_anchor = detail.split("!=")[-1].strip()
                    self.latest_egress_receipt = expected_anchor
                    het_res = _dispatch_with_anchor(self.latest_egress_receipt)

            if het_res.get("status") == "ACCEPTED":
                lineage_val = het_res.get("lineage")
                if isinstance(lineage_val, dict):
                    self.latest_egress_receipt = lineage_val.get("egress_receipt") or lineage_val.get("anchor") or self.latest_egress_receipt
                elif isinstance(lineage_val, str):
                    self.latest_egress_receipt = lineage_val
                elif "egress_receipt" in het_res:
                    self.latest_egress_receipt = het_res["egress_receipt"]

                self.latest_substrate_seq = (
                    het_res.get("cycle_sequence")
                    or het_res.get("sequence")
                    or het_res.get("seq_num")
                    or het_res.get("seq")
                    or self.latest_substrate_seq
                )

            if status == "ok" and executed:
                return GateDecision(action_id=action.action_id, decision=ALLOW, reason="Passed FPT admission")
            else:
                reason = res.get("error") or res.get("output") or f"Blocked with status {status}"
                return GateDecision(action_id=action.action_id, decision=DENY, reason=reason)

        except Exception as e:
            log.error("FPT Gating error for action %s: %s", action.action_id, e)
            if self._fail_open:
                return GateDecision(action_id=action.action_id, decision=ALLOW, reason="Fail-open dev mode")
            return GateDecision(action_id=action.action_id, decision=DENY, reason=str(e))
