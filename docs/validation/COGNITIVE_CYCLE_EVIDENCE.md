# Cognitive-Cycle Evidence Protocol

This protocol turns Aurelia's deterministic replay checks into a machine-readable end-to-end software artifact, including the canonical HTTP response contract.

## What is exercised

Every repetition creates a fresh durable SQLite database and sends the same fixed request through the canonical Flask handler:

\`\`\`text
POST /api/cognitive-cycle
  -> SemanticMeaningEngine
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
  -> serialize_cognitive_cycle JSON response
\`\`\`

The optional local-model call is forced onto the deterministic fallback path. The evidence runner uses Flask's test client, checks the HTTP status, and records one actual serialized API response sample. The same run's runtime receipt is used to record planner output, DAG order, selected hypothesis, invoked capabilities, and critic scores.

## Normalized trace

The normalized trace retains engineering-relevant behavior:

- stable response SHA-256 and intent;
- planned DAG node IDs, capabilities invoked, hypotheses considered, and selected hypothesis;
- verification result, publication decision, numerical checks, and verification issues;
- retrieval/grounding counts and unresolved unknowns;
- persona state and the actuator-free embodiment response;
- durable persistence outcome and per-run write counts;
- artifact types, titles, versions, and normalized payloads;
- the structured API response contract, including its field set and response hash.

The raw representative API response is also included as \`api_response_sample\` for inspection. Generated identifiers are retained in that sample but excluded from normalized comparisons.

## Runtime metadata and normalization

The artifact records package/Python versions, Python implementation, operating system and release, machine architecture, SQLite version, deterministic-model mode, and disposable-database strategy.

Generated decision/snapshot/artifact IDs, candidate IDs, timestamps, database paths, and runtime measurements are not used for equality checks. Persistence identifiers are represented by counts and rejection reasons. Host metadata and latency measurements remain outside the normalized trace so comparable behavior can be checked across runs without pretending that different hosts are identical.

## Run locally

\`\`\`bash
python tools/run_cognitive_cycle_evidence.py \\
  --repetitions 5 \\
  --output reports/local-cognitive-cycle-evidence.json
pytest -q tests/stabilization/test_cognitive_cycle_evidence.py
\`\`\`

GitHub Actions uploads the generated report as \`aurelia-cognitive-cycle-evidence\`. The evidence job fails when normalized traces diverge, the API does not return HTTP 200, the serialized response keys drift from the explicit contract, persistence is not durable, the receipt count is wrong, verification fails, or the embodiment contract is not verified.

The regression test locks the report schema, normalized trace schema, and expected top-level API response keys. An intentional API or evidence-contract change must update the contract and its test together.

## Latency field

The artifact records per-run wall-clock duration plus mean/median/min/max. These values are explicitly labeled:

\`\`\`text
scope: current_process_and_host_only
performance_claim: false
\`\`\`

They are useful for spotting large regressions on comparable environments, but they are not production-scale throughput or latency claims.

## Evidence boundary

A green report demonstrates repeatable software behavior for the documented fixture, successful API serialization, verification, durable SQLite persistence, and the tested actuator-free embodiment contract.

It does **not** demonstrate AGI, general model quality, large-scale production reliability, physical robot safety, or physical embodiment performance.
