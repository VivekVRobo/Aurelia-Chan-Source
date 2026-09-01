"""Regression tests for durable, policy-gated Aurelia runtime persistence."""

from __future__ import annotations

import os
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

from aurelia.artifacts.schemas import ArtifactType, ExecutiveArtifact
from aurelia.contracts.core_types import ClaimType, EvidenceRef, EvidenceReliability
from aurelia.contracts.receipt import DecisionReceipt
from aurelia.llm.ollama_cortex import LocalOllamaCortex
from aurelia.memory.write_policy import MemoryCandidate
from aurelia.persistence.database import CognitiveDatabase, PersistenceError
from aurelia.runtime.app_bootstrap import create_application_runtime, resolve_database_path
from aurelia.runtime.cognitive_runtime import AureliaCognitiveRuntime
from aurelia.runtime.persistence import RuntimePersistence


class TestRuntimePersistence(unittest.TestCase):
    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_file_backed_cycle_survives_database_reopen(self, _mock_llm) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db_path = str(Path(directory) / "aurelia.db")
            first_runtime = AureliaCognitiveRuntime(db_path=db_path)
            result = first_runtime.process_query("Give me general career guidance.")
            self.assertTrue(result.persistence.committed)
            self.assertTrue(result.persistence.durable)
            decision_id = result.decision_receipt.decision_id
            first_runtime.database.close()

            reopened = CognitiveDatabase(db_path)
            stored = reopened.get_full_receipt_payload(decision_id)
            self.assertIsNotNone(stored)
            self.assertEqual(stored["decision_id"], decision_id)
            self.assertEqual(
                tuple(stored["capabilities_invoked"]),
                result.decision_receipt.capabilities_invoked,
            )
            reopened.close()

    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_approved_fact_is_persisted_and_retrieved_by_next_cycle(self, _mock_llm) -> None:
        runtime = AureliaCognitiveRuntime()
        evidence = EvidenceRef(
            id="ev_scope_1",
            source_type="verified_document",
            content_snippet="Director of Engineering scope includes 12 direct reports.",
            reliability=EvidenceReliability.VERIFIED_DOCUMENT,
        )
        candidate = MemoryCandidate(
            candidate_id="scope_1",
            claim_type=ClaimType.FACT,
            key="leadership_scope",
            value="Director of Engineering team of 12",
            evidence=(evidence,),
            proposed_by="verified_document_parser",
            confidence=0.95,
        )

        first = runtime.process_query(
            "Record this verified leadership scope.",
            memory_candidates=(candidate,),
        )
        self.assertTrue(first.persistence.committed)
        self.assertFalse(first.persistence.durable)
        self.assertEqual(first.persistence.approved_memory_ids, ("fact_scope_1",))
        self.assertEqual(runtime.database.count_rows("canonical_facts"), 1)

        second = runtime.process_query("What is my leadership_scope for Director of Engineering?")
        self.assertGreater(second.trace.memories_retrieved_count, 0)
        persistent = runtime.persistence.retrieval_candidates()
        self.assertTrue(any(item["source_type"] == "canonical_fact" for item in persistent))

    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_low_confidence_fact_is_rejected_without_persistence(self, _mock_llm) -> None:
        runtime = AureliaCognitiveRuntime()
        candidate = MemoryCandidate(
            candidate_id="weak_1",
            claim_type=ClaimType.FACT,
            key="budget_scope",
            value="$2M",
            evidence=(
                EvidenceRef(
                    id="ev_weak",
                    source_type="user_statement",
                    content_snippet="I think I owned about $2M.",
                    reliability=EvidenceReliability.SELF_REPORTED_CLAIM,
                ),
            ),
            proposed_by="chat_parser",
            confidence=0.40,
        )

        result = runtime.process_query("Store my budget scope.", memory_candidates=(candidate,))
        self.assertEqual(result.persistence.approved_memory_ids, ())
        self.assertEqual(len(result.persistence.rejected_memory), 1)
        self.assertEqual(runtime.database.count_rows("canonical_facts"), 0)

    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_conflicting_fact_is_rejected_without_overwriting_canonical_fact(
        self, _mock_llm
    ) -> None:
        runtime = AureliaCognitiveRuntime()
        evidence = EvidenceRef(
            id="ev_verified",
            source_type="verified_document",
            content_snippet="Verified team size record.",
            reliability=EvidenceReliability.VERIFIED_DOCUMENT,
        )
        first_candidate = MemoryCandidate(
            candidate_id="team_1",
            claim_type=ClaimType.FACT,
            key="team_size",
            value=12,
            evidence=(evidence,),
            proposed_by="verified_document_parser",
            confidence=0.95,
        )
        runtime.process_query("Record verified team size.", memory_candidates=(first_candidate,))

        conflicting = MemoryCandidate(
            candidate_id="team_2",
            claim_type=ClaimType.FACT,
            key="team_size",
            value=30,
            evidence=(evidence,),
            proposed_by="verified_document_parser",
            confidence=0.95,
        )
        result = runtime.process_query(
            "Replace verified team size.", memory_candidates=(conflicting,)
        )

        self.assertEqual(result.persistence.approved_memory_ids, ())
        self.assertEqual(len(result.persistence.rejected_memory), 1)
        facts = runtime.database.list_facts()
        self.assertEqual(len(facts), 1)
        self.assertEqual(facts[0].object_value, 12)

    def test_atomic_rollback_removes_receipt_and_memory_on_artifact_collision(self) -> None:
        database = CognitiveDatabase(":memory:")
        persistence = RuntimePersistence(database)
        artifact = _artifact("artifact_collision", "decision_seed")
        persistence.commit_verified_cycle(
            receipt=_receipt("decision_seed", artifact.artifact_id),
            artifacts=(artifact,),
        )

        evidence = EvidenceRef(
            id="ev_atomic",
            source_type="verified_document",
            content_snippet="Verified budget ownership.",
            reliability=EvidenceReliability.VERIFIED_DOCUMENT,
        )
        candidate = MemoryCandidate(
            candidate_id="atomic_fact",
            claim_type=ClaimType.FACT,
            key="budget_ownership",
            value=True,
            evidence=(evidence,),
            proposed_by="verified_document_parser",
            confidence=0.99,
        )

        with self.assertRaises(PersistenceError):
            persistence.commit_verified_cycle(
                receipt=_receipt("decision_rollback", artifact.artifact_id),
                artifacts=(artifact,),
                memory_candidates=(candidate,),
            )

        self.assertIsNone(database.get_decision_receipt("decision_rollback"))
        self.assertEqual(database.count_rows("canonical_facts"), 0)
        self.assertEqual(database.count_rows("executive_artifacts"), 1)

    def test_unverified_receipt_is_never_committed(self) -> None:
        database = CognitiveDatabase(":memory:")
        persistence = RuntimePersistence(database)
        receipt = _receipt("decision_unverified", verification_passed=False)

        with self.assertRaises(PersistenceError):
            persistence.commit_verified_cycle(receipt=receipt, artifacts=())

        self.assertEqual(database.count_rows("decision_receipts"), 0)

    def test_application_runtime_defaults_to_file_backed_workspace_database(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            runtime = create_application_runtime(workspace)
            expected = (workspace / "data" / "aurelia.db").resolve()
            self.assertEqual(Path(runtime.database.db_path), expected)
            diagnostics = runtime.persistence.diagnostics()
            self.assertTrue(diagnostics["durable"])
            runtime.database.close()

    def test_database_path_environment_override_can_be_relative_to_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            with patch.dict(os.environ, {"AURELIA_DB_PATH": "state/custom.db"}):
                resolved = resolve_database_path(workspace)
            self.assertEqual(resolved, (workspace / "state" / "custom.db").resolve())


def _receipt(
    decision_id: str,
    artifact_id: str | None = None,
    *,
    verification_passed: bool = True,
) -> DecisionReceipt:
    return DecisionReceipt(
        decision_id=decision_id,
        snapshot_id=f"snapshot_{decision_id}",
        request_text="test request",
        intent_type="general_guidance",
        plan_dag_nodes=("evaluate", "render", "verify"),
        capabilities_invoked=("specialist.evaluate", "response.render.aurelia"),
        inferences_made=(),
        hypotheses_considered=(),
        selected_hypothesis_id=None,
        critic_scores={},
        numerical_calculations_verified=(),
        verification_passed=verification_passed,
        verification_severity="info" if verification_passed else "blocker",
        conclusion_summary="verified result",
        artifacts_generated_ids=(artifact_id,) if artifact_id else (),
        confidence_score=0.90,
        created_at=datetime.now(UTC),
        deterministic_replay_hash="a" * 64,
    )


def _artifact(artifact_id: str, decision_id: str) -> ExecutiveArtifact:
    return ExecutiveArtifact(
        artifact_id=artifact_id,
        artifact_type=ArtifactType.DECISION_MATRIX,
        title="Decision Matrix",
        version=1,
        created_from_decision_id=decision_id,
        updated_from_event_id=None,
        payload={"options": []},
        created_at=datetime.now(UTC),
    )


if __name__ == "__main__":
    unittest.main()
