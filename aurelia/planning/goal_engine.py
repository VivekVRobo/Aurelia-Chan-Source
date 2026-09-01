"""
Aurelia Cognitive OS V3 - Phase 5: Goal Engine
============================================
Manages long-term goals and their decomposition into sub-goals.

The goal engine handles multi-step objectives like:
- "Become a Director within 2 years"
- "Improve communication skills to executive level"
- "Lead a major cloud migration project"
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
from aurelia.cognition.contracts import Goal as BaseGoal, Evidence


class GoalStatus(Enum):
    """Status of a goal."""
    PROPOSED = "proposed"
    ACTIVE = "active"
    BLOCKED = "blocked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DEFERRED = "deferred"


class GoalPriority(Enum):
    """Priority levels for goals."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Goal:
    """
    A goal in the goal engine.
    
    Goals can be long-term objectives that are decomposed into
    sub-goals and tasks.
    """
    id: str
    title: str
    description: str
    status: GoalStatus
    priority: GoalPriority
    created_at: datetime
    target_completion: Optional[datetime] = None
    parent_goal_id: Optional[str] = None  # For hierarchical goals
    sub_goal_ids: List[str] = field(default_factory=list)
    evidence: List[Evidence] = field(default_factory=list)
    confidence: float = 1.0
    completion_percentage: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class GoalEngine:
    """
    Manages long-term goals and their decomposition.
    
    The goal engine handles:
    - Goal creation and decomposition
    - Goal tracking and progress calculation
    - Goal dependency management
    - Goal status transitions
    """
    
    def __init__(self):
        self.goals: Dict[str, Goal] = {}
        self.goal_counter = 0
    
    def create_goal(
        self,
        title: str,
        description: str,
        priority: GoalPriority = GoalPriority.MEDIUM,
        target_completion: Optional[datetime] = None,
        parent_goal_id: Optional[str] = None,
        evidence: Optional[List[Evidence]] = None
    ) -> Goal:
        """Create a new goal."""
        goal_id = f"goal_{self.goal_counter}"
        
        goal = Goal(
            id=goal_id,
            title=title,
            description=description,
            status=GoalStatus.PROPOSED,
            priority=priority,
            created_at=datetime.now(),
            target_completion=target_completion,
            parent_goal_id=parent_goal_id,
            evidence=evidence or []
        )
        
        self.goals[goal_id] = goal
        self.goal_counter += 1
        
        # Add to parent's sub-goals if applicable
        if parent_goal_id and parent_goal_id in self.goals:
            self.goals[parent_goal_id].sub_goal_ids.append(goal_id)
        
        return goal
    
    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """Get a goal by ID."""
        return self.goals.get(goal_id)
    
    def update_goal_status(self, goal_id: str, status: GoalStatus):
        """Update the status of a goal."""
        if goal_id in self.goals:
            self.goals[goal_id].status = status
    
    def update_goal_progress(self, goal_id: str, completion_percentage: float):
        """Update the completion percentage of a goal."""
        if goal_id in self.goals:
            self.goals[goal_id].completion_percentage = max(0.0, min(1.0, completion_percentage))
            
            # Auto-update status based on completion
            if completion_percentage >= 1.0:
                self.goals[goal_id].status = GoalStatus.COMPLETED
            elif completion_percentage > 0.0:
                self.goals[goal_id].status = GoalStatus.IN_PROGRESS
    
    def get_goals_by_status(self, status: GoalStatus) -> List[Goal]:
        """Get all goals with a specific status."""
        return [g for g in self.goals.values() if g.status == status]
    
    def get_goals_by_priority(self, priority: GoalPriority) -> List[Goal]:
        """Get all goals with a specific priority."""
        return [g for g in self.goals.values() if g.priority == priority]
    
    def get_active_goals(self) -> List[Goal]:
        """Get all active goals."""
        return [g for g in self.goals.values() if g.status in [GoalStatus.ACTIVE, GoalStatus.IN_PROGRESS]]
    
    def get_blocked_goals(self) -> List[Goal]:
        """Get all blocked goals."""
        return [g for g in self.goals.values() if g.status == GoalStatus.BLOCKED]
    
    def get_goal_hierarchy(self, goal_id: str) -> List[Goal]:
        """Get the hierarchy of goals (parent and sub-goals)."""
        hierarchy = []
        goal = self.get_goal(goal_id)
        
        if goal:
            hierarchy.append(goal)
            
            # Add sub-goals
            for sub_goal_id in goal.sub_goal_ids:
                hierarchy.extend(self.get_goal_hierarchy(sub_goal_id))
        
        return hierarchy
    
    def calculate_parent_progress(self, goal_id: str) -> float:
        """Calculate progress based on sub-goals."""
        goal = self.get_goal(goal_id)
        if not goal or not goal.sub_goal_ids:
            return goal.completion_percentage if goal else 0.0
        
        # Average of sub-goal completions
        sub_completions = []
        for sub_goal_id in goal.sub_goal_ids:
            sub_goal = self.get_goal(sub_goal_id)
            if sub_goal:
                sub_completions.append(sub_goal.completion_percentage)
        
        if sub_completions:
            avg_completion = sum(sub_completions) / len(sub_completions)
            self.update_goal_progress(goal_id, avg_completion)
            return avg_completion
        
        return 0.0
    
    def decompose_goal(
        self,
        parent_goal_id: str,
        sub_goal_titles: List[str],
        sub_goal_descriptions: List[str]
    ) -> List[Goal]:
        """Decompose a goal into sub-goals."""
        if len(sub_goal_titles) != len(sub_goal_descriptions):
            raise ValueError("Number of titles must match number of descriptions")
        
        sub_goals = []
        for title, description in zip(sub_goal_titles, sub_goal_descriptions):
            sub_goal = self.create_goal(
                title=title,
                description=description,
                parent_goal_id=parent_goal_id
            )
            sub_goals.append(sub_goal)
        
        return sub_goals
    
    def get_goals_near_deadline(self, days: int = 7) -> List[Goal]:
        """Get goals with deadlines within the next N days."""
        from datetime import timedelta
        cutoff = datetime.now() + timedelta(days=days)
        
        return [
            g for g in self.goals.values()
            if g.target_completion and g.target_completion <= cutoff
            and g.status not in [GoalStatus.COMPLETED, GoalStatus.CANCELLED]
        ]
    
    def get_overdue_goals(self) -> List[Goal]:
        """Get goals that are past their deadline."""
        now = datetime.now()
        
        return [
            g for g in self.goals.values()
            if g.target_completion and g.target_completion < now
            and g.status not in [GoalStatus.COMPLETED, GoalStatus.CANCELLED]
        ]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the goal engine state."""
        return {
            "total_goals": len(self.goals),
            "by_status": {status.value: len(self.get_goals_by_status(status)) for status in GoalStatus},
            "by_priority": {priority.value: len(self.get_goals_by_priority(priority)) for priority in GoalPriority},
            "active_goals": len(self.get_active_goals()),
            "blocked_goals": len(self.get_blocked_goals()),
            "near_deadline": len(self.get_goals_near_deadline(7)),
            "overdue": len(self.get_overdue_goals())
        }