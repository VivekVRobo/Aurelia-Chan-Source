# Cognitive-Cycle Evidence Protocol

This protocol turns Aurelia's existing deterministic replay checks into a machine-readable end-to-end software artifact.

## What is exercised

Each run creates a fresh durable SQLite database and executes the same fixture through:

```text
SemanticMeaningEngine
  -> CognitiveRouter
  -> CognitivePlanner
  -> capability registry
  -> CognitiveDAGExecutor
  -> RuntimeGrounder
  -> PersonaRenderer
  -> verification firewall
  -> DecisionReceipt
  -> durable persistence
  -> AureliaEmbodimentAdapter
  -> rci.character_response.v1
```

The optional local-model call is deliberately forced onto the deterministic fallback path so repeated runs can be compared without depending on network access or a model service.

## Fixed fixture

The evidence runner defines one fixed software fixture:

- query: `How should I prepare for a Director of Engineering promotion?`
- user role: `Senior Engineering Manager`
- target role: `Director of Engineering`
- model mode: deterministic local fallback

This fixture is intentionally software-only and does not require proprietary credentials or physical hardware.

## Normalized trace

Generated UUIDs, timestamps and database paths are intentionally excluded from equality checks. The normalized trace retains engineering-relevant behavior:

- stable response SHA-256;
- intent type;
- planned DAG node IDs;
- capabilities actually invoked;
- verification result and numerical checks;
- retrieval/grounding counts;
- persona state;
- durable persistence outcome;
- artifact types/titles/versions;
- actuator-free embodiment schema, speech delivery, expression and motion cue.

Five fresh-runtime executions are used in CI by default. The job fails if the normalized traces diverge, durable persistence is not observed on every run, one decision receipt is not stored per run, verification fails, or the embodiment contract is not verified.

## Environment metadata

The generated JSON report also records reproducibility metadata outside the normalized trace:

- Git revision, using `GITHUB_SHA` in CI and the current Git revision locally;
- Python version and implementation;
- operating-system/platform release and machine architecture;
- installed `aurelia-cognitive-os` package version.

Environment metadata is descriptive provenance. It is not treated as part of the deterministic equality comparison, because equivalent software traces may legitimately be executed on different hosts.

## Run locally

```bash
python tools/run_cognitive_cycle_evidence.py \
  --repetitions 5 \
  --output reports/local-cognitive-cycle-evidence.json
```

GitHub Actions uploads the same report as `aurelia-cognitive-cycle-evidence`.

The stabilization suite also checks that the environment metadata contains the required reproducibility fields.

## Latency field

The artifact also records per-run wall-clock duration plus mean/median/min/max. These values are explicitly labeled:

```text
scope: current_process_and_host_only
performance_claim: false
```

They are useful for spotting large regressions on comparable environments, but they are not a production-scale throughput or latency claim.

## Evidence boundary

A green report demonstrates deterministic software behavior for the documented fixture, successful verification, durable SQLite persistence and a verified actuator-free embodiment contract.

It does **not** demonstrate AGI, general model quality, large-scale production reliability, physical robot safety, or physical embodiment performance.
