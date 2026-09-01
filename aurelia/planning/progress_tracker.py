"""
Aurelia Cognitive OS V3 - Phase 5: Progress Tracker
====================================================
Tracks progress over time for goals and tasks.

The progress tracker handles:
- Historical progress tracking
- Progress trend analysis
- Milestone tracking
- Progress notifications and alerts
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum


class ProgressTrend(Enum):
    """Trend of progress over time."""
    ACCELERATING = "accelerating"  # Progress is speeding up
    STEADY = "steady"  # Consistent progress
    DECELERATING = "decelerating"  # Progress is slowing down
    STALLED = "stalled"  # No progress
    REGRESSING = "regressing"  # Progress going backward


@dataclass
class ProgressSnapshot:
    """
    A snapshot of progress at a specific point in time.
    
    Progress snapshots allow for trend analysis over time.
    """
    timestamp: datetime
    goal_id: str
    completion_percentage: float
    tasks_completed: int
    tasks_total: int
    notes: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Milestone:
    """
    A milestone in the progress towards a goal.
    
    Milestones mark significant achievements in the journey.
    """
    id: str
    goal_id: str
    title: str
    description: str
    target_completion_percentage: float
    achieved: bool = False
    achieved_at: Optional[datetime] = None
    target_date: Optional[datetime] = None


@dataclass
class ProgressAlert:
    """
    An alert about progress issues.
    
    Alerts notify about problems like stalled progress,
    approaching deadlines, or missed milestones.
    """
    id: str
    alert_type: str  # "stalled", "deadline_approaching", "milestone_missed", "trend_concern"
    severity: str  # "low", "medium", "high", "critical"
    goal_id: str
    message: str
    created_at: datetime
    acknowledged: bool = False


class ProgressTracker:
    """
    Tracks progress over time for goals and tasks.
    
    The progress tracker:
    - Records progress snapshots
    - Analyzes progress trends
    - Tracks milestones
    - Generates progress alerts
    """
    
    def __init__(self):
        self.snapshots: List[ProgressSnapshot] = []
        self.milestones: Dict[str, Milestone] = {}  # milestone_id -> Milestone
        self.alerts: List[ProgressAlert] = []
        self.milestone_counter = 0
        self.alert_counter = 0
    
    def record_snapshot(
        self,
        goal_id: str,
        completion_percentage: float,
        tasks_completed: int,
        tasks_total: int,
        notes: Optional[str] = None
    ) -> ProgressSnapshot:
        """Record a progress snapshot."""
        snapshot = ProgressSnapshot(
            timestamp=datetime.now(),
            goal_id=goal_id,
            completion_percentage=completion_percentage,
            tasks_completed=tasks_completed,
            tasks_total=tasks_total,
            notes=notes
        )
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def get_snapshots_for_goal(self, goal_id: str) -> List[ProgressSnapshot]:
        """Get all progress snapshots for a specific goal."""
        return [s for s in self.snapshots if s.goal_id == goal_id]
    
    def get_latest_snapshot(self, goal_id: str) -> Optional[ProgressSnapshot]:
        """Get the most recent snapshot for a goal."""
        goal_snapshots = self.get_snapshots_for_goal(goal_id)
        if goal_snapshots:
            return sorted(goal_snapshots, key=lambda s: s.timestamp, reverse=True)[0]
        return None
    
    def calculate_progress_trend(self, goal_id: str, days: int = 30) -> ProgressTrend:
        """
        Calculate the progress trend over the last N days.
        
        Analyzes whether progress is accelerating, steady, decelerating, stalled, or regressing.
        """
        snapshots = self.get_snapshots_for_goal(goal_id)
        cutoff = datetime.now() - timedelta(days=days)
        recent_snapshots = [s for s in snapshots if s.timestamp >= cutoff]
        
        if len(recent_snapshots) < 2:
            return ProgressTrend.STALLED
        
        # Sort by time
        recent_snapshots.sort(key=lambda s: s.timestamp)
        
        # Calculate progress rate
        first_snapshot = recent_snapshots[0]
        last_snapshot = recent_snapshots[-1]
        
        time_diff = (last_snapshot.timestamp - first_snapshot.timestamp).total_seconds() / 86400  # days
        progress_diff = last_snapshot.completion_percentage - first_snapshot.completion_percentage
        
        if time_diff == 0:
            return ProgressTrend.STALLED
        
        daily_progress_rate = progress_diff / time_diff
        
        # Determine trend
        if daily_progress_rate > 0.01:  # More than 1% per day
            return ProgressTrend.ACCELERATING
        elif daily_progress_rate > 0.005:  # 0.5% to 1% per day
            return ProgressTrend.STEADY
        elif daily_progress_rate > 0:  # Positive but slow
            return ProgressTrend.DECELERATING
        elif daily_progress_rate == 0:
            return ProgressTrend.STALLED
        else:
            return ProgressTrend.REGRESSING
    
    def create_milestone(
        self,
        goal_id: str,
        title: str,
        description: str,
        target_completion_percentage: float,
        target_date: Optional[datetime] = None
    ) -> Milestone:
        """Create a milestone for a goal."""
        milestone_id = f"milestone_{self.milestone_counter}"
        
        milestone = Milestone(
            id=milestone_id,
            goal_id=goal_id,
            title=title,
            description=description,
            target_completion_percentage=target_completion_percentage,
            target_date=target_date
        )
        
        self.milestones[milestone_id] = milestone
        self.milestone_counter += 1
        
        return milestone
    
    def check_milestone_achievement(self, goal_id: str, current_completion: float) -> List[Milestone]:
        """Check if any milestones have been achieved."""
        achieved_milestones = []
        
        for milestone in self.milestones.values():
            if (milestone.goal_id == goal_id and 
                not milestone.achieved and 
                current_completion >= milestone.target_completion_percentage):
                
                milestone.achieved = True
                milestone.achieved_at = datetime.now()
                achieved_milestones.append(milestone)
        
        return achieved_milestones
    
    def get_milestones_for_goal(self, goal_id: str) -> List[Milestone]:
        """Get all milestones for a specific goal."""
        return [m for m in self.milestones.values() if m.goal_id == goal_id]
    
    def create_alert(
        self,
        alert_type: str,
        severity: str,
        goal_id: str,
        message: str
    ) -> ProgressAlert:
        """Create a progress alert."""
        alert_id = f"alert_{self.alert_counter}"
        
        alert = ProgressAlert(
            id=alert_id,
            alert_type=alert_type,
            severity=severity,
            goal_id=goal_id,
            message=message,
            created_at=datetime.now()
        )
        
        self.alerts.append(alert)
        self.alert_counter += 1
        
        return alert
    
    def generate_progress_alerts(self, goal_id: str) -> List[ProgressAlert]:
        """
        Generate progress alerts based on current state.
        
        Checks for stalled progress, approaching deadlines, missed milestones, etc.
        """
        alerts = []
        
        latest_snapshot = self.get_latest_snapshot(goal_id)
        if not latest_snapshot:
            return alerts
        
        # Check for stalled progress
        trend = self.calculate_progress_trend(goal_id, days=14)
        if trend == ProgressTrend.STALLED:
            alerts.append(self.create_alert(
                alert_type="stalled",
                severity="medium",
                goal_id=goal_id,
                message="Progress has stalled over the last 2 weeks"
            ))
        elif trend == ProgressTrend.REGRESSING:
            alerts.append(self.create_alert(
                alert_type="regressing",
                severity="high",
                goal_id=goal_id,
                message="Progress is regressing - completion percentage has decreased"
            ))
        
        # Check for approaching deadlines (if target date is near)
        milestones = self.get_milestones_for_goal(goal_id)
        for milestone in milestones:
            if (not milestone.achieved and 
                milestone.target_date and 
                milestone.target_date <= datetime.now() + timedelta(days=7)):
                
                alerts.append(self.create_alert(
                    alert_type="deadline_approaching",
                    severity="high",
                    goal_id=goal_id,
                    message=f"Milestone '{milestone.title}' deadline approaching in less than 7 days"
                ))
        
        # Check for missed deadlines
        for milestone in milestones:
            if (not milestone.achieved and 
                milestone.target_date and 
                milestone.target_date < datetime.now()):
                
                alerts.append(self.create_alert(
                    alert_type="milestone_missed",
                    severity="critical",
                    goal_id=goal_id,
                    message=f"Milestone '{milestone.title}' deadline has been missed"
                ))
        
        return alerts
    
    def acknowledge_alert(self, alert_id: str):
        """Mark an alert as acknowledged."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
    
    def get_unacknowledged_alerts(self) -> List[ProgressAlert]:
        """Get all unacknowledged alerts."""
        return [a for a in self.alerts if not a.acknowledged]
    
    def get_alerts_for_goal(self, goal_id: str) -> List[ProgressAlert]:
        """Get all alerts for a specific goal."""
        return [a for a in self.alerts if a.goal_id == goal_id]
    
    def get_progress_summary(self, goal_id: str) -> Dict[str, Any]:
        """Get a comprehensive progress summary for a goal."""
        latest_snapshot = self.get_latest_snapshot(goal_id)
        trend = self.calculate_progress_trend(goal_id)
        milestones = self.get_milestones_for_goal(goal_id)
        recent_alerts = self.get_alerts_for_goal(goal_id)
        
        return {
            "latest_completion": latest_snapshot.completion_percentage if latest_snapshot else 0.0,
            "latest_snapshot_time": latest_snapshot.timestamp.isoformat() if latest_snapshot else None,
            "trend": trend.value,
            "total_milestones": len(milestones),
            "achieved_milestones": sum(1 for m in milestones if m.achieved),
            "pending_milestones": sum(1 for m in milestones if not m.achieved),
            "recent_alerts": len(recent_alerts),
            "unacknowledged_alerts": len([a for a in recent_alerts if not a.acknowledged])
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the progress tracker state."""
        return {
            "total_snapshots": len(self.snapshots),
            "total_milestones": len(self.milestones),
            "total_alerts": len(self.alerts),
            "unacknowledged_alerts": len(self.get_unacknowledged_alerts()),
            "goals_tracked": len(set(s.goal_id for s in self.snapshots))
        }