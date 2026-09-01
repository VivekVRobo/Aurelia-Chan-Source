"""
Aurelia Cognitive OS V3 - Phase 9: Metacognition Module
===================================================
Self-awareness and self-reflection capabilities.

Metacognition allows Aurelia to think about her own thinking,
assess her understanding, and improve her cognitive processes.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class MetacognitiveState(Enum):
    """States of metacognitive awareness."""
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"
    CONFUSED = "confused"
    SELF_CORRECTING = "self_correcting"
    LEARNING = "learning"


@dataclass
class CognitiveAssessment:
    """
    Assessment of Aurelia's own cognitive state.
    
    Self-assessment of understanding, confidence, and limitations.
    """
    id: str
    understanding_clarity: float  # 0-1 scale
    information_sufficiency: float  # 0-1 scale
    confidence_in_response: float  # 0-1 scale
    perceived_limitations: List[str]
    self_correction_needed: bool
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Reflection:
    """
    A reflection on cognitive process or outcome.
    
    Captures insights about how Aurelia thinks and can improve.
    """
    id: str
    reflection_type: str  # "process", "outcome", "limitation"
    content: str
    actionable_insights: List[str]
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class MetacognitionEngine:
    """
    Self-awareness and self-reflection capabilities.
    
    The metacognition engine:
    - Assesses understanding and confidence
    - Identifies limitations and knowledge gaps
    - Generates reflections on cognitive processes
    - Enables self-correction and learning
    """
    
    def __init__(self):
        self.current_assessment: Optional[CognitiveAssessment] = None
        self.reflections: List[Reflection] = []
        self.reflection_counter = 0
        self.assessment_history: List[CognitiveAssessment] = []
    
    def assess_cognitive_state(
        self,
        meaning_frame_clarity: float,
        available_evidence: List[Any],
        confidence_level: float
    ) -> CognitiveAssessment:
        """
        Assess current cognitive state.
        
        Self-assessment of understanding, confidence, and limitations.
        """
        # Calculate information sufficiency
        evidence_sufficiency = min(1.0, len(available_evidence) / 3.0)
        
        # Identify perceived limitations
        limitations = []
        
        if evidence_sufficiency < 0.5:
            limitations.append("Insufficient evidence for confident response")
        
        if meaning_frame_clarity < 0.7:
            limitations.append("Unclear understanding of user intent")
        
        if confidence_level < 0.5:
            limitations.append("Low confidence in analysis")
        
        # Determine if self-correction needed
        self_correction_needed = len(limitations) > 0
        
        assessment = CognitiveAssessment(
            id=f"assessment_{len(self.assessment_history)}",
            understanding_clarity=meaning_frame_clarity,
            information_sufficiency=evidence_sufficiency,
            confidence_in_response=confidence_level,
            perceived_limitations=limitations,
            self_correction_needed=self_correction_needed,
            timestamp=datetime.now()
        )
        
        self.current_assessment = assessment
        self.assessment_history.append(assessment)
        
        return assessment
    
    def needs_clarification(self) -> bool:
        """Check if clarification is needed from user."""
        if not self.current_assessment:
            return False
        
        return (self.current_assessment.understanding_clarity < 0.7 or
                self.current_assessment.information_sufficiency < 0.5)
    
    def generate_reflection(
        self,
        reflection_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Reflection:
        """Generate a reflection on cognitive process or outcome."""
        reflection_id = f"reflection_{self.reflection_counter}"
        
        # Extract actionable insights
        insights = self._extract_insights(content, reflection_type)
        
        reflection = Reflection(
            id=reflection_id,
            reflection_type=reflection_type,
            content=content,
            actionable_insights=insights,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.reflections.append(reflection)
        self.reflection_counter += 1
        
        return reflection
    
    def _extract_insights(self, content: str, reflection_type: str) -> List[str]:
        """Extract actionable insights from reflection content."""
        insights = []
        
        # Simple insight extraction based on keywords
        insight_keywords = {
            "process": ["improve", "better", "faster", "more accurate", "efficient"],
            "outcome": ["success", "failure", "effective", "impactful", "meaningful"],
            "limitation": ["knowledge gap", "uncertainty", "assumption", "limitation"]
        }
        
        keywords = insight_keywords.get(reflection_type, [])
        
        for keyword in keywords:
            if keyword in content.lower():
                insights.append(f"Consider improving {keyword}")
        
        if not insights:
            insights.append("Continue monitoring and self-assessment")
        
        return insights
    
    def get_current_assessment(self) -> Optional[CognitiveAssessment]:
        """Get current cognitive assessment."""
        return self.current_assessment
    
    def get_reflections_by_type(self, reflection_type: str) -> List[Reflection]:
        """Get all reflections of a specific type."""
        return [r for r in self.reflections if r.reflection_type == reflection_type]
    
    def get_recent_reflections(self, limit: int = 5) -> List[Reflection]:
        """Get recent reflections."""
        return self.reflections[-limit:]
    
    def generate_self_correction(self) -> Optional[str]:
        """Generate self-correction suggestion if needed."""
        if not self.current_assessment:
            return None
        
        if not self.current_assessment.self_correction_needed:
            return None
        
        # Generate correction based on limitations
        if "insufficient evidence" in " ".join(self.current_assessment.perceived_limitations):
            return "Request additional information or evidence from user"
        
        if "unclear understanding" in " ".join(self.current_assessment.perceived_limitations):
            return "Ask clarifying questions to better understand user intent"
        
        if "low confidence" in " ".join(self.current_assessment.perceived_limitations):
            return "Acknowledge uncertainty and provide response with appropriate caveats"
        
        return "Proceed with current understanding while noting limitations"
    
    def get_metacognitive_summary(self) -> Dict[str, Any]:
        """Get a summary of metacognitive state."""
        if not self.current_assessment:
            return {
                "has_assessment": False,
                "total_reflections": len(self.reflections)
            }
        
        return {
            "has_assessment": True,
            "understanding_clarity": self.current_assessment.understanding_clarity,
            "information_sufficiency": self.current_assessment.information_sufficiency,
            "confidence_in_response": self.current_assessment.confidence_in_response,
            "limitation_count": len(self.current_assessment.perceived_limitations),
            "needs_clarification": self.needs_clarification(),
            "total_reflections": len(self.reflections),
            "reflection_types": {rt: len(self.get_reflections_by_type(rt)) for rt in ["process", "outcome", "limitation"]}
        }