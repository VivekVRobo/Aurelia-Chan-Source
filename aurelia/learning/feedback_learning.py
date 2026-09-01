"""
Aurelia Cognitive OS V3 - Phase 10: Feedback Learning
=====================================================
Learns from user feedback to improve performance.

Feedback learning allows Aurelia to improve based on explicit
and implicit feedback from users.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class FeedbackType(Enum):
    """Types of feedback."""
    EXPLICIT_POSITIVE = "explicit_positive"
    EXPLICIT_NEGATIVE = "explicit_negative"
    IMPLICIT_POSITIVE = "implicit_positive"
    IMPLICIT_NEGATIVE = "implicit_negative"
    CORRECTION = "correction"


class FeedbackCategory(Enum):
    """Categories of feedback."""
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    CLARITY = "clarity"
    COMPLETENESS = "completeness"
    USEFULNESS = "usefulness"


@dataclass
class FeedbackEvent:
    """
    A feedback event from a user.
    
    Represents explicit or implicit feedback on a response or action.
    """
    id: str
    feedback_type: FeedbackType
    feedback_category: FeedbackCategory
    context: str  # What the feedback is about
    content: str  # The feedback content
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningInsight:
    """
    An insight derived from feedback analysis.
    
    Represents a learning point that can improve performance.
    """
    id: str
    insight_type: str
    description: str
    actionable_changes: List[str]
    confidence: float
    timestamp: datetime


class FeedbackLearner:
    """
    Learns from user feedback to improve performance.
    
    The feedback learner:
    - Collects explicit and implicit feedback
    - Analyzes feedback patterns
    - Generates learning insights
    - Implements improvements based on feedback
    """
    
    def __init__(self):
        self.feedback_events: List[FeedbackEvent] = []
        self.learning_insights: List[LearningInsight] = []
        self.feedback_counter = 0
        self.insight_counter = 0
    
    def record_feedback(
        self,
        feedback_type: FeedbackType,
        feedback_category: FeedbackCategory,
        context: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> FeedbackEvent:
        """Record a feedback event."""
        feedback_id = f"feedback_{self.feedback_counter}"
        
        event = FeedbackEvent(
            id=feedback_id,
            feedback_type=feedback_type,
            feedback_category=feedback_category,
            context=context,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.feedback_events.append(event)
        self.feedback_counter += 1
        
        return event
    
    def analyze_feedback_patterns(self) -> List[LearningInsight]:
        """
        Analyze feedback patterns to generate insights.
        
        Identifies recurring patterns in feedback that suggest improvements.
        """
        insights = []
        
        # Group feedback by category
        category_feedback: Dict[FeedbackCategory, List[FeedbackEvent]] = {}
        for event in self.feedback_events:
            if event.feedback_category not in category_feedback:
                category_feedback[event.feedback_category] = []
            category_feedback[event.feedback_category].append(event)
        
        # Analyze each category
        for category, events in category_feedback.items():
            if len(events) >= 3:  # Need at least 3 events to detect pattern
                insight = self._generate_category_insight(category, events)
                if insight:
                    insights.append(insight)
        
        # Add insights to learning insights
        for insight in insights:
            self.learning_insights.append(insight)
        
        return insights
    
    def _generate_category_insight(self, category: FeedbackCategory, events: List[FeedbackEvent]) -> Optional[LearningInsight]:
        """Generate an insight for a specific feedback category."""
        # Count positive vs negative feedback
        positive_count = sum(1 for e in events if e.feedback_type in [FeedbackType.EXPLICIT_POSITIVE, FeedbackType.IMPLICIT_POSITIVE])
        negative_count = sum(1 for e in events if e.feedback_type in [FeedbackType.EXPLICIT_NEGATIVE, FeedbackType.IMPLICIT_NEGATIVE])
        
        insight_id = f"insight_{self.insight_counter}"
        self.insight_counter += 1
        
        if negative_count > positive_count:
            # More negative feedback - need improvement
            insight = LearningInsight(
                id=insight_id,
                insight_type="improvement_needed",
                description=f"Users consistently provide negative feedback on {category.value}",
                actionable_changes=[
                    f"Review processes related to {category.value}",
                    f"Improve {category.value} in responses",
                    f"Consider user preferences for {category.value}"
                ],
                confidence=min(1.0, negative_count / len(events)),
                timestamp=datetime.now()
            )
            return insight
        elif positive_count > negative_count:
            # More positive feedback - strength to maintain
            insight = LearningInsight(
                id=insight_id,
                insight_type="strength_identified",
                description=f"Users consistently provide positive feedback on {category.value}",
                actionable_changes=[
                    f"Maintain current approach to {category.value}",
                    f"Consider applying {category.value} strategies to other areas"
                ],
                confidence=min(1.0, positive_count / len(events)),
                timestamp=datetime.now()
            )
            return insight
        else:
            # Mixed feedback - need investigation
            insight = LearningInsight(
                id=insight_id,
                insight_type="mixed_feedback",
                description=f"Mixed feedback on {category.value} suggests inconsistent performance",
                actionable_changes=[
                    f"Investigate causes of variability in {category.value}",
                    f"Standardize approach to {category.value}"
                ],
                confidence=0.5,
                timestamp=datetime.now()
            )
            return insight
    
    def get_feedback_by_category(self, category: FeedbackCategory) -> List[FeedbackEvent]:
        """Get all feedback events for a specific category."""
        return [e for e in self.feedback_events if e.feedback_category == category]
    
    def get_feedback_by_type(self, feedback_type: FeedbackType) -> List[FeedbackEvent]:
        """Get all feedback events of a specific type."""
        return [e for e in self.feedback_events if e.feedback_type == feedback_type]
    
    def get_recent_feedback(self, limit: int = 10) -> List[FeedbackEvent]:
        """Get recent feedback events."""
        return self.feedback_events[-limit:]
    
    def get_learning_insights(self, limit: int = 10) -> List[LearningInsight]:
        """Get recent learning insights."""
        return self.learning_insights[-limit:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the feedback learner state."""
        return {
            "total_feedback": len(self.feedback_events),
            "total_insights": len(self.learning_insights),
            "by_category": {
                cat.value: len(self.get_feedback_by_category(cat))
                for cat in FeedbackCategory
            },
            "by_type": {
                ft.value: len(self.get_feedback_by_type(ft))
                for ft in FeedbackType
            }
        }