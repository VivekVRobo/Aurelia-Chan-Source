"""
Aurelia Cognitive OS V3 - Phase 12: Proactive Insights
=====================================================
Generates proactive insights and recommendations.

Proactive insights allow Aurelia to suggest improvements and
opportunities without being explicitly asked.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class InsightType(Enum):
    """Types of proactive insights."""
    OPPORTUNITY = "opportunity"
    IMPROVEMENT = "improvement"
    WARNING = "warning"
    RECOMMENDATION = "recommendation"
    PATTERN = "pattern"


class InsightPriority(Enum):
    """Priority levels for insights."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ProactiveInsight:
    """
    A proactive insight or recommendation.
    
    Represents a suggestion generated without explicit user request.
    """
    id: str
    insight_type: InsightType
    title: str
    description: str
    priority: InsightPriority
    actionable_steps: List[str]
    context: Dict[str, Any]
    timestamp: datetime
    dismissed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProactiveInsightGenerator:
    """
    Generates proactive insights and recommendations.
    
    The proactive insight generator:
    - Analyzes system state and user interactions
    - Identifies opportunities for improvement
    - Generates actionable recommendations
    - Tracks insight acceptance and dismissal
    """
    
    def __init__(self):
        self.insights: List[ProactiveInsight] = []
        self.insight_counter = 0
    
    def generate_insight(
        self,
        insight_type: InsightType,
        title: str,
        description: str,
        priority: InsightPriority,
        actionable_steps: List[str],
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProactiveInsight:
        """Generate a new proactive insight."""
        insight_id = f"insight_{self.insight_counter}"
        
        insight = ProactiveInsight(
            id=insight_id,
            insight_type=insight_type,
            title=title,
            description=description,
            priority=priority,
            actionable_steps=actionable_steps,
            context=context or {},
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.insights.append(insight)
        self.insight_counter += 1
        
        return insight
    
    def dismiss_insight(self, insight_id: str):
        """Dismiss an insight."""
        insight = self.get_insight(insight_id)
        if insight:
            insight.dismissed = True
    
    def get_insight(self, insight_id: str) -> Optional[ProactiveInsight]:
        """Get an insight by ID."""
        for insight in self.insights:
            if insight.id == insight_id:
                return insight
        return None
    
    def get_insights_by_type(self, insight_type: InsightType) -> List[ProactiveInsight]:
        """Get all insights of a specific type."""
        return [i for i in self.insights if i.insight_type == insight_type]
    
    def get_insights_by_priority(self, priority: InsightPriority) -> List[ProactiveInsight]:
        """Get all insights of a specific priority."""
        return [i for i in self.insights if i.priority == priority]
    
    def get_active_insights(self) -> List[ProactiveInsight]:
        """Get all non-dismissed insights."""
        return [i for i in self.insights if not i.dismissed]
    
    def get_recent_insights(self, limit: int = 10) -> List[ProactiveInsight]:
        """Get recent insights."""
        return self.insights[-limit:]
    
    def generate_career_opportunity_insight(
        self,
        user_role: str,
        target_role: str,
        skill_gaps: List[str]
    ) -> ProactiveInsight:
        """Generate a career opportunity insight."""
        title = f"Career advancement opportunity: {target_role}"
        description = f"Based on your current role as {user_role}, you have a strong opportunity to advance to {target_role}."
        
        actionable_steps = [
            f"Focus on developing: {', '.join(skill_gaps[:3])}",
            "Seek mentorship from current {target_role}s",
            "Take on projects that demonstrate {target_role} competencies"
        ]
        
        return self.generate_insight(
            insight_type=InsightType.OPPORTUNITY,
            title=title,
            description=description,
            priority=InsightPriority.HIGH,
            actionable_steps=actionable_steps,
            context={"current_role": user_role, "target_role": target_role}
        )
    
    def generate_skill_improvement_insight(
        self,
        skill_name: str,
        current_level: float,
        target_level: float
    ) -> ProactiveInsight:
        """Generate a skill improvement insight."""
        title = f"Skill development opportunity: {skill_name}"
        description = f"Your {skill_name} skill level ({current_level:.1%}) is below the target ({target_level:.1%})."
        
        actionable_steps = [
            f"Enroll in {skill_name} training courses",
            f"Practice {skill_name} in current projects",
            "Seek feedback on {skill_name} from peers"
        ]
        
        return self.generate_insight(
            insight_type=InsightType.IMPROVEMENT,
            title=title,
            description=description,
            priority=InsightPriority.MEDIUM,
            actionable_steps=actionable_steps,
            context={"skill": skill_name, "current": current_level, "target": target_level}
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of proactive insights."""
        active = self.get_active_insights()
        
        return {
            "total_insights": len(self.insights),
            "active_insights": len(active),
            "dismissed_insights": len(self.insights) - len(active),
            "by_type": {
                it.value: len(self.get_insights_by_type(it))
                for it in InsightType
            },
            "by_priority": {
                p.value: len(self.get_insights_by_priority(p))
                for p in InsightPriority
            }
        }