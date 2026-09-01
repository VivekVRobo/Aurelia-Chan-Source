"""
Aurelia Cognitive OS V3 - Phase 8: Persona Renderer
=================================================
Integrates character intelligence into final responses.

The persona renderer combines affect, expression policy, and
Aurelia state to create character-driven natural language responses.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from aurelia.character.affect_engine import AffectEngine, Emotion, AffectIntensity, AffectSuggestion
from aurelia.character.expression_policy import ExpressionPolicyManager, ExpressionStyle, ExpressionPolicy
from aurelia.character.aurelia_state import AureliaStateManager, AureliaMode, PersonalityTrait
from aurelia.llm.response_renderer import RenderedResponse


@dataclass
class PersonaRenderedResponse:
    """
    Final response with full character intelligence applied.
    
    Integrates affect, expression policy, and Aurelia state.
    """
    content: str
    emotion: Emotion
    emotion_intensity: AffectIntensity
    expression_style: ExpressionStyle
    mode: str
    traits: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class PersonaRenderer:
    """
    Integrates character intelligence into final responses.
    
    The persona renderer:
    - Combines affect, expression policy, and state
    - Applies character traits to responses
    - Ensures consistent character expression
    - Balances emotional intelligence with professionalism
    """
    
    def __init__(self):
        self.affect_engine = AffectEngine()
        self.expression_manager = ExpressionPolicyManager()
        self.state_manager = AureliaStateManager()
        
        # Initialize state
        self.state_manager.initialize_state()
    
    def render_with_persona(
        self,
        base_response: RenderedResponse,
        user_message: str,
        context: Optional[str] = None
    ) -> PersonaRenderedResponse:
        """
        Render response with full character intelligence.
        
        Integrates affect, expression policy, and Aurelia state.
        """
        # Determine appropriate affect
        affect_suggestion = self.affect_engine.suggest_affect(
            user_message=user_message,
            context=context or "standard interaction"
        )
        
        # Calibrate affect for professionalism
        calibrated_affect = self.affect_engine.calibrate_emotional_response(
            affect_suggestion,
            professional_constraint=True
        )
        
        # Update Aurelia's emotional state
        self.affect_engine.update_emotional_state(
            emotion=calibrated_affect.suggested_emotion,
            intensity=calibrated_affect.suggested_intensity,
            context=context or "response generation"
        )
        
        # Adapt expression policy for context
        adapted_policy = self.expression_manager.adapt_for_context(
            context or "standard interaction"
        )
        
        # Determine appropriate mode
        suggested_mode = self.state_manager.get_mode_for_context(
            context or "standard interaction"
        )
        
        # Update Aurelia's mode
        self.state_manager.update_mode(
            mode=suggested_mode,
            context=context or "response generation"
        )
        
        # Apply expression policy to base response
        compliance = self.expression_manager.check_compliance(base_response.content)
        
        if not compliance["compliant"]:
            # Apply improvements
            improvements = self.expression_manager.suggest_improvements(base_response.content)
            # In full system, would actually apply improvements
            # For now, just note the issues
        
        # Apply emotional expression to response
        characterized_content = self._apply_emotional_expression(
            base_response.content,
            calibrated_affect.suggested_emotion,
            calibrated_affect.suggested_intensity
        )
        
        # Apply expression style
        styled_content = self._apply_expression_style(
            characterized_content,
            adapted_policy.style
        )
        
        # Get current traits
        active_traits = self.state_manager.get_active_traits()
        
        return PersonaRenderedResponse(
            content=styled_content,
            emotion=calibrated_affect.suggested_emotion,
            emotion_intensity=calibrated_affect.suggested_intensity,
            expression_style=adapted_policy.style,
            mode=suggested_mode.value,
            traits=[t.value for t in active_traits],
            metadata={
                "affect_reasoning": calibrated_affect.reasoning,
                "compliance_score": compliance["compliance_score"],
                "affect_confidence": calibrated_affect.confidence
            }
        )
    
    def _apply_emotional_expression(
        self,
        content: str,
        emotion: Emotion,
        intensity: AffectIntensity
    ) -> str:
        """Apply emotional expression to response content."""
        if intensity == AffectIntensity.NONE:
            return content
        
        # Add emotional expressions based on type and intensity
        emotional_prefixes = {
            Emotion.SUPPORTIVE: {
                AffectIntensity.SUBTLE: "I understand.",
                AffectIntensity.MODERATE: "I understand this is challenging.",
                AffectIntensity.STRONG: "I understand this is quite challenging, and I'm here to support you."
            },
            Emotion.ENCOURAGING: {
                AffectIntensity.SUBTLE: "Good progress.",
                AffectIntensity.MODERATE: "You're making good progress.",
                AffectIntensity.STRONG: "You're making excellent progress - keep building on this momentum."
            },
            Emotion.EMPATHETIC: {
                AffectIntensity.SUBTLE: "I appreciate your situation.",
                AffectIntensity.MODERATE: "I understand this situation is meaningful to you.",
                AffectIntensity.STRONG: "I understand this situation is deeply meaningful to you, and I'm committed to helping you navigate it."
            },
            Emotion.CONFIDENT: {
                AffectIntensity.SUBTLE: "I'm confident in this approach.",
                AffectIntensity.MODERATE: "I'm confident this approach will serve you well.",
                AffectIntensity.STRONG: "I'm strongly confident this approach will serve you well based on the evidence."
            },
            Emotion.CAUTIOUS: {
                AffectIntensity.SUBTLE: "Let's proceed carefully.",
                AffectIntensity.MODERATE: "Let's proceed with appropriate consideration.",
                AffectIntensity.STRONG: "Let's proceed with careful consideration of all factors involved."
            }
        }
        
        # Get appropriate prefix
        prefixes = emotional_prefixes.get(emotion, {})
        prefix = prefixes.get(intensity, "")
        
        if prefix:
            return f"{prefix}\n\n{content}"
        
        return content
    
    def _apply_expression_style(self, content: str, style: ExpressionStyle) -> str:
        """Apply expression style to response content."""
        if style == ExpressionStyle.FORMAL:
            # Add formal language markers
            content = content.replace("you're", "you are")
            content = content.replace("don't", "do not")
            content = content.replace("can't", "cannot")
        
        elif style == ExpressionStyle.CONVERSATIONAL:
            # Add conversational markers
            if not content.endswith(("!", "?", ".")):
                content += "."
        
        elif style == ExpressionStyle.MENTORIAL:
            # Add mentorial tone
            if not any(word in content.lower() for word in ["you", "your"]):
                content = "For you, " + content[0].lower() + content[1:]
        
        return content
    
    def adjust_engagement(self, level: float):
        """Adjust Aurelia's engagement level."""
        self.state_manager.update_engagement(level)
    
    def get_character_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of Aurelia's character state."""
        affect_summary = self.affect_engine.get_summary()
        expression_summary = self.expression_manager.get_summary()
        state_summary = self.state_manager.get_summary()
        
        return {
            "affect": affect_summary,
            "expression": expression_summary,
            "state": state_summary,
            "character_description": self.state_manager.get_character_description()
        }
    
    def get_voice_profile(self) -> str:
        """Get Aurelia's current voice profile description."""
        if not self.state_manager.current_state:
            return "Aurelia: Executive Career Mentor"
        
        return f"""
Aurelia Voice Profile:
- Mode: {self.state_manager.current_state.current_mode.value}
- Active Traits: {', '.join([t.value for t in self.state_manager.current_state.active_traits])}
- Engagement: {self.state_manager.current_state.engagement_level:.0%}
- Current Mood: {self.state_manager.current_state.mood}
- Expression Style: {self.expression_manager.current_policy.style.value}
- Current Emotion: {self.affect_engine.current_state.primary_emotion.value if self.affect_engine.current_state else 'None'}
        """.strip()