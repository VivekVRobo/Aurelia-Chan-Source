"""Stable HTTP serialization contract for the Aurelia cognitive runtime."""

from __future__ import annotations

from typing import Any

from aurelia.embodiment.adapter import AureliaEmbodimentAdapter
from aurelia.embodiment.contracts import SCHEMA_VERSION
from aurelia.runtime.cognitive_runtime import CognitiveCycleResponse


def serialize_cognitive_cycle(result: CognitiveCycleResponse) -> dict[str, Any]:
    """Serialize one verified cognitive cycle without dropping runtime provenance.

    The top-level expression and portrait fields are retained for existing clients.
    New clients should consume the typed ``persona``, ``persistence``, and
    actuator-free ``character_response`` blocks.
    """
    character_response = AureliaEmbodimentAdapter.adapt(result)
    return {
        "response": result.response_text,
        "expression": result.expression,
        "portrait": result.portrait_path,
        "confidence": result.confidence_percentage,
        "persona": {
            "emotion": result.persona.emotion.value,
            "emotion_intensity": result.persona.emotion_intensity.value,
            "expression_style": result.persona.expression_style.value,
            "mode": result.persona.mode,
            "traits": list(result.persona.traits),
            "expression": result.persona.expression,
            "portrait": result.persona.portrait_path,
        },
        "character_response": character_response.to_dict(),
        "trace": {
            "understood": result.trace.understood_goal,
            "memories_count": result.trace.memories_retrieved_count,
            "graph_facts_count": result.trace.graph_facts_count,
            "specialists_invoked": list(result.trace.specialists_invoked),
            "alternatives_evaluated": list(result.trace.alternatives_evaluated),
            "numerical_checks": list(result.trace.numerical_calculations_verified),
            "unresolved_unknowns": list(result.trace.unresolved_unknowns),
            "confidence_level": result.trace.confidence_level,
            "summary_formatted": result.trace.to_formatted_summary(),
        },
        "verification": {
            "passed": result.verification_report.passed,
            "severity": result.verification_report.max_severity.value,
            "safe_to_publish": result.verification_report.is_safe_to_publish,
            "issues": [
                {
                    "type": issue.issue_type,
                    "severity": issue.severity.value,
                    "description": issue.description,
                    "target_claim": issue.target_claim,
                }
                for issue in result.verification_report.issues
            ],
        },
        "persistence": {
            "committed": result.persistence.committed,
            "durable": result.persistence.durable,
            "approved_memory_ids": list(result.persistence.approved_memory_ids),
            "rejected_memory": [
                {"candidate_id": candidate_id, "reason": reason}
                for candidate_id, reason in result.persistence.rejected_memory
            ],
        },
        "artifacts": [
            {
                "id": artifact.artifact_id,
                "type": artifact.artifact_type.value,
                "title": artifact.title,
                "version": artifact.version,
                "payload": artifact.payload,
            }
            for artifact in result.artifacts
        ],
        "decision_id": result.decision_receipt.decision_id,
    }


def serialize_runtime_status(result: dict[str, object]) -> dict[str, object]:
    """Return persistence diagnostics without exposing the local database path."""
    return {
        "runtime_configured": True,
        "persona_renderer": True,
        "embodiment_contract": SCHEMA_VERSION,
        "persistence": {
            "durable": bool(result["durable"]),
            "decision_receipts": int(result["decision_receipts"]),
            "executive_artifacts": int(result["executive_artifacts"]),
            "canonical_facts": int(result["canonical_facts"]),
            "canonical_inferences": int(result["canonical_inferences"]),
        },
    }
