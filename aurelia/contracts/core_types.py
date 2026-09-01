"""
Aurelia Cognitive OS V4 - Core Contracts & Primitive Types
===========================================================
Defines the foundational, strictly typed cognitive primitives.

Absolute Invariant:
Fact, Observation, Inference, Hypothesis, Prediction, Recommendation,
UserPreference, and UserGoal are distinct cognitive classes and must
never be used interchangeably or silently merged.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Optional, Any, Tuple, Union


class ClaimType(Enum):
    """Explicit classification of cognitive claims."""
    FACT = "fact"                      # Verifiable ground truth with evidence
    OBSERVATION = "observation"        # Direct perceptual input from user/document
    INFERENCE = "inference"            # Deduced insight derived by reasoning engine
    HYPOTHESIS = "hypothesis"          # Proposed candidate strategy or unproven theory
    PREDICTION = "prediction"          # Modeled future trajectory or readiness estimate
    RECOMMENDATION = "recommendation"  # Prescribed actionable guidance
    USER_PREFERENCE = "user_preference"# Explicit subjective preference stated by user
    USER_GOAL = "user_goal"            # Target career objective or milestone


class EvidenceReliability(Enum):
    """Reliability weight of evidence sources."""
    VERIFIED_DOCUMENT = 1.0     # Official document, verified metrics, certified transcript
    REPEATED_DEMONSTRATION = 0.9# High performance across multiple evaluation sessions
    HISTORICAL_FACT = 0.85      # Documented past employment/achievement
    SELF_REPORTED_METRIC = 0.65 # User claim with numbers but unverified
    SELF_REPORTED_CLAIM = 0.40  # Vague self claim without numbers ("I am a leader")
    INFERRED_DERIVATION = 0.50  # Derived by cognitive analysis


class VerificationSeverity(Enum):
    """Severity of verification findings."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    BLOCKER = "blocker"         # Blocks claim publication in final response


@dataclass(frozen=True)
class EvidenceRef:
    """
    Cryptographic/traceable reference to an evidence artifact.
    """
    id: str
    source_type: str             # e.g., "resume_v2", "interview_session_07", "user_statement"
    content_snippet: str
    reliability: EvidenceReliability = EvidenceReliability.SELF_REPORTED_CLAIM
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ConfidenceScore:
    """
    Evidence-grounded confidence metric.
    Confidence reflects evidence density and verification, not LLM token probabilities.
    """
    score: float                # 0.0 to 1.0
    evidence_weight: float      # Contribution from evidence reliability
    sample_size: int = 1        # Number of corroborating observations
    uncertainty_sources: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self):
        if not (0.0 <= self.score <= 1.0):
            raise ValueError(f"Confidence score must be between 0.0 and 1.0, got {self.score}")


@dataclass(frozen=True)
class VerifiedValue:
    """
    A verified numerical or qualitative measurement with explicit provenance.
    """
    value: Any
    confidence: ConfidenceScore
    evidence: Tuple[EvidenceRef, ...] = field(default_factory=tuple)
    method: str = "deterministic_evaluator"
    verified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_authoritative: bool = True


# --- Strictly Typed Cognitive Primitives ---

@dataclass(frozen=True)
class Fact:
    """
    Ground truth fact supported by verifiable evidence.
    Cannot be modified by persona or LLM inference.
    """
    id: str
    subject: str
    predicate: str
    object_value: Any
    evidence: Tuple[EvidenceRef, ...]
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    confidence: float = 1.0
    claim_type: ClaimType = ClaimType.FACT


@dataclass(frozen=True)
class Observation:
    """
    Direct input from a document, chat message, or user interaction.
    """
    id: str
    source: str                 # e.g., "chat_input", "resume_upload"
    raw_content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    claim_type: ClaimType = ClaimType.OBSERVATION


@dataclass(frozen=True)
class Inference:
    """
    Derived analytical deduction. Must cite supporting facts or observations.
    """
    id: str
    claim: str
    derived_from_ids: Tuple[str, ...]   # IDs of supporting Facts/Observations
    confidence: ConfidenceScore
    reasoning_method: str               # e.g., "competency_matrix_evaluator"
    claim_type: ClaimType = ClaimType.INFERENCE


@dataclass(frozen=True)
class Hypothesis:
    """
    Proposed candidate strategy or untested theory.
    """
    id: str
    hypothesis_text: str
    assumptions: Tuple[str, ...]
    risks: Tuple[str, ...]
    test_criteria: str
    confidence: float = 0.5
    claim_type: ClaimType = ClaimType.HYPOTHESIS


@dataclass(frozen=True)
class Prediction:
    """
    Modeled future outcome or readiness trajectory.
    """
    id: str
    target_milestone: str
    estimated_time_months: float
    probability_range: Tuple[float, float]  # e.g., (0.65, 0.85)
    critical_dependencies: Tuple[str, ...]
    claim_type: ClaimType = ClaimType.PREDICTION


@dataclass(frozen=True)
class Recommendation:
    """
    Actionable executive guidance prescribed to the user.
    """
    id: str
    action_statement: str
    rationale: str
    expected_impact: str
    prerequisites: Tuple[str, ...]
    priority_level: int = 1             # 1 (Highest) to 5 (Lowest)
    claim_type: ClaimType = ClaimType.RECOMMENDATION


@dataclass(frozen=True)
class UserPreference:
    """
    Subjective boundary or preference stated by the user.
    """
    id: str
    preference_key: str                 # e.g., "work_location", "risk_tolerance"
    value: Any                          # e.g., "remote_only", "low_risk"
    is_hard_constraint: bool = False
    claim_type: ClaimType = ClaimType.USER_PREFERENCE


@dataclass(frozen=True)
class UserGoal:
    """
    Active career objective with explicit success criteria.
    """
    id: str
    title: str                          # e.g., "VP of Engineering Transition"
    target_role: str
    target_compensation_band: Optional[str] = None
    deadline: Optional[datetime] = None
    success_conditions: Tuple[str, ...] = field(default_factory=tuple)
    status: str = "active"              # active, achieved, superseded, paused
    claim_type: ClaimType = ClaimType.USER_GOAL
