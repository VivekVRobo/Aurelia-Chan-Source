"""
Aurelia Cognitive OS V4 - Memory Conflict & Goal Supersession Engine
====================================================================
Detects contradictions between old and new knowledge, resolves goal updates
without data loss or silent overwriting, and emits supersession events.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Tuple, Optional
from aurelia.contracts.core_types import UserGoal, Fact


@dataclass(frozen=True)
class GoalSupersessionEvent:
    """Audit record when a user updates their primary career objective."""
    event_id: str
    old_goal_id: str
    old_goal_title: str
    new_goal_id: str
    new_goal_title: str
    superseded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reason: str = "User requested objective shift"


class MemoryConflictEngine:
    """
    Manages active goal supersession and detects factual contradictions.
    """

    @staticmethod
    def resolve_goal_update(
        existing_goals: List[UserGoal],
        new_goal: UserGoal,
        reason: str = "User initiated objective change"
    ) -> Tuple[List[UserGoal], Optional[GoalSupersessionEvent]]:
        """
        Supersedes conflicting active goals cleanly without deleting historical records.
        """
        updated_goals: List[UserGoal] = []
        supersession_event: Optional[GoalSupersessionEvent] = None
        
        for g in existing_goals:
            if g.status == "active" and g.target_role != new_goal.target_role:
                # Mark old goal as superseded
                superseded_goal = UserGoal(
                    id=g.id,
                    title=g.title,
                    target_role=g.target_role,
                    target_compensation_band=g.target_compensation_band,
                    deadline=g.deadline,
                    success_conditions=g.success_conditions,
                    status="superseded"
                )
                updated_goals.append(superseded_goal)
                
                supersession_event = GoalSupersessionEvent(
                    event_id=f"super_{g.id}_{new_goal.id}",
                    old_goal_id=g.id,
                    old_goal_title=g.title,
                    new_goal_id=new_goal.id,
                    new_goal_title=new_goal.title,
                    reason=reason
                )
            else:
                updated_goals.append(g)
                
        updated_goals.append(new_goal)
        return updated_goals, supersession_event
