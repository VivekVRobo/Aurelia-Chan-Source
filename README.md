# Aurelia — Cognitive Runtime & Character Intelligence System

[![Aurelia Software Validation](https://github.com/VivekVRobo/Aurelia-Chan-Source/actions/workflows/aurelia-ci.yml/badge.svg)](https://github.com/VivekVRobo/Aurelia-Chan-Source/actions/workflows/aurelia-ci.yml)

**Aurelia** is an experimental character-intelligence and cognitive-runtime project built around a modular Python 3.12 package, a durable Flask application runtime, explicit planning and execution contracts, persistence, persona rendering, embodiment boundaries, and a browser character interface.

The repository began as an interactive character and career-mentor experience. It has since grown into a broader engineering project: the current `main` branch contains a packaged cognitive runtime (`aurelia-cognitive-os`), stabilization suites, DAG execution, persistence, runtime health/grounding contracts, frontend integrity checks, and an explicit software-to-embodiment boundary.

> **Engineering status:** active experimental software. The repository demonstrates architecture, software contracts, tests, and integration work. It is **not** a claim of AGI, production safety certification, or validated physical autonomy.

## Project snapshot

| Area | Current state |
| --- | --- |
| Python package | `aurelia-cognitive-os` `0.6.0.dev0` |
| Runtime | Flask-backed canonical application bootstrap |
| Planning/execution | Planner + capability registry + DAG execution |
| State | Durable SQLite-backed runtime persistence |
| Character layer | Persona renderer + expression/voice assets |
| Embodiment | Explicit software contract and tested boundary |
| Frontend | Browser character stage with source/contract integrity tests |
| Local model path | Optional Ollama integration |
| Validation | Stabilization, V3–V6, frontend integrity, lint/format CI |
| Physical robot evidence | Not claimed by this repository |

## Why this project exists

A character interface becomes much more interesting when its behavior is not a single monolithic script. Aurelia explores how to separate the pieces that make an interactive agent understandable and testable:

- **cognition** — planning and reasoning-oriented orchestration;
- **execution** — capability dispatch and DAG execution;
- **grounding and verification** — contracts around what can safely be surfaced;
- **persistence** — durable state instead of process-only memory;
- **persona** — character presentation kept separate from execution logic;
- **embodiment** — an explicit boundary between software intent and external actuation;
- **interface integrity** — tests that protect the browser stage from drifting away from backend contracts.

The goal is not to hide complexity behind an “AI assistant” label. The goal is to make the runtime inspectable, testable, and progressively evidence-backed.

## Runtime architecture

```text
Browser / API client
        |
        v
Canonical Flask application
        |
        v
AureliaCognitiveRuntime
   |        |         |
   |        |         +--> Persona / character rendering
   |        +------------> Durable persistence
   +---------------------> Planner + capability registry
                              |
                              v
                         DAG execution
                              |
                              v
                   Grounding / verification contracts
                              |
                              v
                     Structured API response

External or physical embodiment
        ^
        |
Explicit embodiment contract
(no physical validation is implied)
```

### Core implementation areas

- [`aurelia/runtime/`](aurelia/runtime/) — canonical runtime, API contracts, health, grounding, persistence and capability wiring.
- [`aurelia/cognition/`](aurelia/cognition/) — planning-oriented cognition components.
- [`aurelia/execution/`](aurelia/execution/) — execution and DAG machinery.
- [`aurelia/persistence/`](aurelia/persistence/) — durable database layer.
- [`aurelia/character/`](aurelia/character/) — persona and presentation behavior.
- [`aurelia/embodiment/`](aurelia/embodiment/) — typed software boundary for embodiment-facing behavior.
- [`docs/architecture/embodiment-contract.md`](docs/architecture/embodiment-contract.md) — architecture-level embodiment contract.
- [`frontend/`](frontend/) — browser-side cognitive contract and integrity layer.
- [`tests/`](tests/) — stabilization and versioned regression suites.

The canonical server bootstrap is [`aurelia/runtime/app_bootstrap.py`](aurelia/runtime/app_bootstrap.py). It creates the durable cognitive runtime, installs hardened HTTP handlers, exposes runtime readiness information, and fails closed when the cognitive runtime is unavailable.

## Quick start

### Requirements

- Python **3.12+**
- `pip`
- Node.js 22+ only if you want to run the frontend integrity suite locally
- Ollama only for the optional local-model path

### Install the software package

```bash
git clone https://github.com/VivekVRobo/Aurelia-Chan-Source.git
cd Aurelia-Chan-Source
python -m venv .venv
```

Activate the environment, then install the package and development dependencies:

```bash
python -m pip install --upgrade pip
pip install -e '.[dev]'
```

On Windows PowerShell, virtual-environment activation is typically:

```powershell
.\.venv\Scripts\Activate.ps1
```

On Linux/macOS:

```bash
source .venv/bin/activate
```

### Start the canonical runtime

```bash
aurelia-server
```

Defaults:

- host: `127.0.0.1`
- port: `5000`
- SQLite state: `data/aurelia.db`

Optional environment overrides:

```text
AURELIA_HOST
AURELIA_PORT
AURELIA_DB_PATH
```

The runtime status endpoint is available at:

```text
GET /api/runtime-status
```

## Validation

The repository treats tests as part of the architecture rather than an afterthought.

### Stabilized runtime

```bash
pytest -q tests/stabilization
```

This suite covers areas such as runtime stabilization, DAG execution, persona behavior, persistence, and the embodiment contract.

### Versioned regression suites

```bash
pytest -q tests/v3
pytest -q tests/v4 tests/v5 tests/v6
```

### Frontend integrity

```bash
npm run test:frontend
```

### CI gates

GitHub Actions currently separates validation into four jobs:

1. **package-and-stabilization** — package install, compile, Ruff checks, formatting and stabilization regressions;
2. **legacy-v3** — V3 regression suite;
3. **cognitive-v4-v6** — V4/V5/V6 cognitive suites;
4. **frontend-integrity** — JavaScript contract and source-integrity tests.

This separation makes regressions easier to localize and prevents a green UI check from being mistaken for a green cognitive runtime.

## Local model integration

Aurelia includes an optional local-model path built around Ollama. It is not required for installing or inspecting the software architecture.

See [`OLLAMA_SETUP.md`](OLLAMA_SETUP.md) for the current local setup path.

## Character and media layer

The cognitive runtime is only one part of Aurelia. The repository also retains the character-production work that the project started with:

- immutable character canon and master reference sheets;
- expression portraits;
- browser character stage;
- voice-generation tooling;
- 3D reference/generation/validation pipeline;
- WebGL-oriented model-viewer assets.

These assets are presentation and production layers around the runtime; they should not be interpreted as evidence of autonomous physical embodiment.

## Evidence and maturity boundaries

### Demonstrated in the repository

- modular Python package structure;
- durable application bootstrap and SQLite-backed state;
- capability registration and DAG-oriented execution;
- fail-closed runtime/API behavior;
- persona/runtime separation;
- embodiment software contract;
- versioned automated regression suites;
- frontend source/contract integrity checks.

### Not demonstrated by this repository alone

- AGI or human-level general intelligence;
- safety certification;
- production reliability under large-scale load;
- real-world robotic actuation;
- physical perception, manipulation, or navigation evidence;
- guaranteed correctness of model-generated content.

Those boundaries are intentional. Future claims should be added only when matching evidence exists.

## Repository structure

```text
Aurelia-Chan-Source/
├── aurelia/                 # packaged cognitive/character runtime
│   ├── cognition/           # planning and cognition
│   ├── execution/           # capability and DAG execution
│   ├── runtime/             # canonical runtime/API/bootstrap
│   ├── persistence/         # durable state
│   ├── character/           # persona rendering
│   └── embodiment/          # embodiment-facing contracts
├── tests/
│   ├── stabilization/       # stabilization regressions
│   ├── v3/                  # legacy/versioned validation
│   ├── v4/
│   ├── v5/
│   └── v6/
├── frontend/                # browser contract/integrity layer
├── docs/architecture/       # architecture contracts
├── aurelia-canon/           # character canon + reference sheets
├── aurelia-expressions/     # expression assets
├── pipeline/                # character/3D production tooling
├── integrated_backend.py    # integrated Flask application layer
├── pyproject.toml           # package metadata and dev tooling
└── .github/workflows/       # automated validation
```

## Engineering roadmap

The next high-value milestones are evidence-oriented rather than feature-count oriented:

- [ ] publish a deterministic end-to-end cognitive-cycle fixture with a machine-readable result artifact;
- [ ] add runtime latency and persistence-performance baselines;
- [ ] document the capability registry and DAG schema with one reproducible trace;
- [ ] add API contract examples for success and fail-closed behavior;
- [ ] define a release-readiness checklist for the first tagged software release;
- [ ] keep any future embodiment claims gated behind real integration evidence.

## Contributing

Before changing runtime behavior:

1. preserve the separation between cognition, execution, persona, persistence, and embodiment;
2. add or update the narrowest relevant regression test;
3. keep failure behavior explicit rather than returning success-looking fallbacks;
4. run the relevant Python and/or frontend suites;
5. do not add physical or production-readiness claims without matching evidence.

## License and use

This repository is publicly viewable for project development, demonstration, and review, but the project is currently **proprietary**. No open-source license grant is implied by public source visibility. Character assets, specifications, and generated content remain subject to their applicable copyright and intellectual-property restrictions.

## Author

**Vivek Vala** — Robotics & Automation student building projects across autonomous systems, robotics software, computer vision, embedded systems, and agent architectures.
