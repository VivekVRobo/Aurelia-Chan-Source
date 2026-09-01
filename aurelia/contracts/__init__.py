"""
Aurelia Cognitive OS V4 - Contracts Package
===========================================
"""

from aurelia.contracts.core_types import (
    ClaimType,
    EvidenceReliability,
    VerificationSeverity,
    EvidenceRef,
    ConfidenceScore,
    VerifiedValue,
    Fact,
    Observation,
    Inference,
    Hypothesis,
    Prediction,
    Recommendation,
    UserPreference,
    UserGoal,
)
from aurelia.contracts.meaning_frame import (
    IntentType,
    EntityRecord,
    TemporalConstraint,
    MeaningFrame,
)
from aurelia.contracts.snapshot import (
    DataFreshnessRecord,
    CognitiveSnapshot,
)
from aurelia.contracts.receipt import (
    InferenceRecord,
    DecisionReceipt,
)

__all__ = [
    "ClaimType",
    "EvidenceReliability",
    "VerificationSeverity",
    "EvidenceRef",
    "ConfidenceScore",
    "VerifiedValue",
    "Fact",
    "Observation",
    "Inference",
    "Hypothesis",
    "Prediction",
    "Recommendation",
    "UserPreference",
    "UserGoal",
    "IntentType",
    "EntityRecord",
    "TemporalConstraint",
    "MeaningFrame",
    "DataFreshnessRecord",
    "CognitiveSnapshot",
    "InferenceRecord",
    "DecisionReceipt",
]
