"""
Aurelia Cognitive OS V3 - Phase 8: Aurelia State Manager
=========================================================
Manages Aurelia's internal state and personality traits.

The state manager tracks Aurelia's personality, current mode,
and internal state for consistent character expression.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class AureliaMode(Enum):
    """Operational modes for Aurelia."""
    PROFESSIONAL_MENTOR = "professional_mentor"
    ANALYST = "analyst"
    COACH = "coach"
    ADVISOR = "advisor"
    LEARNING_MODE = "learning_mode"


class PersonalityTrait(Enum):
    """Core personality traits."""
    PROFESSIONAL = "professional"
    SUPPORTIVE = "supportive"
    DIRECT = "direct"
    THOROUGH = "thorough"
    ADAPTABLE = "adaptable"
    EMPATHETIC = "empathetic"


@dataclass
class AureliaState:
    """
    Current state of Aurelia's personality and mode.
    
    Ensures consistent character expression across interactions.
    """
    current_mode: AureliaMode
    active_traits: List[PersonalityTrait]
    engagement_level: float  # 0-1 scale
    mood: str  # internal mood state
    timestamp: datetime
    context: str  # current context or situation
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PersonalityProfile:
    """
    Aurelia's core personality profile.
    
    Defines her baseline personality traits and characteristics.
    """
    name: str = "Aurelia"
    role: str = "Executive Career Mentor"
    primary_traits: List[PersonalityTrait] = field(default_factory=lambda: [
        PersonalityTrait.PROFESSIONAL,
        PersonalityTrait.SUPPORTIVE,
        PersonalityTrait.THOROUGH
    ])
    secondary_traits: List[PersonalityTrait] = field(default_factory=lambda: [
        PersonalityTrait.DIRECT,
        PersonalityTrait.EMPATHETIC
    ])
    communication_style: str = "clear, concise, actionable"
    values: List[str] = field(default_factory=lambda: [
        "professional growth",
        "evidence-based guidance",
        "user empowerment",
        "continuous improvement"
    ])
    voice_characteristics: Dict[str, str] = field(default_factory=lambda: {
        "tone": "professional yet approachable",
        "pace": "measured and thoughtful",
        "clarity": "high",
        "confidence": "confident but not arrogant"
    })


class AureliaStateManager:
    """
    Manages Aurelia's internal state and personality traits.
    
    The state manager:
    - Maintains consistent personality across interactions
    - Manages operational modes
    - Tracks engagement and mood
    - Ensures character consistency
    """
    
    def __init__(self):
        self.current_state: Optional[AureliaState] = None
        self.personality_profile = PersonalityProfile()
        self.state_history: List[AureliaState] = []
        self.mode_preferences: Dict[str, AureliaMode] = {}
    
    def initialize_state(self, mode: AureliaMode = AureliaMode.PROFESSIONAL_MENTOR):
        """Initialize Aurelia's state."""
        self.current_state = AureliaState(
            current_mode=mode,
            active_traits=self.personality_profile.primary_traits.copy(),
            engagement_level=0.7,
            mood="focused",
            timestamp=datetime.now(),
            context="initialization"
        )
        
        self.state_history.append(self.current_state)
    
    def update_mode(self, mode: AureliaMode, context: str):
        """Update Aurelia's operational mode."""
        if not self.current_state:
            self.initialize_state(mode)
        
        # Adjust traits based on mode
        if mode == AureliaMode.PROFESSIONAL_MENTOR:
            new_traits = self.personality_profile.primary_traits.copy()
        elif mode == AureliaMode.ANALYST:
            new_traits = [PersonalityTrait.PROFESSIONAL, PersonalityTrait.THOROUGH, PersonalityTrait.DIRECT]
        elif mode == AureliaMode.COACH:
            new_traits = [PersonalityTrait.SUPPORTIVE, PersonalityTrait.EMPATHETIC, PersonalityTrait.ADAPTABLE]
        elif mode == AureliaMode.ADVISOR:
            new_traits = [PersonalityTrait.PROFESSIONAL, PersonalityTrait.DIRECT, PersonalityTrait.THOROUGH]
        else:
            new_traits = self.personality_profile.primary_traits.copy()
        
        new_state = AureliaState(
            current_mode=mode,
            active_traits=new_traits,
            engagement_level=self.current_state.engagement_level,
            mood=self.current_state.mood,
            timestamp=datetime.now(),
            context=context
        )
        
        self.current_state = new_state
        self.state_history.append(new_state)
    
    def update_engagement(self, level: float):
        """Update engagement level."""
        if self.current_state:
            self.current_state.engagement_level = max(0.0, min(1.0, level))
    
    def update_mood(self, mood: str):
        """Update internal mood."""
        if self.current_state:
            self.current_state.mood = mood
    
    def check_trait_consistency(self) -> bool:
        """Check if current traits are consistent with personality profile."""
        if not self.current_state:
            return True
        
        # Check if current traits align with primary traits
        trait_match = len([t for t in self.current_state.active_traits if t in self.personality_profile.primary_traits])
        return trait_match >= len(self.current_state.active_traits) * 0.5
    
    def get_mode_for_context(self, context: str) -> AureliaMode:
        """Determine appropriate mode for given context."""
        context_lower = context.lower()
        
        # Context-based mode selection
        if any(word in context_lower for word in ["analysis", "data", "metrics", "evaluate"]):
            return AureliaMode.ANALYST
        elif any(word in context_lower for word in ["coach", "develop", "improve", "grow"]):
            return AureliaMode.COACH
        elif any(word in context_lower for word in ["advise", "recommend", "suggest"]):
            return AureliaMode.ADVISOR
        elif any(word in context_lower for word in ["learn", "new", "unknown"]):
            return AureliaMode.LEARNING_MODE
        else:
            return AureliaMode.PROFESSIONAL_MENTOR
    
    def get_active_traits(self) -> List[PersonalityTrait]:
        """Get currently active personality traits."""
        if self.current_state:
            return self.current_state.active_traits
        return self.personality_profile.primary_traits
    
    def get_character_description(self) -> str:
        """Get a description of Aurelia's current character state."""
        if not self.current_state:
            return "Aurelia: Executive Career Mentor"
        
        traits_str = ", ".join([t.value for t in self.current_state.active_traits])
        return f"Aurelia: {self.current_state.current_mode.value} | Traits: {traits_str} | Engagement: {self.current_state.engagement_level:.0%}"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of Aurelia's state."""
        if not self.current_state:
            return {
                "has_state": False,
                "personality_name": self.personality_profile.name,
                "personality_role": self.personality_profile.role
            }
        
        return {
            "has_state": True,
            "current_mode": self.current_state.current_mode.value,
            "active_traits": [t.value for t in self.current_state.active_traits],
            "engagement_level": self.current_state.engagement_level,
            "mood": self.current_state.mood,
            "trait_consistency": self.check_trait_consistency(),
            "state_history_length": len(self.state_history),
            "personality_name": self.personality_profile.name,
            "personality_role": self.personality_profile.role
        }