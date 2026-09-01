"""Verified persistence coordinator for Aurelia runtime cycles."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock

from aurelia.artifacts.schemas import ExecutiveArtifact
from aurelia.contracts.core_types import Fact, Inference
from aurelia.contracts.receipt import DecisionReceipt
from aurelia.memory.write_policy import MemoryCandidate, MemoryCommitResult, MemoryWritePolicy
from aurelia.persistence.database import CognitiveDatabase, PersistenceError


@dataclass(frozen=True)
class PersistenceCommitResult:
    """Observed result of one atomic verified-cycle persistence attempt."""

    committed: bool
    durable: bool
    approved_memory_ids: tuple[str, ...]
    rejected_memory: tuple[tuple[str, str], ...]


class RuntimePersistence:
    """Gate canonical memory through policy and commit a verified cycle atomically."""

    def __init__(self, database: CognitiveDatabase) -> None:
        self.database = database
        self._lock = RLock()

    def commit_verified_cycle(
        self,
        *,
        receipt: DecisionReceipt,
        artifacts: tuple[ExecutiveArtifact, ...],
        memory_candidates: tuple[MemoryCandidate, ...] = (),
    ) -> PersistenceCommitResult:
        """Persist receipt, artifacts, and approved memory in one transaction."""
        if not receipt.verification_passed:
            raise PersistenceError("Unverified cognitive cycles cannot be persisted.")

        with self._lock:
            existing_facts = self.database.list_facts()
            approved_facts: list[tuple[Fact, str | None]] = []
            approved_inferences: list[tuple[Inference, str | None]] = []
            approved_ids: list[str] = []
            rejected: list[tuple[str, str]] = []

            for candidate in memory_candidates:
                outcome = MemoryWritePolicy.evaluate_candidate(candidate, existing_facts)
                self._collect_memory_outcome(
                    candidate,
                    outcome,
                    existing_facts,
                    approved_facts,
                    approved_inferences,
                    approved_ids,
                    rejected,
                )

            self.database.save_verified_cycle(
                receipt=receipt,
                artifacts=artifacts,
                facts=approved_facts,
                inferences=approved_inferences,
            )
            return PersistenceCommitResult(
                committed=True,
                durable=self.database.db_path != ":memory:",
                approved_memory_ids=tuple(approved_ids),
                rejected_memory=tuple(rejected),
            )

    @staticmethod
    def _collect_memory_outcome(
        candidate: MemoryCandidate,
        outcome: MemoryCommitResult,
        existing_facts: list[Fact],
        approved_facts: list[tuple[Fact, str | None]],
        approved_inferences: list[tuple[Inference, str | None]],
        approved_ids: list[str],
        rejected: list[tuple[str, str]],
    ) -> None:
        if not outcome.approved:
            rejected.append(
                (
                    candidate.candidate_id,
                    outcome.rejection_reason or "Memory candidate rejected by policy.",
                )
            )
            return

        if outcome.committed_fact is not None:
            approved_facts.append((outcome.committed_fact, candidate.candidate_id))
            existing_facts.append(outcome.committed_fact)
            approved_ids.append(outcome.committed_fact.id)
        if outcome.committed_inference is not None:
            approved_inferences.append((outcome.committed_inference, candidate.candidate_id))
            approved_ids.append(outcome.committed_inference.id)

    def retrieval_candidates(self) -> list[dict[str, object]]:
        """Return persisted canonical memory in retriever-compatible form."""
        with self._lock:
            return self.database.retrieval_candidates()

    def diagnostics(self) -> dict[str, object]:
        """Return truthful persistence readiness and row counts."""
        with self._lock:
            return {
                "db_path": self.database.db_path,
                "durable": self.database.db_path != ":memory:",
                "decision_receipts": self.database.count_rows("decision_receipts"),
                "executive_artifacts": self.database.count_rows("executive_artifacts"),
                "canonical_facts": self.database.count_rows("canonical_facts"),
                "canonical_inferences": self.database.count_rows("canonical_inferences"),
            }
