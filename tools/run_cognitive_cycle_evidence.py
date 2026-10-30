from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sqlite3
import statistics
import sys
import tempfile
import time
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from unittest.mock import patch

from aurelia.contracts.receipt import DecisionReceipt
from aurelia.llm.ollama_cortex import LocalOllamaCortex
from aurelia.runtime.app_bootstrap import _install_hardened_cognitive_cycle
from aurelia.runtime.cognitive_runtime import AureliaCognitiveRuntime

FIXTURE_QUERY = "How should I prepare for a Director of Engineering promotion?"
FIXTURE_USER_ROLE = "Senior Engineering Manager"
FIXTURE_TARGET_ROLE = "Director of Engineering"
EXPECTED_API_RESPONSE_KEYS = frozenset(
    {
        "response",
        "expression",
        "portrait",
        "confidence",
        "persona",
        "character_response",
        "trace",
        "verification",
        "persistence",
        "artifacts",
        "decision_id",
    }
)
VOLATILE_API_KEYS = frozenset(
    {
        "decision_id",
        "snapshot_id",
        "created_at",
        "updated_at",
        "timestamp",
        "artifact_id",
        "candidate_id",
        "request_id",
        "run_id",
        "database_path",
        "db_path",
    }
)


def _runtime_metadata() -> dict[str, str]:
    """Describe the environment without mixing host-specific values into trace equality."""
    try:
        package_version = version("aurelia-cognitive-os")
    except PackageNotFoundError:
        package_version = "unknown"

    return {
        "package_name": "aurelia-cognitive-os",
        "package_version": package_version,
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "os": platform.system(),
        "os_release": platform.release(),
        "machine": platform.machine(),
        "sqlite_version": sqlite3.sqlite_version,
        "local_model_mode": "forced_deterministic_fallback",
        "database_strategy": "fresh_temporary_sqlite_per_repetition",
    }


def _strip_volatile_fields(value: object) -> object:
    """Remove generated identifiers and timestamps before cross-run comparison."""
    if isinstance(value, dict):
        return {
            str(key): _strip_volatile_fields(item)
            for key, item in value.items()
            if key not in VOLATILE_API_KEYS
        }
    if isinstance(value, list):
        return [_strip_volatile_fields(item) for item in value]
    return value


def _normalize_api_response(api_response: dict[str, object]) -> dict[str, object]:
    """Keep the serialized HTTP contract while excluding per-run identity fields."""
    normalized = _strip_volatile_fields(api_response)
    if not isinstance(normalized, dict):
        raise TypeError("API response normalization did not produce an object")

    normalized.pop("decision_id", None)
    artifacts = normalized.get("artifacts", [])
    if isinstance(artifacts, list):
        for artifact in artifacts:
            if isinstance(artifact, dict):
                artifact.pop("id", None)

    persistence = normalized.get("persistence")
    if isinstance(persistence, dict):
        approved_ids = persistence.pop("approved_memory_ids", [])
        persistence["approved_memory_count"] = (
            len(approved_ids) if isinstance(approved_ids, list) else 0
        )
        rejected_memory = persistence.get("rejected_memory", [])
        if isinstance(rejected_memory, list):
            persistence["rejected_memory"] = [
                {"reason": entry.get("reason")}
                for entry in rejected_memory
                if isinstance(entry, dict)
            ]

    normalized["top_level_keys"] = sorted(api_response)
    normalized["response_sha256"] = hashlib.sha256(
        str(api_response.get("response", "")).encode("utf-8")
    ).hexdigest()
    normalized["contract_keys_match"] = set(api_response) == EXPECTED_API_RESPONSE_KEYS
    return normalized


def _normalize(
    api_response: dict[str, object],
    receipt: DecisionReceipt,
) -> dict[str, object]:
    """Project planner, verification, persistence and the actual API response."""
    normalized_api = _normalize_api_response(api_response)
    trace = api_response.get("trace", {})
    verification = api_response.get("verification", {})
    if not isinstance(trace, dict) or not isinstance(verification, dict):
        raise TypeError("API response is missing its trace or verification object")

    planner = {
        "intent_type": receipt.intent_type,
        "plan_dag_nodes": list(receipt.plan_dag_nodes),
        "capabilities_invoked": list(receipt.capabilities_invoked),
        "hypotheses_considered": list(receipt.hypotheses_considered),
        "selected_hypothesis_id": receipt.selected_hypothesis_id,
        "critic_scores": dict(sorted(receipt.critic_scores.items())),
    }
    persistence = normalized_api.get("persistence", {})
    if not isinstance(persistence, dict):
        raise TypeError("API response persistence contract must be an object")

    artifacts = api_response.get("artifacts", [])
    if not isinstance(artifacts, list):
        raise TypeError("API response artifacts contract must be a list")

    return {
        "response_sha256": receipt.deterministic_replay_hash,
        "intent_type": receipt.intent_type,
        "plan_dag_nodes": list(receipt.plan_dag_nodes),
        "capabilities_invoked": list(receipt.capabilities_invoked),
        "planner": planner,
        "verification": {
            "passed": receipt.verification_passed,
            "severity": receipt.verification_severity,
            "safe_to_publish": bool(verification.get("safe_to_publish")),
            "numerical_checks": list(receipt.numerical_calculations_verified),
            "issues": _strip_volatile_fields(verification.get("issues", [])),
        },
        "trace": {
            "memories_retrieved_count": int(trace.get("memories_count", 0)),
            "graph_facts_count": int(trace.get("graph_facts_count", 0)),
            "specialists_invoked": list(trace.get("specialists_invoked", [])),
            "alternatives_evaluated": list(trace.get("alternatives_evaluated", [])),
            "unresolved_unknowns": list(trace.get("unresolved_unknowns", [])),
            "confidence_level": trace.get("confidence_level"),
        },
        "persona": normalized_api.get("persona", {}),
        "persistence": persistence,
        "artifacts": [
            {
                "type": artifact.get("type"),
                "title": artifact.get("title"),
                "version": artifact.get("version"),
            }
            for artifact in artifacts
            if isinstance(artifact, dict)
        ],
        "embodiment": normalized_api.get("character_response", {}),
        "api_response": normalized_api,
        "api_response_contract_valid": bool(normalized_api["contract_keys_match"]),
    }


