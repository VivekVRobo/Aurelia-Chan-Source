"""Character intelligence module."""
from .affect_engine import AffectEngine, EmotionalState, AffectSuggestion, Emotion, AffectIntensity
from .expression_policy import ExpressionPolicyManager, ExpressionPolicy, ExpressionStyle, ExpressionConstraint
from .aurelia_state import AureliaStateManager, AureliaState, PersonalityProfile, AureliaMode, PersonalityTrait
from .persona_renderer import PersonaRenderer, PersonaRenderedResponse
__all__ = ['AffectEngine', 'EmotionalState', 'AffectSuggestion', 'Emotion', 'AffectIntensity', 'ExpressionPolicyManager', 'ExpressionPolicy', 'ExpressionStyle', 'ExpressionConstraint', 'AureliaStateManager', 'AureliaState', 'PersonalityProfile', 'AureliaMode', 'PersonalityTrait', 'PersonaRenderer', 'PersonaRenderedResponse']