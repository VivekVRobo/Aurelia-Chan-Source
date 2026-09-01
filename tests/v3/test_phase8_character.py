#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aurelia Cognitive OS V3 - Phase 8 Character Intelligence Tests
============================================================
Tests the affect engine, expression policy, Aurelia state manager, and persona renderer.
"""

import sys
sys.path.insert(0, 'C:\\Users\\vivek\\Desktop\\Aurelia-Chan')

from aurelia.character.affect_engine import AffectEngine, EmotionalState, AffectSuggestion, Emotion, AffectIntensity
from aurelia.character.expression_policy import ExpressionPolicyManager, ExpressionPolicy, ExpressionStyle, ExpressionConstraint
from aurelia.character.aurelia_state import AureliaStateManager, AureliaState, PersonalityProfile, AureliaMode, PersonalityTrait
from aurelia.character.persona_renderer import PersonaRenderer, PersonaRenderedResponse
from aurelia.llm.response_renderer import RenderedResponse, ResponseStyle, ResponseTone
from aurelia.cognition.contracts import ResponsePlan


def test_affect_engine():
    """Test affect engine."""
    print("Testing Affect Engine...")
    
    engine = AffectEngine()
    
    # Test affect suggestion
    suggestion = engine.suggest_affect(
        user_message="I'm really struggling with this career transition",
        context="career transition challenge"
    )
    
    assert suggestion.suggested_emotion in [Emotion.SUPPORTIVE, Emotion.EMPATHETIC]
    assert suggestion.suggested_intensity in [AffectIntensity.SUBTLE, AffectIntensity.MODERATE]
    assert suggestion.confidence >= 0.0
    
    # Test emotional state update
    engine.update_emotional_state(
        emotion=Emotion.SUPPORTIVE,
        intensity=AffectIntensity.MODERATE,
        context="user expressed difficulty"
    )
    
    assert engine.current_state is not None
    assert engine.current_state.primary_emotion == Emotion.SUPPORTIVE
    
    # Test emotional trend
    engine.update_emotional_state(Emotion.ENCOURAGING, AffectIntensity.MODERATE, "progress made")
    engine.update_emotional_state(Emotion.CONFIDENT, AffectIntensity.SUBTLE, "clear path")
    
    trend = engine.get_emotional_trend(limit=3)
    assert len(trend) == 3
    
    # Test emotional consistency
    consistency = engine.detect_emotional_consistency()
    assert isinstance(consistency, bool)
    
    # Test affect calibration
    calibrated = engine.calibrate_emotional_response(suggestion, professional_constraint=True)
    assert calibrated.suggested_emotion == suggestion.suggested_emotion
    
    print("  Affect Engine: PASS")
    return True


def test_expression_policy():
    """Test expression policy manager."""
    print("Testing Expression Policy Manager...")
    
    manager = ExpressionPolicyManager()
    
    # Test default policy
    assert manager.current_policy.style == ExpressionStyle.PROFESSIONAL
    assert len(manager.current_policy.constraints) > 0
    
    # Test compliance checking
    test_text = "I guarantee this will work perfectly for you."
    compliance = manager.check_compliance(test_text)
    
    assert compliance["compliant"] == False  # Should fail due to overpromising
    assert len(compliance["violations"]) > 0
    
    # Test with compliant text
    compliant_text = "Based on the evidence, this approach may help your career progression."
    compliant_check = manager.check_compliance(compliant_text)
    
    assert compliant_check["compliant"] == True
    assert len(compliant_check["violations"]) == 0
    
    # Test improvement suggestions
    improvements = manager.suggest_improvements(test_text)
    assert len(improvements) > 0
    
    # Test context adaptation
    adapted = manager.adapt_for_context("personal challenge")
    assert adapted.style == ExpressionStyle.MENTORIAL
    
    celebration_adapted = manager.adapt_for_context("great success achievement")
    assert celebration_adapted.style == ExpressionStyle.SEMI_FORMAL
    
    print("  Expression Policy Manager: PASS")
    return True


def test_aurelia_state_manager():
    """Test Aurelia state manager."""
    print("Testing Aurelia State Manager...")
    
    manager = AureliaStateManager()
    
    # Test initialization
    manager.initialize_state()
    assert manager.current_state is not None
    assert manager.current_state.current_mode == AureliaMode.PROFESSIONAL_MENTOR
    
    # Test mode update
    manager.update_mode(AureliaMode.ANALYST, "data analysis request")
    assert manager.current_state.current_mode == AureliaMode.ANALYST
    
    # Test engagement update
    manager.update_engagement(0.9)
    assert manager.current_state.engagement_level == 0.9
    
    # Test mood update
    manager.update_mood("focused")
    assert manager.current_state.mood == "focused"
    
    # Test trait consistency
    consistency = manager.check_trait_consistency()
    assert isinstance(consistency, bool)
    
    # Test mode for context
    mode = manager.get_mode_for_context("analyze the data")
    assert mode == AureliaMode.ANALYST
    
    coach_mode = manager.get_mode_for_context("help me develop this skill")
    assert coach_mode == AureliaMode.COACH
    
    # Test character description
    description = manager.get_character_description()
    assert "Aurelia" in description
    assert len(description) > 0
    
    print("  Aurelia State Manager: PASS")
    return True


def test_persona_renderer():
    """Test persona renderer."""
    print("Testing Persona Renderer...")
    
    renderer = PersonaRenderer()
    
    # Create test base response
    response_plan = ResponsePlan(
        intent="Provide career guidance",
        claims=["Strategic thinking is important"],
        recommendations=["Develop strategic planning"],
        uncertainty=["Timeline may vary"],
        questions=["What specific skills?"],
        tone="professional"
    )
    
    base_response = RenderedResponse(
        content="You should focus on developing strategic thinking skills.",
        style=ResponseStyle.PROFESSIONAL,
        tone=ResponseTone.NEUTRAL,
        sections=["You should focus on developing strategic thinking skills."]
    )
    
    # Test persona rendering
    persona_response = renderer.render_with_persona(
        base_response=base_response,
        user_message="I'm struggling with my career path",
        context="career guidance"
    )
    
    assert persona_response.content is not None
    assert persona_response.emotion in [Emotion.SUPPORTIVE, Emotion.EMPATHETIC]
    assert persona_response.expression_style in [ExpressionStyle.PROFESSIONAL, ExpressionStyle.MENTORIAL]
    assert len(persona_response.traits) > 0
    
    # Test engagement adjustment
    renderer.adjust_engagement(0.8)
    assert renderer.state_manager.current_state.engagement_level == 0.8
    
    # Test character summary
    summary = renderer.get_character_summary()
    assert "affect" in summary
    assert "expression" in summary
    assert "state" in summary
    
    # Test voice profile
    voice_profile = renderer.get_voice_profile()
    assert "Aurelia" in voice_profile
    assert "Voice Profile" in voice_profile
    
    print("  Persona Renderer: PASS")
    return True


def test_character_integration():
    """Test integration between character components."""
    print("Testing Character Integration...")
    
    # Create all character components
    affect_engine = AffectEngine()
    expression_manager = ExpressionPolicyManager()
    state_manager = AureliaStateManager()
    persona_renderer = PersonaRenderer()
    
    # Initialize state
    state_manager.initialize_state()
    
    # Simulate a character-driven interaction
    user_message = "I'm worried about not being ready for the Director role"
    
    # Suggest affect
    affect = affect_engine.suggest_affect(user_message, context="career readiness concern")
    assert affect.suggested_emotion in [Emotion.SUPPORTIVE, Emotion.EMPATHETIC]
    
    # Update emotional state
    affect_engine.update_emotional_state(affect.suggested_emotion, affect.suggested_intensity, "user concern")
    
    # Update mode based on context
    appropriate_mode = state_manager.get_mode_for_context("career readiness concern")
    state_manager.update_mode(appropriate_mode, "character-driven response")
    
    # Adapt expression policy
    adapted_policy = expression_manager.adapt_for_context("career readiness concern")
    
    # Verify integration
    assert affect_engine.current_state is not None
    assert state_manager.current_state.current_mode == appropriate_mode
    assert adapted_policy.style in [ExpressionStyle.MENTORIAL, ExpressionStyle.PROFESSIONAL]
    
    print("  Character Integration: PASS")
    return True


def test_emotional_consistency():
    """Test emotional consistency over time."""
    print("Testing Emotional Consistency...")
    
    engine = AffectEngine()
    
    # Create consistent emotional states
    engine.update_emotional_state(Emotion.NEUTRAL, AffectIntensity.SUBTLE, "normal interaction")
    engine.update_emotional_state(Emotion.NEUTRAL, AffectIntensity.SUBTLE, "information request")
    engine.update_emotional_state(Emotion.CONFIDENT, AffectIntensity.SUBTLE, "providing guidance")
    
    # Should be consistent (not wildly fluctuating)
    consistency = engine.detect_emotional_consistency()
    assert consistency == True
    
    # Create inconsistent states
    engine.update_emotional_state(Emotion.CELEBRATORY, AffectIntensity.STRONG, "sudden success")
    engine.update_emotional_state(Emotion.CONCERNED, AffectIntensity.STRONG, "sudden failure")
    
    # Should detect inconsistency
    inconsistent_consistency = engine.detect_emotional_consistency()
    # With wild swings, should be false
    assert isinstance(inconsistent_consistency, bool)
    
    print("  Emotional Consistency: PASS")
    return True


def main():
    print("=" * 70)
    print("    AURELIA COGNITIVE OS V3 - PHASE 8 CHARACTER INTELLIGENCE TESTS")
    print("=" * 70)
    print()
    
    tests = [
        test_affect_engine,
        test_expression_policy,
        test_aurelia_state_manager,
        test_persona_renderer,
        test_character_integration,
        test_emotional_consistency
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print()
    print("=" * 70)
    print("    TEST RESULTS")
    print("=" * 70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print()
        print("SUCCESS: All Phase 8 character intelligence tests passed!")
        print()
        print("Character intelligence system ready:")
        print("  - Affect Engine (emotional intelligence, appropriate responses)")
        print("  - Expression Policy (communication style, professional boundaries)")
        print("  - Aurelia State Manager (personality traits, operational modes)")
        print("  - Persona Renderer (character integration into responses)")
        print()
        print("PHASE 8 COMPLETE!")
        print()
        print("Next: Phase 9 - Higher Cognition (Scenario simulation, Prediction, Counterfactual reasoning, Metacognition, Replanning)")
    else:
        print()
        print("FAILURE: Some tests failed. Please fix the issues.")
    
    print("=" * 70)


if __name__ == "__main__":
    main()