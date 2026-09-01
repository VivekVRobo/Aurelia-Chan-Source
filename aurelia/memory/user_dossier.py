"""
Aurelia Cognitive OS V4 - Persistent User Career Dossier V2
===========================================================
Structured, canonical career dossier tracking verified user history,
competencies, compensation bands, goals, and evidence.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional, Any
from aurelia.contracts.core_types import Fact, UserGoal, UserPreference, VerifiedValue


@dataclass(frozen=True)
class CareerTimelineEvent:
    """A verified career milestone in the user's timeline."""
    event_id: str
    company_name: str
    role_title: str
    start_date: datetime
    end_date: Optional[datetime] = None  # None if currently active
    is_current: bool = False
    scale_summary: str = ""              # e.g., "Led team of 14, $4.2M budget"
    achievements: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CompensationRecord:
    """Historical or target compensation data point."""
    record_id: str
    effective_date: datetime
    base_salary_usd: float
    target_bonus_pct: float
    annual_equity_usd: float
    total_target_comp_usd: float
    company_stage: str                   # e.g., "Seed", "Series B", "Public Big Tech"


@dataclass
class UserDossier:
    """
    Canonical persistent user profile.
    Maintains provenance and confidence for all career records.
    """
    user_id: str
    full_name: str
    current_role: str
    current_level: str
    target_role: str
    years_experience: float
    
    # Structured History
    timeline: List[CareerTimelineEvent] = field(default_factory=list)
    compensation_history: List[CompensationRecord] = field(default_factory=list)
    verified_competencies: Dict[str, float] = field(default_factory=dict) # competency_id -> observed score (1.0 - 5.0)
    
    # Active Goals & Constraints
    active_goals: List[UserGoal] = field(default_factory=list)
    user_preferences: List[UserPreference] = field(default_factory=list)
    
    # Evaluation History
    past_resume_scores: List[Dict[str, Any]] = field(default_factory=list)
    past_interview_scores: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata & Versioning
    version: int = 1
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def get_active_goal(self) -> Optional[UserGoal]:
        """Returns the primary active career goal."""
        for g in self.active_goals:
            if g.status == "active":
                return g
        return None
