"""
Aurelia Cognitive OS V4 - MeaningFrame Contracts
=================================================
Represents the structured semantic meaning resolved by the Perception & Meaning Engine.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Optional, Any, Tuple
from aurelia.contracts.core_types import Observation, UserPreference


class IntentType(Enum):
    """Classified executive intent categories."""
    CAREER_ROADMAP = "career_roadmap"          # Long-term career trajectory & milestone planning
    RESUME_AUDIT = "resume_audit"              # Executive resume / CV evaluation
    INTERVIEW_PRACTICE = "interview_practice"  # Mock scenario evaluation
    COMPENSATION_STRATEGY = "compensation_strategy" # Salary / Equity / Bonus negotiation
    WORKPLACE_CONFLICT = "workplace_conflict"  # Leadership disputes & politics
    BURNOUT_TRIAGE = "burnout_triage"          # Operational workload rebalancing
    DECISION_EVALUATION = "decision_evaluation"# Tradeoff analysis (Startup vs Big Tech)
    STATUS_INQUIRY = "status_inquiry"          # Fast lookup of past scores / goals
    GENERAL_MENTORSHIP = "general_mentorship"  # Broad leadership inquiry


@dataclass(frozen=True)
class EntityRecord:
    """Extracted named entity or quantitative parameter."""
    name: str
    entity_type: str            # "role", "company", "compensation", "skill", "metric"
    normalized_value: Any
    raw_mention: str
    confidence: float = 1.0


@dataclass(frozen=True)
class TemporalConstraint:
    """Resolved temporal reference (e.g. 'last month', 'by Q4', '6-month review')."""
    raw_expression: str
    resolved_start: Optional[datetime] = None
    resolved_end: Optional[datetime] = None
    duration_months: Optional[float] = None
    is_relative: bool = True


@dataclass(frozen=True)
class MeaningFrame:
    """
    Immutable semantic representation of user input.
    """
    frame_id: str
    raw_input: str
    intent: IntentType
    primary_entities: Tuple[EntityRecord, ...] = field(default_factory=tuple)
    temporal_constraints: Tuple[TemporalConstraint, ...] = field(default_factory=tuple)
    detected_user_preferences: Tuple[UserPreference, ...] = field(default_factory=tuple)
    emotional_subtext: str = "neutral"          # e.g., "urgent", "frustrated", "confident"
    complexity_level: str = "standard"          # "reflex", "standard", "deep", "verified"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
