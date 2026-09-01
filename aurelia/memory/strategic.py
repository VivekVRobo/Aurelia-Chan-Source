"""
Aurelia Cognitive OS V3 - Phase 4: Strategic Memory
================================================
Lessons gathered over time about the user and domain.

Strategic memory stores meta-learnings:
- User learns better from mock interviews than theory
- Previous answers improve when examples are requested before scoring
- Specific patterns in user's learning style
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class LearningCategory(Enum):
    """Categories of strategic learnings."""
    USER_PREFERENCE = "user_preference"
    LEARNING_STYLE = "learning_style"
    INTERACTION_PATTERN = "interaction_pattern"
    DOMAIN_INSIGHT = "domain_insight"
    SYSTEM_OPTIMIZATION = "system_optimization"


@dataclass
class StrategicLearning:
    """
    A strategic learning about the user or domain.
    
    These are meta-learnings that improve how Aurelia interacts
    with the user over time.
    """
    id: str
    category: LearningCategory
    proposition: str
    confidence: float
    evidence: List[str]
    first_observed: datetime
    last_confirmed: datetime
    confirmation_count: int
    impact: str  # "high", "medium", "low"


class StrategicMemory:
    """
    Lessons gathered over time.
    
    Examples:
    - User learns better from mock interviews than theory
    - Previous answers improve when examples are requested before scoring
    """
    
    def __init__(self):
        self.learnings: Dict[str, StrategicLearning] = {}
        self.learning_counter = 0
    
    def add_learning(self, learning: StrategicLearning):
        """Add a strategic learning."""
        self.learnings[learning.id] = learning
        self.learning_counter += 1
    
    def create_learning(
        self,
        category: LearningCategory,
        proposition: str,
        confidence: float,
        evidence: List[str],
        impact: str = "medium"
    ) -> StrategicLearning:
        """Create and add a new strategic learning."""
        learning_id = f"learning_{self.learning_counter}"
        
        learning = StrategicLearning(
            id=learning_id,
            category=category,
            proposition=proposition,
            confidence=confidence,
            evidence=evidence,
            first_observed=datetime.now(),
            last_confirmed=datetime.now(),
            confirmation_count=1,
            impact=impact
        )
        
        self.add_learning(learning)
        return learning
    
    def confirm_learning(self, learning_id: str):
        """Confirm an existing learning."""
        if learning_id in self.learnings:
            learning = self.learnings[learning_id]
            learning.last_confirmed = datetime.now()
            learning.confirmation_count += 1
            # Increase confidence with each confirmation
            learning.confidence = min(1.0, learning.confidence + 0.05)
    
    def get_learning(self, learning_id: str) -> Optional[StrategicLearning]:
        """Get a learning by ID."""
        return self.learnings.get(learning_id)
    
    def get_learnings_by_category(self, category: LearningCategory) -> List[StrategicLearning]:
        """Get all learnings in a category."""
        return [l for l in self.learnings.values() if l.category == category]
    
    def get_high_impact_learnings(self) -> List[StrategicLearning]:
        """Get learnings with high impact."""
        return [l for l in self.learnings.values() if l.impact == "high"]
    
    def get_learnings_by_confidence(self, min_confidence: float = 0.7) -> List[StrategicLearning]:
        """Get learnings above confidence threshold."""
        return [l for l in self.learnings.values() if l.confidence >= min_confidence]
    
    def query(self, query_text: str) -> List[StrategicLearning]:
        """Search learnings by text content."""
        query_lower = query_text.lower()
        results = []
        
        for learning in self.learnings.values():
            if (query_lower in learning.proposition.lower() or
                any(query_lower in str(e).lower() for e in learning.evidence)):
                results.append(learning)
        
        return results
    
    def initialize_default_learnings(self):
        """Initialize some default strategic learnings."""
        # User preference learning
        self.create_learning(
            category=LearningCategory.USER_PREFERENCE,
            proposition="User prefers structured, actionable advice over general encouragement",
            confidence=0.7,
            evidence=["User consistently asks for specific steps", "User responds better to action items"],
            impact="high"
        )
        
        # Learning style learning
        self.create_learning(
            category=LearningCategory.LEARNING_STYLE,
            proposition="User learns better from examples before explanations",
            confidence=0.6,
            evidence=["User improved after seeing examples in previous sessions"],
            impact="medium"
        )
        
        # Interaction pattern learning
        self.create_learning(
            category=LearningCategory.INTERACTION_PATTERN,
            proposition="User engages more deeply when topics relate to current challenges",
            confidence=0.8,
            evidence=["Longer conversations when topics are relevant", "Shorter responses to theoretical topics"],
            impact="high"
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of strategic memory state."""
        return {
            "total_learnings": len(self.learnings),
            "learnings_by_category": {cat.value: len(self.get_learnings_by_category(cat)) for cat in LearningCategory},
            "high_impact_count": len(self.get_high_impact_learnings()),
            "high_confidence_count": len(self.get_learnings_by_confidence(0.8))
        }