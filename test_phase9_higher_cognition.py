"""
Aurelia Cognitive OS V3 - Phase 9: Higher Cognition Tests
======================================================
Tests for advanced cognitive capabilities.
"""

import sys
sys.path.insert(0, '.')

from aurelia.cognition.scenario_simulation import (
    ScenarioSimulator,
    ScenarioType,
    ScenarioStatus
)
from aurelia.cognition.prediction_engine import (
    PredictionEngine,
    PredictionType,
    PredictionConfidence
)
from aurelia.cognition.counterfactual_reasoning import (
    CounterfactualReasoner,
    CounterfactualType
)
from aurelia.cognition.metacognition import (
    MetacognitionEngine,
    MetacognitiveState
)
from aurelia.cognition.replanning_engine import (
    ReplanningEngine,
    ReplanningTrigger,
    ReplanningStrategy
)


def test_scenario_simulation():
    """Test scenario simulation capabilities."""
    print("Testing Scenario Simulation...")
    
    simulator = ScenarioSimulator()
    
    # Create a career path scenario
    scenario = simulator.create_scenario(
        scenario_type=ScenarioType.CAREER_PATH,
        description="Path to Director level in 2 years",
        parameters={
            "skill_level": 0.75,
            "market_conditions": "favorable",
            "management_experience": "moderate"
        },
        assumptions=["Continuous learning", "Internal opportunities available"]
    )
    
    assert scenario.id == "scenario_0"
    assert scenario.scenario_type == ScenarioType.CAREER_PATH
    assert len(scenario.assumptions) == 2
    
    # Simulate the scenario
    result = simulator.simulate_scenario(scenario.id)
    
    assert result.scenario_id == scenario.id
    assert len(result.outcomes) > 0
    assert 0 <= result.probability <= 1
    assert 0 <= result.confidence <= 1
    assert isinstance(result.risks, list)
    assert isinstance(result.benefits, list)
    assert result.recommendation
    
    # Simulate with parameter variations
    result = simulator.simulate_scenario(
        scenario.id,
        parameter_variations={
            "skill_level": [0.6, 0.8, 0.9]
        }
    )
    
    assert len(result.outcomes) > 1  # Should have multiple outcomes
    
    # Get summary
    summary = simulator.get_summary()
    assert summary["total_scenarios"] == 1
    assert summary["total_simulations"] == 2
    
    print("  Scenario Simulation: PASS")
    return True


def test_prediction_engine():
    """Test prediction engine capabilities."""
    print("Testing Prediction Engine...")
    
    engine = PredictionEngine()
    
    # Test career progression prediction
    prediction = engine.predict_career_progression(
        current_role="Senior Manager",
        target_role="Director",
        current_skills={"leadership": 0.8, "strategy": 0.7, "communication": 0.9},
        time_horizon="2 years"
    )
    
    assert prediction.prediction_type == PredictionType.CAREER_PROGRESSION
    assert 0 <= prediction.predicted_value <= 1
    assert prediction.confidence_level in [PredictionConfidence.HIGH, PredictionConfidence.MEDIUM, PredictionConfidence.LOW]
    assert len(prediction.factors) > 0
    
    # Test skill acquisition prediction
    prediction = engine.predict_skill_acquisition(
        skill_name="Python",
        current_level=0.3,
        target_level=0.8,
        time_available="6 months",
        learning_intensity="high"
    )
    
    assert prediction.prediction_type == PredictionType.SKILL_ACQUISITION
    assert 0 <= prediction.predicted_value <= 1
    
    # Test goal achievement prediction
    prediction = engine.predict_goal_achievement(
        goal_description="Complete executive training program",
        current_progress=0.4,
        remaining_time="3 months",
        resource_availability="adequate"
    )
    
    assert prediction.prediction_type == PredictionType.GOAL_ACHIEVEMENT
    assert 0 <= prediction.predicted_value <= 1
    
    # Record accuracy
    engine.record_accuracy(prediction.id, actual_value=0.8)
    
    # Get summary
    summary = engine.get_summary()
    assert summary["total_predictions"] == 3
    assert summary["accuracy_records"] == 1
    
    print("  Prediction Engine: PASS")
    return True


def test_counterfactual_reasoning():
    """Test counterfactual reasoning capabilities."""
    print("Testing Counterfactual Reasoning...")
    
    reasoner = CounterfactualReasoner()
    
    # Create a counterfactual
    counterfactual = reasoner.create_counterfactual(
        counterfactual_type=CounterfactualType.WHAT_IF,
        original_situation="Currently at Senior Manager level",
        counterfactual_situation="Already at Director level",
        premise="What if I had taken the opportunity 2 years ago?",
        assumptions=["Earlier management experience", "Same skill development"]
    )
    
    assert counterfactual.id == "counterfactual_0"
    assert counterfactual.counterfactual_type == CounterfactualType.WHAT_IF
    assert 0 <= counterfactual.plausibility <= 1
    
    # Analyze the counterfactual
    analysis = reasoner.analyze_counterfactual(counterfactual.id)
    
    assert analysis.counterfactual_id == counterfactual.id
    assert isinstance(analysis.is_plausible, bool)
    assert 0 <= analysis.plausibility_score <= 1
    assert isinstance(analysis.required_changes, list)
    assert analysis.likelihood_estimate
    assert 0 <= analysis.confidence <= 1
    
    # Get summary
    summary = reasoner.get_summary()
    assert summary["total_counterfactuals"] == 1
    assert summary["total_analyses"] == 1
    
    print("  Counterfactual Reasoning: PASS")
    return True


