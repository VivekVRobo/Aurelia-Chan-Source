# Aurelia Software Release Readiness

Aurelia is still experimental software. This checklist defines when the current `0.6.0` candidate may be tagged as a **pre-1.0 software release** without implying AGI, production-scale reliability, safety certification, open-source licensing, or physical autonomy.

## Allowed release statement

> **Aurelia 0.6.0 — Experimental cognitive-runtime and character-intelligence software with deterministic fallback evidence, durable persistence, DAG execution, verification contracts, and an actuator-free embodiment boundary.**

The release must remain explicit that model quality, production-scale performance, and physical embodiment are outside the demonstrated scope.

## Required CI gates

- [ ] `package-and-stabilization` is green on the exact tag commit.
- [ ] `legacy-v3` is green on the exact tag commit.
- [ ] `cognitive-v4-v6` is green on the exact tag commit.
- [ ] `frontend-integrity` is green on the exact tag commit.
- [ ] The package compiles under Python 3.12.
- [ ] Stabilized runtime files pass Ruff lint and format checks.

## Deterministic cognitive-cycle evidence

- [ ] `tools/run_cognitive_cycle_evidence.py` completes successfully.
- [ ] At least five fresh runtime instances execute the canonical fixture.
- [ ] Every run uses a fresh durable SQLite database.
- [ ] The normalized engineering trace is identical across repetitions.
- [ ] The report contains the stable response SHA-256, intent, DAG nodes, actual capabilities invoked, verification state, grounding counts, persona state, persistence state, artifact metadata, and embodiment contract.
- [ ] Random UUIDs, timestamps, and temporary paths remain excluded from determinism comparisons.
- [ ] The actuator-free `rci.character_response.v1` embodiment contract remains verified.
- [ ] CI uploads the `aurelia-cognitive-cycle-evidence` artifact.

## Persistence and verification gates

- [ ] One decision receipt is durably persisted per evidence run.
- [ ] Verified-cycle persistence remains atomic.
- [ ] Unverified cognitive cycles cannot be committed as successful verified cycles.
- [ ] Conflicting/rejected memory candidates do not overwrite canonical facts silently.
- [ ] Verification firewall status is visible in the serialized runtime result.
- [ ] Fail-closed bootstrap/API behavior remains covered by stabilization tests.

## Performance claim boundary

- [ ] Any latency samples are labeled `current_process_and_host_only`.
- [ ] `performance_claim` remains false for CI-host timing artifacts.
- [ ] No universal latency, throughput, scalability, or production-SLA claim is made from GitHub Actions timing.
- [ ] Optional Ollama/model latency is not mixed with deterministic-fallback timing unless separately measured and labeled.

## Embodiment claim boundary

- [ ] The character contract contains semantic speech/expression/motion intent only.
- [ ] No servo angle, PWM, trajectory, joint target, or actuator-driver command crosses the Aurelia embodiment boundary.
- [ ] Physical robot evidence is not claimed by this repository.
- [ ] RCI remains the downstream authority for deterministic robot planning/safety when integration is used.

## Packaging, docs, and legal status

- [ ] `pyproject.toml` version is exactly `0.6.0` and matches the intended tag.
- [ ] `README.md` status and validation sections match the tagged tree.
- [ ] `docs/validation/COGNITIVE_CYCLE_EVIDENCE.md` matches the evidence runner.
- [ ] Quick-start commands have been reviewed against the tag.
- [ ] Release notes list known limitations and optional Ollama dependency behavior.
- [ ] Release notes explicitly state the current proprietary license/status; public source visibility is not described as an open-source grant.
- [ ] Character/media assets are not accidentally relicensed by the software tag.

## Recommended first tagged release

Once every gate above passes on the exact release commit, create:

`v0.6.0 — Deterministic Cognitive Runtime Evidence Release`

Do **not** use `v1.0.0` until the project has a deliberately defined stable public API/compatibility commitment and a clear long-term licensing/release policy.

## Recruiter review path

1. `README.md` — architecture and claim boundaries;
2. `aurelia/runtime/cognitive_runtime.py` — full cognitive-cycle orchestration;
3. `aurelia/execution/` + capability catalog — explicit execution architecture;
4. `aurelia/runtime/persistence.py` + `aurelia/persistence/database.py` — durable state boundary;
5. `aurelia/embodiment/` — actuator-free external embodiment contract;
6. `tools/run_cognitive_cycle_evidence.py` + `docs/validation/COGNITIVE_CYCLE_EVIDENCE.md` — deterministic proof;
7. `.github/workflows/aurelia-ci.yml` — four independent validation jobs;
8. this checklist — exact release boundary.
