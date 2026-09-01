"""
Aurelia Cognitive OS V4 - Memory Write Firewall
================================================
Absolute Invariant: The LLM cannot directly mutate canonical memory.
All proposed memories must pass through this deterministic firewall.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Tuple, List, Dict, Any
from aurelia.contracts.core_types import ClaimType, EvidenceRef, Fact, Inference, ConfidenceScore


@dataclass(frozen=True)
class MemoryCandidate:
    """
    A proposed memory item submitted by a specialist or reasoning model.
    """
    candidate_id: str
    claim_type: ClaimType
    key: str
    value: Any
    evidence: Tuple[EvidenceRef, ...]
    proposed_by: str                    # e.g., "ollama_reasoning_v4", "resume_parser"
    confidence: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class MemoryCommitResult:
    """Result of evaluating a memory candidate against the firewall."""
    approved: bool
    candidate_id: str
    rejection_reason: Optional[str] = None
    committed_fact: Optional[Fact] = None
    committed_inference: Optional[Inference] = None


class MemoryWritePolicy:
    """
    Deterministic guardian of canonical memory integrity.
    """

    MIN_FACT_CONFIDENCE = 0.70
    MIN_INFERENCE_CONFIDENCE = 0.50

    @classmethod
    def evaluate_candidate(
        cls,
        candidate: MemoryCandidate,
        existing_facts: List[Fact]
    ) -> MemoryCommitResult:
        """
        Evaluates a memory candidate against evidence thresholds and consistency rules.
        """
        # Rule 1: Facts must have valid, non-empty evidence
        if candidate.claim_type == ClaimType.FACT:
            if not candidate.evidence or len(candidate.evidence) == 0:
                return MemoryCommitResult(
                    approved=False,
                    candidate_id=candidate.candidate_id,
                    rejection_reason="REJECTED: Canonical Facts require non-empty verifiable evidence."
                )
            if candidate.confidence < cls.MIN_FACT_CONFIDENCE:
                return MemoryCommitResult(
                    approved=False,
                    candidate_id=candidate.candidate_id,
                    rejection_reason=f"REJECTED: Fact confidence {candidate.confidence:.2f} is below required threshold ({cls.MIN_FACT_CONFIDENCE:.2f})."
                )

        # Rule 2: Inferences require minimum confidence
        if candidate.claim_type == ClaimType.INFERENCE:
            if candidate.confidence < cls.MIN_INFERENCE_CONFIDENCE:
                return MemoryCommitResult(
                    approved=False,
                    candidate_id=candidate.candidate_id,
                    rejection_reason=f"REJECTED: Inference confidence {candidate.confidence:.2f} is below minimum threshold ({cls.MIN_INFERENCE_CONFIDENCE:.2f})."
                )

        # Rule 3: Contradiction check against existing active facts
        for existing in existing_facts:
            if existing.subject == "user" and existing.predicate == candidate.key:
                # If values strictly disagree and both claim to be active ground facts
                if existing.object_value != candidate.value and candidate.claim_type == ClaimType.FACT:
                    # Check temporal validity
                    if existing.valid_to is None: # Existing fact is still marked active
                        return MemoryCommitResult(
                            approved=False,
                            candidate_id=candidate.candidate_id,
                            rejection_reason=f"CONFLICT: Proposed fact '{candidate.key}={candidate.value}' contradicts active verified fact '{existing.key if hasattr(existing, 'key') else existing.predicate}={existing.object_value}'."
                        )

        # Commit Approved Fact or Inference
        if candidate.claim_type == ClaimType.FACT:
            fact = Fact(
                id=f"fact_{candidate.candidate_id}",
                subject="user",
                predicate=candidate.key,
                object_value=candidate.value,
                evidence=candidate.evidence,
                confidence=candidate.confidence
            )
            return MemoryCommitResult(approved=True, candidate_id=candidate.candidate_id, committed_fact=fact)
            
        elif candidate.claim_type == ClaimType.INFERENCE:
            inf = Inference(
                id=f"inf_{candidate.candidate_id}",
                claim=str(candidate.value),
                derived_from_ids=tuple(e.id for e in candidate.evidence),
                confidence=ConfidenceScore(score=candidate.confidence, evidence_weight=0.7),
                reasoning_method=candidate.proposed_by
            )
            return MemoryCommitResult(approved=True, candidate_id=candidate.candidate_id, committed_inference=inf)

        return MemoryCommitResult(approved=True, candidate_id=candidate.candidate_id)