def test_metacognition():
    """Test metacognition capabilities."""
    print("Testing Metacognition...")
    
    engine = MetacognitionEngine()
    
    # Assess cognitive state
    assessment = engine.assess_cognitive_state(
        meaning_frame_clarity=0.8,
        available_evidence=["fact1", "fact2"],
        confidence_level=0.7
    )
    
    assert assessment.understanding_clarity == 0.8
    assert assessment.information_sufficiency >= 0
    assert assessment.confidence_in_response == 0.7
    assert isinstance(assessment.perceived_limitations, list)
    assert isinstance(assessment.self_correction_needed, bool)
    
    # Check if clarification needed
    needs_clarification = engine.needs_clarification()
    assert isinstance(needs_clarification, bool)
    
    # Generate reflection
    reflection = engine.generate_reflection(
        reflection_type="process",
        content="The analysis process was thorough but could be more efficient",
        metadata={"context": "career planning"}
    )
    
    assert reflection.reflection_type == "process"
    assert reflection.content
    assert isinstance(reflection.actionable_insights, list)
    
    # Get self-correction
    self_correction = engine.generate_self_correction()
    if self_correction:
        assert isinstance(self_correction, str)
    
    # Get summary
    summary = engine.get_metacognitive_summary()
    assert summary["has_assessment"] == True
    assert summary["total_reflections"] == 1
    
    print("  Metacognition: PASS")
    return True


def test_replanning_engine():
    """Test replanning engine capabilities."""
    print("Testing Replanning Engine...")
    
    engine = ReplanningEngine()
    
    # Detect replanning need
    trigger = engine.detect_replanning_need(
        plan_id="plan_0",
        execution_status="failed",
        obstacles=["budget constraints"],
        deadline_status="on_track"
    )
    
    assert trigger == ReplanningTrigger.PLAN_FAILURE
    
    # Determine strategy
    strategy = engine.determine_replanning_strategy(
        trigger=trigger,
        context={"obstacle_severity": "major"}
    )
    
    assert strategy == ReplanningStrategy.CHANGE_APPROACH
    
    # Generate replanning actions
    actions = engine.generate_replanning_actions(
        strategy=strategy,
        plan_id="plan_0",
        context={"obstacle_severity": "major"}
    )
    
    assert len(actions) > 0
    assert actions[0].action_type == strategy
    
    # Execute replanning
    result = engine.execute_replanning(
        plan_id="plan_0",
        trigger=trigger,
        context={"obstacle_severity": "major"}
    )
    
    assert result.original_plan_id == "plan_0"
    assert result.trigger == trigger
    assert len(result.actions) > 0
    assert result.new_plan_id
    assert result.success == True
    assert 0 <= result.confidence <= 1
    assert result.rationale
    
    # Get summary
    summary = engine.get_summary()
    assert summary["total_replans"] == 1
    assert summary["successful_replans"] == 1
    
    print("  Replanning Engine: PASS")
    return True


def test_higher_cognition_integration():
    """Test integration of higher cognition components."""
    print("Testing Higher Cognition Integration...")
    
    # Scenario simulation + prediction
    simulator = ScenarioSimulator()
    predictor = PredictionEngine()
    
    scenario = simulator.create_scenario(
        scenario_type=ScenarioType.CAREER_PATH,
        description="Career progression scenario",
        parameters={"skill_level": 0.7, "market_conditions": "favorable"},
        assumptions=["Continuous growth"]
    )
    
    simulation_result = simulator.simulate_scenario(scenario.id)
    prediction = predictor.predict_career_progression(
        current_role="Manager",
        target_role="Director",
        current_skills={"leadership": 0.7},
        time_horizon="2 years"
    )
    
    # Both should provide probability estimates
    assert 0 <= simulation_result.probability <= 1
    assert 0 <= prediction.predicted_value <= 1
    
    # Metacognition + replanning
    metacognition = MetacognitionEngine()
    replanner = ReplanningEngine()
    
    assessment = metacognition.assess_cognitive_state(
        meaning_frame_clarity=0.6,
        available_evidence=["fact1"],
        confidence_level=0.5
    )
    
    if assessment.self_correction_needed:
        trigger = replanner.detect_replanning_need(
            plan_id="plan_0",
            execution_status="on_track",
            obstacles=[],
            deadline_status="on_track"
        )
        # No trigger should be detected in this case
        assert trigger is None
    
    print("  Higher Cognition Integration: PASS")
    return True


def test():
    """Run all Phase 9 tests."""
    print("=" * 70)
    print("    AURELIA COGNITIVE OS V3 - PHASE 9 HIGHER COGNITION TESTS")
    print("=" * 70)
    print()
    
    tests = [
        test_scenario_simulation,
        test_prediction_engine,
        test_counterfactual_reasoning,
        test_metacognition,
        test_replanning_engine,
        test_higher_cognition_integration
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1
    
    print()
    print("=" * 70)
    print("    TEST RESULTS")
    print("=" * 70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    print()
    
    if failed == 0:
        print("SUCCESS: All Phase 9 higher cognition tests passed!")
        print()
        print("Higher cognition system ready:")
        print("  - Scenario Simulation (what-if scenarios, outcome prediction)")
        print("  - Prediction Engine (career progression, skill acquisition, goal achievement)")
        print("  - Counterfactual Reasoning (alternative possibilities, causality testing)")
        print("  - Metacognition (self-awareness, self-reflection, self-correction)")
        print("  - Replanning Engine (dynamic plan adjustment, obstacle handling)")
        print()
        print("PHASE 9 COMPLETE!")
        print()
        print("Next: Phase 10 - Learning (Memory consolidation, Calibration, User-specific models, Feedback learning)")
        print("=" * 70)
        return True
    else:
        print("FAILURE: Some tests failed. Please fix the issues.")
        print("=" * 70)
        return False


if __name__ == "__main__":
    success = test()
    sys.exit(0 if success else 1)