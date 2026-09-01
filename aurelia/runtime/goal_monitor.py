"""
Aurelia Cognitive OS V3 - Phase 12: Goal Monitor
================================================
Monitors goal progress and triggers alerts.

The goal monitor tracks progress on active goals and alerts
when goals are at risk, completed, or need attention.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class GoalStatus(Enum):
    """Status of goals being monitored."""
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    BEHIND = "behind"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class AlertType(Enum):
    """Types of goal alerts."""
    PROGRESS_SLOW = "progress_slow"
    DEADLINE_APPROACHING = "deadline_approaching"
    DEADLINE_MISSED = "deadline_missed"
    OBSTACLE_DETECTED = "obstacle_detected"
    GOAL_COMPLETED = "goal_completed"


@dataclass
class MonitoredGoal:
    """
    A goal being monitored.
    
    Represents an active goal with progress tracking.
    """
    id: str
    description: str
    target: str
    current_progress: float  # 0-1 scale
    target_progress: float = 1.0
    deadline: Optional[datetime] = None
    status: GoalStatus = GoalStatus.ON_TRACK
    obstacles: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GoalAlert:
    """
    An alert about a goal.
    
    Generated when a goal needs attention.
    """
    id: str
    goal_id: str
    alert_type: AlertType
    message: str
    severity: str  # "info", "warning", "critical"
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class GoalMonitor:
    """
    Monitors goal progress and triggers alerts.
    
    The goal monitor:
    - Tracks progress on active goals
    - Evaluates goal status (on track, at risk, behind, etc.)
    - Generates alerts when goals need attention
    - Provides progress summaries
    """
    
    def __init__(self):
        self.monitored_goals: Dict[str, MonitoredGoal] = {}
        self.alerts: List[GoalAlert] = []
        self.goal_counter = 0
        self.alert_counter = 0
    
    def add_goal(
        self,
        description: str,
        target: str,
        deadline: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MonitoredGoal:
        """Add a goal to monitor."""
        goal_id = f"goal_{self.goal_counter}"
        
        goal = MonitoredGoal(
            id=goal_id,
            description=description,
            target=target,
            current_progress=0.0,
            deadline=deadline,
            status=GoalStatus.ON_TRACK,
            metadata=metadata or {}
        )
        
        self.monitored_goals[goal_id] = goal
        self.goal_counter += 1
        
        return goal
    
    def update_progress(self, goal_id: str, progress: float):
        """Update progress on a monitored goal."""
        goal = self.get_goal(goal_id)
        if not goal:
            return
        
        goal.current_progress = progress
        self._evaluate_goal_status(goal)
    
    def add_obstacle(self, goal_id: str, obstacle: str):
        """Add an obstacle to a monitored goal."""
        goal = self.get_goal(goal_id)
        if not goal:
            return
        
        goal.obstacles.append(obstacle)
        self._evaluate_goal_status(goal)
    
    def _evaluate_goal_status(self, goal: MonitoredGoal):
        """Evaluate the current status of a goal."""
        # Check if completed
        if goal.current_progress >= goal.target_progress:
            goal.status = GoalStatus.COMPLETED
            self._generate_alert(goal, AlertType.GOAL_COMPLETED, "Goal has been completed!", "info")
            return
        
        # Check for obstacles
        if goal.obstacles:
            goal.status = GoalStatus.BLOCKED
            self._generate_alert(goal, AlertType.OBSTACLE_DETECTED, f"Obstacle detected: {goal.obstacles[-1]}", "warning")
            return
        
        # Check deadline
        if goal.deadline:
            time_remaining = (goal.deadline - datetime.now()).total_seconds()
            if time_remaining < 0:
                goal.status = GoalStatus.BEHIND
                self._generate_alert(goal, AlertType.DEADLINE_MISSED, "Deadline has been missed", "critical")
            elif time_remaining < 86400 * 2:  # Less than 2 days
                goal.status = GoalStatus.AT_RISK
                self._generate_alert(goal, AlertType.DEADLINE_APPROACHING, "Deadline approaching soon", "warning")
        
        # Check progress rate (simplified)
        if goal.current_progress < 0.3:
            goal.status = GoalStatus.AT_RISK
            self._generate_alert(goal, AlertType.PROGRESS_SLOW, "Progress is slower than expected", "warning")
        else:
            goal.status = GoalStatus.ON_TRACK
    
    def _generate_alert(self, goal: MonitoredGoal, alert_type: AlertType, message: str, severity: str):
        """Generate an alert for a goal."""
        alert_id = f"alert_{self.alert_counter}"
        
        alert = GoalAlert(
            id=alert_id,
            goal_id=goal.id,
            alert_type=alert_type,
            message=message,
            severity=severity,
            timestamp=datetime.now()
        )
        
        self.alerts.append(alert)
        self.alert_counter += 1
    
    def get_goal(self, goal_id: str) -> Optional[MonitoredGoal]:
        """Get a monitored goal by ID."""
        return self.monitored_goals.get(goal_id)
    
    def get_goals_by_status(self, status: GoalStatus) -> List[MonitoredGoal]:
        """Get all goals with a specific status."""
        return [g for g in self.monitored_goals.values() if g.status == status]
    
    def get_alerts_by_severity(self, severity: str) -> List[GoalAlert]:
        """Get all alerts of a specific severity."""
        return [a for a in self.alerts if a.severity == severity]
    
    def get_recent_alerts(self, limit: int = 10) -> List[GoalAlert]:
        """Get recent alerts."""
        return self.alerts[-limit:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of goal monitoring."""
        return {
            "total_goals": len(self.monitored_goals),
            "by_status": {
                status.value: len(self.get_goals_by_status(status))
                for status in GoalStatus
            },
            "total_alerts": len(self.alerts),
            "critical_alerts": len(self.get_alerts_by_severity("critical")),
            "warning_alerts": len(self.get_alerts_by_severity("warning"))
        }