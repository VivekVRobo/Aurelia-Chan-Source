"""Regression tests for the machine-readable cognitive-cycle evidence contract."""

import hashlib
import json

from tools.run_cognitive_cycle_evidence import EXPECTED_API_RESPONSE_KEYS, run_campaign


EXPECTED_REPORT_KEYS = {
    "schema_version",
    "evidence_type",
    "fixture",
    "runtime_environment",
    "run_count",
    "api_http_status_codes",
    "api_http_success_each_run",
    "api_response_contract_each_run",
    "deterministic_normalized_trace",
    "durable_persistence_each_run",
    "one_decision_receipt_each_run",
    "verification_passed",
    "embodiment_contract_verified",
    "all_checks_passed",
    "normalized_trace_sha256",
    "normalized_api_response_sha256",
    "representative_trace",
    "api_response_sample",
    "persistence_runs",
    "latency_baseline",
    "claim_boundary",
}

EXPECTED_TRACE_KEYS = {
    "response_sha256",
    "intent_type",
    "plan_dag_nodes",
    "capabilities_invoked",
    "planner",
    "verification",
    "trace",
    "persona",
    "persistence",
    "artifacts",
    "embodiment",
    "api_response",
    "api_response_contract_valid",
}

EXPECTED_API_RESPONSE_KEYS_NORMALIZED = {
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
    "top_level_keys",
    "response_sha256",
    "contract_keys_match",
}


def test_cognitive_cycle_evidence_contract_and_api_response_are_stable():
    report = run_campaign(2)

    assert set(report) == EXPECTED_REPORT_KEYS
    assert report["schema_version"] == "aurelia.cognitive_cycle_evidence.v1"
    assert report["api_http_status_codes"] == [200, 200]
    assert report["api_http_success_each_run"] is True
    assert report["api_response_contract_each_run"] is True
    assert report["deterministic_normalized_trace"] is True
    assert report["durable_persistence_each_run"] is True
    assert report["one_decision_receipt_each_run"] is True
    assert report["all_checks_passed"] is True

    environment = report["runtime_environment"]
    assert set(environment) == {
        "package_name",
        "package_version",
        "python_version",
        "python_implementation",
        "os",
        "os_release",
        "machine",
        "sqlite_version",
        "local_model_mode",
        "database_strategy",
    }
    assert environment["package_version"] != "unknown"
    assert environment["local_model_mode"] == "forced_deterministic_fallback"

    trace = report["representative_trace"]
    assert set(trace) == EXPECTED_TRACE_KEYS
    assert set(trace["planner"]) == {
        "intent_type",
        "plan_dag_nodes",
        "capabilities_invoked",
        "hypotheses_considered",
        "selected_hypothesis_id",
        "critic_scores",
    }
    assert trace["planner"]["intent_type"] == trace["intent_type"]
    assert trace["planner"]["plan_dag_nodes"] == trace["plan_dag_nodes"]
    assert trace["planner"]["capabilities_invoked"] == trace["capabilities_invoked"]
    assert trace["verification"]["safe_to_publish"] is True
    assert trace["persistence"]["committed"] is True
    assert trace["persistence"]["durable"] is True
    assert trace["api_response_contract_valid"] is True

    api_response = trace["api_response"]
    assert set(api_response) == EXPECTED_API_RESPONSE_KEYS_NORMALIZED
    assert api_response["top_level_keys"] == sorted(EXPECTED_API_RESPONSE_KEYS)
    assert api_response["contract_keys_match"] is True
    assert api_response["response_sha256"] == trace["response_sha256"]
    assert report["api_response_sample"]["decision_id"]
    assert len(report["normalized_trace_sha256"]) == 64
    assert len(report["normalized_api_response_sha256"]) == 64

    canonical_api = json.dumps(api_response, sort_keys=True, separators=(",", ":")).encode()
    assert hashlib.sha256(canonical_api).hexdigest() == report["normalized_api_response_sha256"]
    assert report["claim_boundary"] == {
        "production_scale_validated": False,
        "model_quality_benchmark": False,
        "physical_embodiment_evidence": False,
    }
