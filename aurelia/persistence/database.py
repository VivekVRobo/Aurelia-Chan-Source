"""SQLite persistence for verified Aurelia cognitive state.

The database is the durable boundary for decision receipts, executive artifacts,
and canonical memory. A verified cycle is committed atomically: if any insert
fails, no receipt, artifact, fact, or inference from that cycle is retained.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Sequence
from dataclasses import asdict, is_dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from aurelia.artifacts.schemas import ExecutiveArtifact
from aurelia.contracts.core_types import (
    ConfidenceScore,
    EvidenceRef,
    EvidenceReliability,
    Fact,
    Inference,
)
from aurelia.contracts.receipt import DecisionReceipt


class PersistenceError(RuntimeError):
    """A verified cognitive cycle could not be persisted atomically."""


class CognitiveDatabase:
    """ACID SQLite storage for receipts, artifacts, and canonical memory."""

    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        if db_path != ":memory:":
            Path(db_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()

    def _init_schema(self) -> None:
        """Create current schema and apply additive migrations for older databases."""
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS decision_receipts (
                    decision_id TEXT PRIMARY KEY,
                    snapshot_id TEXT NOT NULL,
                    request_text TEXT NOT NULL,
                    intent_type TEXT NOT NULL,
                    conclusion_summary TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    receipt_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS executive_artifacts (
                    artifact_id TEXT PRIMARY KEY,
                    artifact_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    decision_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    artifact_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS canonical_facts (
                    fact_id TEXT PRIMARY KEY,
                    subject TEXT NOT NULL,
                    predicate TEXT NOT NULL,
                    object_json TEXT NOT NULL,
                    evidence_json TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    valid_from TEXT,
                    valid_to TEXT,
                    source_candidate_id TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS canonical_inferences (
                    inference_id TEXT PRIMARY KEY,
                    claim TEXT NOT NULL,
                    derived_from_ids_json TEXT NOT NULL,
                    confidence_json TEXT NOT NULL,
                    reasoning_method TEXT NOT NULL,
                    source_candidate_id TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            self._ensure_column("decision_receipts", "receipt_json", "TEXT")
            self._ensure_column("executive_artifacts", "artifact_json", "TEXT")

    def _ensure_column(self, table: str, column: str, definition: str) -> None:
        existing = {
            str(row["name"]) for row in self.conn.execute(f"PRAGMA table_info({table})").fetchall()
        }
        if column not in existing:
            self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def save_verified_cycle(
        self,
        *,
        receipt: DecisionReceipt,
        artifacts: Sequence[ExecutiveArtifact] = (),
        facts: Sequence[tuple[Fact, str | None]] = (),
        inferences: Sequence[tuple[Inference, str | None]] = (),
    ) -> None:
        """Atomically persist a fully verified cognitive cycle."""
        try:
            with self.conn:
                self._insert_receipt(receipt)
                for artifact in artifacts:
                    self._insert_artifact(receipt.decision_id, artifact)
                for fact, candidate_id in facts:
                    self._insert_fact(fact, candidate_id)
                for inference, candidate_id in inferences:
                    self._insert_inference(inference, candidate_id)
        except sqlite3.Error as exc:
            raise PersistenceError(f"Cognitive transaction rolled back: {exc}") from exc

    def _insert_receipt(self, receipt: DecisionReceipt) -> None:
        self.conn.execute(
            """
            INSERT INTO decision_receipts (
                decision_id,
                snapshot_id,
                request_text,
                intent_type,
                conclusion_summary,
                confidence_score,
                receipt_json,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                receipt.decision_id,
                receipt.snapshot_id,
                receipt.request_text,
                receipt.intent_type,
                receipt.conclusion_summary,
                receipt.confidence_score,
                _json_dumps(receipt),
                receipt.created_at.isoformat(),
            ),
        )

    def _insert_artifact(self, decision_id: str, artifact: ExecutiveArtifact) -> None:
        artifact_type = getattr(artifact.artifact_type, "value", str(artifact.artifact_type))
        self.conn.execute(
            """
            INSERT INTO executive_artifacts (
                artifact_id,
                artifact_type,
                title,
                version,
                decision_id,
                payload_json,
                artifact_json,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                artifact.artifact_id,
                artifact_type,
                artifact.title,
                artifact.version,
                decision_id,
                _json_dumps(artifact.payload),
                _json_dumps(artifact),
                artifact.created_at.isoformat(),
            ),
        )

    def _insert_fact(self, fact: Fact, candidate_id: str | None) -> None:
        self.conn.execute(
            """
            INSERT INTO canonical_facts (
                fact_id,
                subject,
                predicate,
                object_json,
                evidence_json,
                confidence,
                valid_from,
                valid_to,
                source_candidate_id,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fact.id,
                fact.subject,
                fact.predicate,
                _json_dumps(fact.object_value),
                _json_dumps(fact.evidence),
                fact.confidence,
                fact.valid_from.isoformat() if fact.valid_from else None,
                fact.valid_to.isoformat() if fact.valid_to else None,
                candidate_id,
                _fact_observed_at(fact).isoformat(),
            ),
        )

    def _insert_inference(self, inference: Inference, candidate_id: str | None) -> None:
        self.conn.execute(
            """
            INSERT INTO canonical_inferences (
                inference_id,
                claim,
                derived_from_ids_json,
                confidence_json,
                reasoning_method,
                source_candidate_id,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                inference.id,
                inference.claim,
                _json_dumps(inference.derived_from_ids),
                _json_dumps(inference.confidence),
                inference.reasoning_method,
                candidate_id,
                datetime.now(UTC).isoformat(),
            ),
        )

    def save_cognitive_cycle_transaction(
        self,
        decision_id: str,
        snapshot_id: str,
        request_text: str,
        intent_type: str,
        conclusion: str,
        confidence: float,
        artifacts: list[dict[str, Any]],
    ) -> bool:
        """Compatibility wrapper for the original V4 persistence contract."""
        try:
            with self.conn:
                self.conn.execute(
                    """
                    INSERT INTO decision_receipts (
                        decision_id,
                        snapshot_id,
                        request_text,
                        intent_type,
                        conclusion_summary,
                        confidence_score
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        decision_id,
                        snapshot_id,
                        request_text,
                        intent_type,
                        conclusion,
                        confidence,
                    ),
                )
                for artifact in artifacts:
                    self.conn.execute(
                        """
                        INSERT INTO executive_artifacts (
                            artifact_id,
                            artifact_type,
                            title,
                            version,
                            decision_id,
                            payload_json
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            artifact["id"],
                            artifact["type"],
                            artifact["title"],
                            artifact["version"],
                            decision_id,
                            _json_dumps(artifact["payload"]),
                        ),
                    )
            return True
        except sqlite3.Error:
            return False

    def get_decision_receipt(self, decision_id: str) -> dict[str, Any] | None:
        """Return legacy receipt fields by ID."""
        row = self.conn.execute(
            """
            SELECT decision_id, snapshot_id, request_text, conclusion_summary, confidence_score
            FROM decision_receipts
            WHERE decision_id = ?
            """,
            (decision_id,),
        ).fetchone()
        if row is None:
            return None
        return dict(row)

    def get_full_receipt_payload(self, decision_id: str) -> dict[str, Any] | None:
        """Return the complete persisted receipt payload when available."""
        row = self.conn.execute(
            "SELECT receipt_json FROM decision_receipts WHERE decision_id = ?",
            (decision_id,),
        ).fetchone()
        if row is None or row["receipt_json"] is None:
            return None
        return json.loads(str(row["receipt_json"]))

    def list_facts(self) -> list[Fact]:
        """Load canonical facts as typed immutable objects."""
        rows = self.conn.execute(
            """
            SELECT fact_id, subject, predicate, object_json, evidence_json,
                   confidence, valid_from, valid_to
            FROM canonical_facts
            ORDER BY created_at ASC
            """
        ).fetchall()
        return [_row_to_fact(row) for row in rows]

    def list_inferences(self) -> list[Inference]:
        """Load canonical inferences as typed immutable objects."""
        rows = self.conn.execute(
            """
            SELECT inference_id, claim, derived_from_ids_json,
                   confidence_json, reasoning_method
            FROM canonical_inferences
            ORDER BY created_at ASC
            """
        ).fetchall()
        return [_row_to_inference(row) for row in rows]

    def retrieval_candidates(self) -> list[dict[str, Any]]:
        """Expose durable canonical memory in HybridMemoryRetriever input form."""
        candidates: list[dict[str, Any]] = []
        for fact in self.list_facts():
            evidence_quality = max(
                (float(evidence.reliability.value) for evidence in fact.evidence),
                default=0.70,
            )
            candidates.append(
                {
                    "id": fact.id,
                    "content": f"{fact.predicate}: {fact.object_value}",
                    "timestamp": _fact_observed_at(fact),
                    "reliability_weight": evidence_quality,
                    "source_type": "canonical_fact",
                }
            )
        for inference in self.list_inferences():
            candidates.append(
                {
                    "id": inference.id,
                    "content": inference.claim,
                    "timestamp": datetime.now(UTC),
                    "reliability_weight": inference.confidence.evidence_weight,
                    "source_type": "canonical_inference",
                }
            )
        return candidates

    def count_rows(self, table: str) -> int:
        """Return a row count for known persistence tables, primarily for diagnostics/tests."""
        allowed = {
            "decision_receipts",
            "executive_artifacts",
            "canonical_facts",
            "canonical_inferences",
        }
        if table not in allowed:
            raise ValueError(f"Unknown persistence table: {table}")
        row = self.conn.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()
        return int(row["count"])

    def close(self) -> None:
        """Close the SQLite connection."""
        self.conn.close()


def _json_dumps(value: Any) -> str:
    return json.dumps(value, default=_json_default, sort_keys=True, separators=(",", ":"))


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    if isinstance(value, set):
        return sorted(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _fact_observed_at(fact: Fact) -> datetime:
    if fact.evidence:
        return max(evidence.observed_at for evidence in fact.evidence)
    return datetime.now(UTC)


def _parse_datetime(value: Any) -> datetime | None:
    if value in {None, ""}:
        return None
    return datetime.fromisoformat(str(value))


def _evidence_from_payload(payload: dict[str, Any]) -> EvidenceRef:
    return EvidenceRef(
        id=str(payload["id"]),
        source_type=str(payload["source_type"]),
        content_snippet=str(payload["content_snippet"]),
        reliability=EvidenceReliability(float(payload["reliability"])),
        observed_at=_parse_datetime(payload.get("observed_at")) or datetime.now(UTC),
        valid_from=_parse_datetime(payload.get("valid_from")),
        valid_to=_parse_datetime(payload.get("valid_to")),
        metadata=dict(payload.get("metadata", {})),
    )


def _row_to_fact(row: sqlite3.Row) -> Fact:
    evidence_payload = json.loads(str(row["evidence_json"]))
    return Fact(
        id=str(row["fact_id"]),
        subject=str(row["subject"]),
        predicate=str(row["predicate"]),
        object_value=json.loads(str(row["object_json"])),
        evidence=tuple(_evidence_from_payload(item) for item in evidence_payload),
        valid_from=_parse_datetime(row["valid_from"]),
        valid_to=_parse_datetime(row["valid_to"]),
        confidence=float(row["confidence"]),
    )


def _row_to_inference(row: sqlite3.Row) -> Inference:
    confidence_payload = json.loads(str(row["confidence_json"]))
    confidence = ConfidenceScore(
        score=float(confidence_payload["score"]),
        evidence_weight=float(confidence_payload["evidence_weight"]),
        sample_size=int(confidence_payload.get("sample_size", 1)),
        uncertainty_sources=tuple(confidence_payload.get("uncertainty_sources", ())),
    )
    return Inference(
        id=str(row["inference_id"]),
        claim=str(row["claim"]),
        derived_from_ids=tuple(json.loads(str(row["derived_from_ids_json"]))),
        confidence=confidence,
        reasoning_method=str(row["reasoning_method"]),
    )