def _run_once(
    db_path: Path,
) -> tuple[dict[str, object], float, dict[str, object], dict[str, object], int]:
    repository_root = str(Path(__file__).resolve().parents[1])
    if repository_root not in sys.path:
        sys.path.insert(0, repository_root)
    import integrated_backend as backend

    runtime = AureliaCognitiveRuntime(db_path=str(db_path))
    previous_runtime = getattr(backend, "v4_runtime", None)
    previous_view = backend.app.view_functions.get("cognitive_cycle")
    backend.v4_runtime = runtime
    started = time.perf_counter()

    try:
        _install_hardened_cognitive_cycle(backend)
        with patch.object(LocalOllamaCortex, "query_local_model", return_value=None):
            response = backend.app.test_client().post(
                "/api/cognitive-cycle",
                json={
                    "message": FIXTURE_QUERY,
                    "user_role": FIXTURE_USER_ROLE,
                    "target_role": FIXTURE_TARGET_ROLE,
                },
            )
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        if response.status_code != 200:
            raise RuntimeError(
                "Cognitive-cycle API returned "
                f"HTTP {response.status_code}: {response.get_data(as_text=True)[:500]}"
            )

        api_response = response.get_json()
        if not isinstance(api_response, dict):
            raise RuntimeError("Cognitive-cycle API did not return a JSON object")
        decision_id = api_response.get("decision_id")
        receipt = runtime.receipts.get(decision_id)
        if receipt is None:
            raise RuntimeError("API response decision_id has no matching runtime receipt")

        diagnostics = runtime.persistence.diagnostics()
        return (
            _normalize(api_response, receipt),
            elapsed_ms,
            {
                "durable": bool(diagnostics["durable"]),
                "decision_receipts": int(diagnostics["decision_receipts"]),
                "executive_artifacts": int(diagnostics["executive_artifacts"]),
                "canonical_facts": int(diagnostics["canonical_facts"]),
                "canonical_inferences": int(diagnostics["canonical_inferences"]),
            },
            api_response,
            int(response.status_code),
        )
    finally:
        if previous_view is None:
            backend.app.view_functions.pop("cognitive_cycle", None)
        else:
            backend.app.view_functions["cognitive_cycle"] = previous_view
        backend.v4_runtime = previous_runtime
        runtime.database.close()


def run_campaign(repetitions: int) -> dict[str, object]:
    if repetitions < 2:
        raise ValueError("repetitions must be at least 2")

    normalized_runs: list[dict[str, object]] = []
    elapsed_ms: list[float] = []
    persistence_runs: list[dict[str, object]] = []
    api_response_samples: list[dict[str, object]] = []
    http_status_codes: list[int] = []

    with tempfile.TemporaryDirectory(prefix="aurelia-evidence-") as tmp:
        root = Path(tmp)
        for index in range(repetitions):
            normalized, elapsed, persistence, api_response, status_code = _run_once(
                root / f"run-{index}.db"
            )
            normalized_runs.append(normalized)
            elapsed_ms.append(elapsed)
            persistence_runs.append(persistence)
            api_response_samples.append(api_response)
            http_status_codes.append(status_code)

    representative = normalized_runs[0]
    deterministic = all(run == representative for run in normalized_runs[1:])
    durable_each_run = all(bool(run["durable"]) for run in persistence_runs)
    one_receipt_each_run = all(int(run["decision_receipts"]) == 1 for run in persistence_runs)
    verified = bool(representative["verification"]["passed"])  # type: ignore[index]
    embodiment_verified = bool(representative["embodiment"]["verified"])  # type: ignore[index]
    api_response_contract_each_run = all(
        bool(run["api_response_contract_valid"]) for run in normalized_runs
    )
    api_http_success_each_run = all(status_code == 200 for status_code in http_status_codes)

    canonical = json.dumps(representative, sort_keys=True, separators=(",", ":")).encode()
    stable_sha256 = hashlib.sha256(canonical).hexdigest()
    normalized_api_response = representative["api_response"]
    api_canonical = json.dumps(
        normalized_api_response, sort_keys=True, separators=(",", ":")
    ).encode()
    normalized_api_sha256 = hashlib.sha256(api_canonical).hexdigest()

    result: dict[str, object] = {
        "schema_version": "aurelia.cognitive_cycle_evidence.v1",
        "evidence_type": "deterministic_software_cognitive_cycle",
        "fixture": {
            "query": FIXTURE_QUERY,
            "user_role": FIXTURE_USER_ROLE,
            "target_role": FIXTURE_TARGET_ROLE,
            "endpoint": "POST /api/cognitive-cycle",
            "local_model_mode": "forced_deterministic_fallback",
            "database_strategy": "fresh_temporary_sqlite_per_repetition",
        },
        "runtime_environment": _runtime_metadata(),
        "run_count": repetitions,
        "api_http_status_codes": http_status_codes,
        "api_http_success_each_run": api_http_success_each_run,
        "api_response_contract_each_run": api_response_contract_each_run,
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
            and api_response_contract_each_run
            and api_http_success_each_run
        ),
        "normalized_trace_sha256": stable_sha256,
        "normalized_api_response_sha256": normalized_api_sha256,
        "representative_trace": representative,
        "api_response_sample": api_response_samples[0],
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
