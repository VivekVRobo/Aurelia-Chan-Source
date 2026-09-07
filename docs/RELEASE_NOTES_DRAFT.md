# Draft Release Notes — v0.6.0

## v0.6.0 — Deterministic Cognitive Runtime Evidence Release

Aurelia 0.6.0 is a pre-1.0 experimental cognitive-runtime and character-intelligence software release focused on inspectable execution, durable state, verification contracts and reproducible evidence rather than broad intelligence claims.

### What this release demonstrates

- modular Python 3.12 cognitive runtime;
- canonical Flask application bootstrap;
- planner, capability registry and DAG execution;
- durable SQLite-backed persistence;
- grounding and verification contracts;
- persona rendering separated from execution logic;
- actuator-free `rci.character_response.v1` embodiment boundary;
- fail-closed runtime/API behavior;
- versioned V3–V6 regression suites and frontend integrity checks;
- deterministic end-to-end cognitive-cycle evidence across five fresh runtime instances and fresh SQLite databases;
- stable normalized trace containing response hash, intent, DAG nodes, actual capabilities, verification, grounding counts, persona state, persistence and embodiment metadata;
- CI-host timing retained only as regression context with `performance_claim: false`.

### Evidence boundary

This release does **not** claim AGI, human-level general intelligence, safety certification, production-scale reliability, universal latency/throughput, or validated physical autonomy.

The deterministic evidence fixture intentionally uses Aurelia's deterministic fallback path so repeatability is not dependent on network/model-service availability. Optional Ollama/model quality and latency are separate concerns.

### Embodiment boundary

Aurelia emits semantic character-response/embodiment intent only. Servo angles, PWM, trajectories, joint targets and actuator-driver authority do not cross this repository's embodiment boundary. When connected to robotics, RCI remains the downstream deterministic planning/safety authority.

### Legal/status boundary

This repository is publicly viewable but currently proprietary. Public source visibility is not an open-source license grant. Character/media assets remain subject to their applicable intellectual-property restrictions.

### Before tagging

- change the package version from `0.6.0.dev0` to the intended release version;
- run all four CI jobs on the exact tag commit;
- verify the five-run cognitive-cycle evidence artifact;
- review quick-start and status text;
- confirm no production, AGI, safety-certification or physical-autonomy claims have been introduced.

Use `docs/RELEASE_READINESS.md` as the authoritative release checklist.
