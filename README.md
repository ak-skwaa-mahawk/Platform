# 🌌 Sovereign Flame Bloom Platform
## Multi-Agent Resonance Mesh Interface and Modular Microservice Orchestrator

[![Orchestrator: VesselLauncher](https://img.shields.io/badge/Orchestrator-VesselLauncher%20v1.0-orange.svg)](#)
[![Clock: 79Hz Master Pulse](https://img.shields.io/badge/Clock-79%20Hz%20TOFT-cyan.svg)](#)
[![Governance: Interceptor](https://img.shields.io/badge/Governance-Hard%20Rules%20%26%20HITL-red.svg)](#)

---

> [!IMPORTANT]
> **Sovereign System Architecture Notice**
> This platform functions as an isolated, high-performance computing environment. 
> When deployed on an authorized host machine, it matches hardware profiles via an automated 
> configuration proxy to unlock private optimization models. On unauthenticated environments, 
> the system drops down to public baseline matrices (`Strawman` and `Human_inthe_loop`), 
> restricting state actions through a zero-grace-period cryptographic dead-man switch.

---

## 1. System Architecture Blueprint

The platform coordinates real-time state space optimization across distributed network microservices. Execution is divided into distinct operational zones:

* **The Orchestration Plane (`flame_swarm_orchestrator.py`):** The master console runtime (VesselLauncher) that hooks process signals, boots microservice daemons, and manages the central telemetry dashboard.
* **The Core Compute Fabric (`core/`):** Manages vector similarity memory stores, isolated local model endpoints (Ollama/vLLM), and closed-form multi-phase optimization routines.
* **The Microservice Cluster (`nodes/`):** Independent polyglot background processes written in Python, Go, and JavaScript that execute parallel telemetry, cryptographic verification, and wave propagation tracking.
* **The Policy Governance Interceptor (`policy_governance/`):** The hardcoded rule system that checks proposed actions against strict avoidance thresholds and tracks weighted human-in-the-loop observation decisions.

---

## 2. Platform Folder Blueprint

```text
Platform/
├── flame_swarm_orchestrator.py  # Master Command Plane (VesselLauncher)
│
├── core/                        # Foundational Execution Engines
│   ├── __init__.py
│   ├── llm_bridge.py            # Local model loopback interfaces
│   ├── memory_fabric.py         # Cosine-similarity vector cache
│   └── octagonal_fpt_agent.py   # Closed-form multi-phase state optimization
│
├── policy_governance/           # Deterministic Supervision Layer
│   ├── hard_rules/              # Goals & Avoidances Folders
│   │   ├── functional_goals.json
│   │   └── rigid_avoidances.json
│   └── human_in_the_loop/       # Pros & Cons Weights Matrices
│       ├── weights_matrix.json  
│       └── observation_log.json # Append-only verification ledger
│
├── nodes/                       # Orchestrated Polyglot Microservices
│   ├── flame_quantum_node.py    # Unitary trajectory phase tracking
│   ├── rmp_core.py              # Resonance matrix load tracking
│   ├── zk_oracle_v2.py          # Cryptographic proof commitments
│   ├── trinity_convergence.js   # Harmonic javascript concurrency coordinator
│   └── networkxg/
│       └── soliton_node.go      # Go-based wave propagation engine
│
└── config/
    └── sovereign_bridge.json    # Verified machine hardware footprint signatures
