"""
Aurelia Cognitive OS V5 - Core Contracts & Provenance Types
============================================================
Defines the strict type system for lifelong learning, goal forecasting,
active learning, personal strategy modeling, and proactive autonomy.

Invariant 1: Learning modulates controlled parameters and insights, NEVER raw code.
Invariant 2: All predictions, beliefs, and insights have explicit confidence and provenance.
Invariant 3: Goal forecasts are probabilistic and time-bounded.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional, Tuple, List


class GoalStatusEnum(str, Enum):
    """Status classification for live goal forecasts."""
    ON_TRACK = "ON_TRACK"
    AT_RISK = "AT_RISK"
    BLOCKED = "BLOCKED"
    AHEAD_OF_PLAN = "AHEAD_OF_PLAN"


class RecommendationStatus(str, Enum):
    """Lifecycle state of an executive recommendation."""
    RECOMMENDED = "RECOMMENDED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class ExperimentStatus(str, Enum):
    """Status of an empirical strategy experiment."""
    RUNNING = "RUNNING"
    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    INCONCLUSIVE = "INCONCLUSIVE"


class StalenessStatus(str, Enum):
    """Freshness status of artifacts, predictions, and knowledge."""
    FRESH = "FRESH"
    STALE = "STALE"
    INVALIDATED = "INVALIDATED"


@dataclass(frozen=True)
class RecommendationOutcome:
    """Tracks what occurred following a specific recommendation."""
    recommendation_id: str
    action_taken: bool
    status: RecommendationStatus
    recommended_at: datetime
    completed_at: Optional[datetime]
    predicted_effect: str
    observed_effect: Optional[str]
    success_score: float # 0.0 to 1.0
    measured_improvement: float # e.g. +0.4 on competency score
    provenance_evidence_id: Optional[str] = None


@dataclass(frozen=True)
class CompetencyObservation:
    """Historical timestamped measurement of a competency."""
    competency_id: str
    observed_at: datetime
    score: float # 1.0 to 5.0
    confidence: float # 0.0 to 1.0
    source_context: str
    evidence_id: str


@dataclass(frozen=True)
class CompetencyVelocityRecord:
    """Calculated longitudinal trajectory of a competency."""
    competency_id: str
    current_score: float
    velocity_per_month: float # delta score / month
    acceleration_per_month: float # delta velocity / month
    is_plateaued: bool
    is_regressing: bool
    projected_weeks_to_target: Optional[float]
    historical_count: int


@dataclass(frozen=True)
class CriticalPathNode:
    """Node in the Critical Path Method (CPM) dependency graph."""
    node_id: str
    name: str
    estimated_weeks: float
    current_score: float
    target_score: float
    is_on_critical_path: bool
    earliest_start_week: float
    latest_finish_week: float
    slack_weeks: float


@dataclass(frozen=True)
class GoalForecast:
    """Probabilistic prediction of goal completion trajectory."""
    goal_id: str
    target_role: str
    probability_of_completion: float # 0.0 to 1.0
    likely_completion_window_months: Tuple[float, float] # (min_months, max_months)
    status: GoalStatusEnum
    critical_path_bottleneck: str
    blockers: Tuple[str, ...]
    accelerating_factors: Tuple[str, ...]
    confidence_score: float
    forecasted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class PersonalStrategyModel:
    """Learned parameters of what strategies and styles work for this individual."""
    preferred_learning_mode: str # e.g. "simulation", "reading", "mock"
    follow_through_by_modality: Dict[str, float] # modality -> probability (0.0 to 1.0)
    response_to_feedback_style: Dict[str, float] # "direct" -> 0.89, "gentle" -> 0.61
    domain_learning_velocities: Dict[str, float] # domain -> velocity
    optimal_session_duration_minutes: int
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class StrategicInsight:
    """Durable, evidence-backed strategic lesson with temporal freshness decay."""
    insight_id: str
    claim: str
    category: str
    evidence_count: int
    confidence: float # 0.0 to 1.0
    first_observed: datetime
    last_validated: datetime
    decay_half_life_days: float = 180.0
    is_active: bool = True

    def calculate_current_freshness(self, current_time: datetime) -> float:
        """Computes exponential freshness decay: e^(-lambda * dt)."""
        dt_days = (current_time - self.last_validated).total_seconds() / 86400.0
        if dt_days <= 0:
            return 1.0
        import math
        decay_rate = math.log(2) / max(1.0, self.decay_half_life_days)
        return math.exp(-decay_rate * dt_days)


@dataclass(frozen=True)
class LearningReceipt:
    """Immutable provenance record documenting why and how a belief changed."""
    receipt_id: str
    insight_or_belief_id: str
    previous_belief: str
    new_evidence_refs: Tuple[str, ...]
    updated_belief: str
    update_method: str # e.g. "Bayesian_Conjugate_Update", "Empirical_Outcome"
    confidence_delta: float
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class InformationNeed:
    """Diagnostic uncertainty quantification for active learning."""
    variable_name: str
    current_uncertainty: float # 0.0 to 1.0
    expected_decision_impact: float # 0.0 to 1.0 (EVOI)
    acquisition_cost: str # "LOW", "MEDIUM", "HIGH"
    priority_score: float # expected_decision_impact * current_uncertainty


@dataclass(frozen=True)
class EventSignificance:
    """Evaluates whether an environmental event warrants proactive cognition."""
    event_type: str
    relevance_to_active_goal: float # 0.0 to 1.0
    magnitude: float # 0.0 to 1.0
    novelty: float # 0.0 to 1.0
    requires_replan: bool
    significance_score: float # weighted composite


@dataclass(frozen=True)
class ProactiveAction:
    """A proactive suggestion or autonomous insight prepared for the user."""
    action_id: str
    title: str
    reason_to_interrupt: str # Mandatory "Why now?"
    significance_score: float
    confidence: float
    proposed_replan: Optional[str]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ArtifactStalenessRecord:
    """Tracks causal staleness triggers for executive artifacts."""
    artifact_id: str
    status: StalenessStatus
    stale_reason: str
    triggering_event_id: str
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
