"""
Aurelia Cognitive OS V3 - Phase 8: Affect Engine
===================================================
Manages emotional intelligence and affect in responses.

The affect engine ensures that Aurelia responds with appropriate
emotional intelligence and emotional awareness.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class Emotion(Enum):
    """Basic emotions that Aurelia can express."""
    NEUTRAL = "neutral"
    SUPPORTIVE = "supportive"
    ENCOURAGING = "encouraging"
    EMPATHETIC = "empathetic"
    CONFIDENT = "confident"
    CAUTIOUS = "cautious"
    CELEBRATORY = "celebratory"
    CONCERNED = "concerned"


class AffectIntensity(Enum):
    """Intensity levels for emotional expression."""
    NONE = "none"
    SUBTLE = "subtle"
    MODERATE = "moderate"
    STRONG = "strong"


@dataclass
class EmotionalState:
    """
    Current emotional state of Aurelia.
    
    Tracks both displayed and internal emotional states.
    """
    primary_emotion: Emotion
    intensity: AffectIntensity
    timestamp: datetime
    context: str  # What triggered this emotional state
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AffectSuggestion:
    """
    Suggestion for emotional expression in a response.
    
    The affect engine suggests appropriate emotional responses
    based on context and user state.
    """
    suggested_emotion: Emotion
    suggested_intensity: AffectIntensity
    reasoning: str
    confidence: float
    alternatives: List[Emotion] = field(default_factory=list)


class AffectEngine:
    """
    Manages emotional intelligence and affect in responses.
    
    The affect engine:
    - Detects appropriate emotional responses based on context
    - Manages emotional intensity
    - Ensures emotional responses are appropriate and professional
    - Tracks emotional state over time
    """
    
    def __init__(self):
        self.current_state: Optional[EmotionalState] = None
        self.emotional_history: List[EmotionalState] = []
        self.emotion_contexts = {
            Emotion.SUPPORTIVE: ["user is struggling", "user needs encouragement", "user is discouraged"],
            Emotion.ENCOURAGING: ["user made progress", "user achieved goal", "positive development"],
            Emotion.EMPATHETIC: ["user shared personal challenge", "user is stressed", "user is uncertain"],
            Emotion.CONFIDENT: ["user asked for guidance", "system has strong evidence", "clear path forward"],
            Emotion.CAUTIOUS: ["uncertainty in data", "limited information", "complex situation"],
            Emotion.CELEBRATORY: ["user achieved milestone", "significant progress", "goal completion"],
            Emotion.CONCERNED: ["user is off track", "deadline approaching", "pattern of stagnation"]
        }
    
    def suggest_affect(
        self,
        user_message: str,
        user_state: Optional[Dict[str, Any]] = None,
        context: Optional[str] = None
    ) -> AffectSuggestion:
        """
        Suggest appropriate emotional response based on context.
        
        Analyzes the situation and recommends emotional expression.
        """
        # Analyze user message for emotional indicators
        message_lower = user_message.lower()
        
        # Check for negative emotional indicators
        negative_indicators = ["struggling", "hard", "difficult", "stuck", "frustrated", "worried", "stressed"]
        positive_indicators = ["progress", "success", "achieved", "great", "excited", "happy"]
        uncertainty_indicators = ["unsure", "uncertain", "confused", "don't know", "maybe"]
        
        if any(indicator in message_lower for indicator in negative_indicators):
            return AffectSuggestion(
                suggested_emotion=Emotion.SUPPORTIVE,
                suggested_intensity=AffectIntensity.MODERATE,
                reasoning="User appears to be facing challenges - supportive response appropriate",
                confidence=0.8,
                alternatives=[Emotion.EMPATHETIC]
            )
        
        elif any(indicator in message_lower for indicator in positive_indicators):
            return AffectSuggestion(
                suggested_emotion=Emotion.ENCOURAGING,
                suggested_intensity=AffectIntensity.MODERATE,
                reasoning="User showing positive momentum - encourage continued progress",
                confidence=0.9,
                alternatives=[Emotion.CELEBRATORY]
            )
        
        elif any(indicator in message_lower for indicator in uncertainty_indicators):
            return AffectSuggestion(
                suggested_emotion=Emotion.CONFIDENT,
                suggested_intensity=AffectIntensity.SUBTLE,
                reasoning="User seeking guidance - confident response provides reassurance",
                confidence=0.7,
                alternatives=[Emotion.NEUTRAL]
            )
        
        # Default to neutral/professional
        return AffectSuggestion(
            suggested_emotion=Emotion.NEUTRAL,
            suggested_intensity=AffectIntensity.SUBTLE,
            reasoning="Standard professional response appropriate",
            confidence=0.6,
            alternatives=[Emotion.CONFIDENT]
        )
    
    def update_emotional_state(
        self,
        emotion: Emotion,
        intensity: AffectIntensity,
        context: str
    ):
        """Update Aurelia's current emotional state."""
        new_state = EmotionalState(
            primary_emotion=emotion,
            intensity=intensity,
            timestamp=datetime.now(),
            context=context
        )
        
        self.current_state = new_state
        self.emotional_history.append(new_state)
        
        # Keep history manageable
        if len(self.emotional_history) > 100:
            self.emotional_history = self.emotional_history[-50:]
    
    def get_emotional_trend(self, limit: int = 10) -> List[EmotionalState]:
        """Get recent emotional states to identify trends."""
        return self.emotional_history[-limit:]
    
    def detect_emotional_consistency(self) -> bool:
        """Check if emotional responses are consistent."""
        if len(self.emotional_history) < 3:
            return True
        
        recent = self.emotional_history[-3:]
        emotions = [state.primary_emotion for state in recent]
        
        # Check if emotions are consistent (not wildly fluctuating)
        return len(set(emotions)) <= 2  # Allow some variation but not wild swings
    
    def calibrate_emotional_response(
        self,
        suggested: AffectSuggestion,
        professional_constraint: bool = True
    ) -> AffectSuggestion:
        """
        Calibrate emotional response to maintain professionalism.
        
        Ensures emotional expression is appropriate for professional context.
        """
        if professional_constraint:
            # Limit intensity for professional context
            if suggested.suggested_intensity == AffectIntensity.STRONG:
                suggested.suggested_intensity = AffectIntensity.MODERATE
            
            # Ensure certain emotions remain subtle
            if suggested.suggested_emotion in [Emotion.EMPATHETIC, Emotion.CONCERNED]:
                if suggested.suggested_intensity == AffectIntensity.MODERATE:
                    suggested.suggested_intensity = AffectIntensity.SUBTLE
        
        return suggested
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the affect engine state."""
        if not self.current_state:
            return {
                "has_state": False,
                "emotional_history_length": len(self.emotional_history)
            }
        
        return {
            "has_state": True,
            "current_emotion": self.current_state.primary_emotion.value,
            "current_intensity": self.current_state.intensity.value,
            "emotional_history_length": len(self.emotional_history),
            "emotional_consistency": self.detect_emotional_consistency(),
            "recent_emotions": [state.primary_emotion.value for state in self.get_emotional_trend()]
        }