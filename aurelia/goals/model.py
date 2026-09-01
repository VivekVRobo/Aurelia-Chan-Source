"""
Aurelia Cognitive OS V4 - Goal Engine & Progress Resolver
==========================================================
Enables active goal tracking, dependency resolution, and automated
milestone progress calculation from incoming evidence.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Tuple, Optional, Any
from aurelia.contracts.core_types import EvidenceRef


@dataclass(frozen=True)
class GoalMilestone:
    """A discrete milestone required to achieve a career goal."""
    milestone_id: str
    title: str                           # e.g., "Complete Executive Finance & P&L Training"
    target_competency_id: str            # e.g., "comp_budget"
    required_evidence_type: str          # e.g., "training_completion", "executive_presentation"
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    supporting_evidence: Tuple[EvidenceRef, ...] = field(default_factory=tuple)


@dataclass
class ActiveGoalTracker:
    """
    Active tracker for a user's primary career objective.
    """
    goal_id: str
    target_role: str
    target_compensation_usd: float
    deadline: Optional[datetime]
    milestones: List[GoalMilestone] = field(default_factory=list)
    overall_progress_pct: float = 0.0

    def recalculate_progress(self) -> float:
        """Calculates exact deterministic progress from completed milestones."""
        if not self.milestones:
            self.overall_progress_pct = 0.0
            return 0.0
        completed = sum(1 for m in self.milestones if m.is_completed)
        self.overall_progress_pct = (completed / len(self.milestones)) * 100.0
        return self.overall_progress_pct

    def resolve_incoming_evidence(self, text: str, evidence: EvidenceRef) -> Optional[str]:
        """
        Automatically resolves whether an observation satisfies an active milestone.
        """
        text_lower = text.lower()
        
        for i, m in enumerate(self.milestones):
            if not m.is_completed:
                # Check for milestone title or competency keywords
                keywords = m.title.lower().split()
                matches = sum(1 for kw in keywords if len(kw) > 3 and kw in text_lower)
                
                if matches >= 2 or (m.target_competency_id in text_lower):
                    # Complete milestone
                    updated_milestone = GoalMilestone(
                        milestone_id=m.milestone_id,
                        title=m.title,
                        target_competency_id=m.target_competency_id,
                        required_evidence_type=m.required_evidence_type,
                        is_completed=True,
                        completed_at=datetime.now(timezone.utc),
                        supporting_evidence=m.supporting_evidence + (evidence,)
                    )
                    self.milestones[i] = updated_milestone
                    self.recalculate_progress()
                    return f"Milestone '{m.title}' marked COMPLETED. Total Goal Progress: {self.overall_progress_pct:.1f}%."
                    
        return None
