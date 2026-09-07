from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

from aurelia.embodiment.adapter import AureliaEmbodimentAdapter
from aurelia.llm.ollama_cortex import LocalOllamaCortex
from aurelia.runtime.cognitive_runtime import AureliaCognitiveRuntime, CognitiveCycleResponse

FIXTURE_QUERY = "How should I prepare for a Director of Engineering promotion?"
FIXTURE_USER_ROLE = "Senior Engineering Manager"
FIXTURE_TARGET_ROLE = "Director of Engineering"


def _normalize(result: CognitiveCycleResponse) -> dict[str, object]:
    receipt = result.decision_receipt
    embodiment = AureliaEmbodimentAdapter.adapt(result)
    diagnostics = result.persistence
    return {
        "response_sha256": receipt.deterministic_replay_hash,
        "intent_type": receipt.intent_type,
        "plan_dag_nodes": list(receipt.plan_dag_nodes),
        "capabilities_invoked": list(receipt.capabilities_invoked),
        "verification": {
            "passed": receipt.verification_passed,
            "severity": receipt.verification_severity,
            "safe_to_publish": result.verification_report.is_safe_to_publish,
            "numerical_checks": list(receipt.numerical_calculations_verified),
        },
        "trace": {
            "memories_retrieved_count": result.trace.memories_retrieved_count,
            "graph_facts_count": result.trace.graph_facts_count,
            "specialists_invoked": list(result.trace.specialists_invoked),
            "alternatives_evaluated": list(result.trace.alternatives_evaluated),
            "unresolved_unknowns": list(result.trace.unresolved_unknowns),
            "confidence_level": result.trace.confidence_level,
        },
        "persona": {
            "emotion": result.persona.emotion.value,
            "emotion_intensity": result.persona.emotion_intensity.value,
            "expression_style": result.persona.expression_style.value,
            "mode": result.persona.mode,
            "expression": result.persona.expression,
        },
        "persistence": {
            "committed": diagnostics.committed,
            "durable": diagnostics.durable,
        },
        "artifacts": [
            {
                "type": artifact.artifact_type.value,
                "title": artifact.title,
                "version": artifact.version,
            }
            for artifact in result.artifacts
        ],
        "embodiment": {
            "schema_version": embodiment.schema_version,
            "source_character": embodiment.source_character,
            "verified": embodiment.verified,
            "persistence_committed": embodiment.persistence_committed,
            "persistence_durable": embodiment.persistence_durable,
            "speech_delivery": embodiment.speech.delivery.value,
            "expression": embodiment.expression.expression,
            "expression_strength": embodiment.expression.strength.value,
            "motion_cue": embodiment.motion.cue.value,
            "motion_style": embodiment.motion.style.value,
            "motion_disposition": embodiment.motion.disposition.value,
        },
    }


def _run_once(db_path: Path) -> tuple[dict[str, object], float, dict[str, object]]:
    runtime = AureliaCognitiveRuntime(db_path=str(db_path))
    started = time.perf_counter()
    try:
        with patch.object(LocalOllamaCortex, "query_local_model", return_value=None):
            result = runtime.process_query(
                FIXTURE_QUERY,
                user_role=FIXTURE_USER_ROLE,
                target_role=FIXTURE_TARGET_ROLE,
            )
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        persistence = runtime.persistence.diagnostics()
        return _normalize(result), elapsed_ms, {
            "durable": bool(persistence["durable"]),
            "decision_receipts": int(persistence["decision_receipts"]),
            "executive_artifacts": int(persistence["executive_artifacts"]),
            "canonical_facts": int(persistence["canonical_facts"]),
            "canonical_inferences": int(persistence["canonical_inferences"]),
        }
    finally:
        runtime.database.close()


def run_campaign(repetitions: int) -> dict[str, object]:
    if repetitions < 2:
        raise ValueError("repetitions must be at least 2")

    normalized_runs: list[dict[str, object]] = []
    elapsed_ms: list[float] = []
    persistence_runs: list[dict[str, object]] = []

    with tempfile.TemporaryDirectory(prefix="aurelia-evidence-") as tmp:
        root = Path(tmp)
        for index in range(repetitions):
            normalized, elapsed, persistence = _run_once(root / f"run-{index}.db")
            normalized_runs.append(normalized)
            elapsed_ms.append(elapsed)
            persistence_runs.append(persistence)

    representative = normalized_runs[0]
    deterministic = all(run == representative for run in normalized_runs[1:])
    durable_each_run = all(bool(run["durable"]) for run in persistence_runs)
    one_receipt_each_run = all(int(run["decision_receipts"]) == 1 for run in persistence_runs)
    verified = bool(representative["verification"]["passed"])  # type: ignore[index]
    embodiment_verified = bool(representative["embodiment"]["verified"])  # type: ignore[index]

    canonical = json.dumps(representative, sort_keys=True, separators=(",", ":")).encode()
    stable_sha256 = hashlib.sha256(canonical).hexdigest()

    result: dict[str, object] = {
        "schema_version": "aurelia.cognitive_cycle_evidence.v1",
        "evidence_type": "deterministic_software_cognitive_cycle",
        "fixture": {
            "query": FIXTURE_QUERY,
            "user_role": FIXTURE_USER_ROLE,
            "target_role": FIXTURE_TARGET_ROLE,
            "local_model_mode": "forced_deterministic_fallback",
        },
        "run_count": repetitions,
        "deterministic_normalized_trace": deterministic,
        "durable_persistence_each_run": durable_each_run,
        "one_decision_receipt_each_run": one_receipt_each_run,
        "verification_passed": verified,
        "embodiment_contract_verified": embodiment_verified,
        "all_checks_passed": (
            deterministic
            and durable_each_run
            and one_receipt_each_run
            and verified
            and embodiment_verified
        ),
        "normalized_trace_sha256": stable_sha256,
        "representative_trace": representative,
        "persistence_runs": persistence_runs,
        "latency_baseline": {
            "scope": "current_process_and_host_only",
            "performance_claim": False,
            "samples_ms": [round(value, 3) for value in elapsed_ms],
            "mean_ms": round(statistics.fmean(elapsed_ms), 3),
            "median_ms": round(statistics.median(elapsed_ms), 3),
            "min_ms": round(min(elapsed_ms), 3),
            "max_ms": round(max(elapsed_ms), 3),
        },
        "claim_boundary": {
            "production_scale_validated": False,
            "model_quality_benchmark": False,
            "physical_embodiment_evidence": False,
        },
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate deterministic Aurelia cognitive-cycle evidence"
    )
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = run_campaign(args.repetitions)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
        print(args.output)

    if not result["all_checks_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
