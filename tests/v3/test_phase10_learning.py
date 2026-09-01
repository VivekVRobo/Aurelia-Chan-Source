"""
Aurelia Cognitive OS V3 - Phase 10: Learning Tests
================================================
Tests for learning capabilities.
"""

import sys
sys.path.insert(0, '.')

from aurelia.learning.memory_consolidation import (
    MemoryConsolidator,
    ConsolidationType,
    ConsolidationPriority
)
from aurelia.learning.calibration_engine import (
    CalibrationEngine,
    CalibrationType
)
from aurelia.learning.user_models import (
    UserModelManager,
    ModelType
)
from aurelia.learning.feedback_learning import (
    FeedbackLearner,
    FeedbackType,
    FeedbackCategory
)


def test_memory_consolidation():
    """Test memory consolidation capabilities."""
    print("Testing Memory Consolidation...")
    
    consolidator = MemoryConsolidator()
    
    # Add a consolidation candidate
    candidate = consolidator.add_candidate(
        content={"fact": "User prefers concise responses"},
        source_memory_type="working",
        importance_score=0.8,
        access_count=5,
        metadata={"type": "strategic"}
    )
    
    assert candidate.id == "candidate_0"
    assert candidate.importance_score == 0.8
    assert candidate.access_count == 5
    
    # Determine consolidation type
    consolidation_type = consolidator.determine_consolidation_type(candidate)
    assert consolidation_type in ConsolidationType
    
    # Calculate priority
    priority = consolidator.calculate_consolidation_priority(candidate)
    assert priority in ConsolidationPriority
    
    # Consolidate the candidate
    result = consolidator.consolidate(candidate.id)
    
    assert result.success == True
    assert result.target_memory_type in ConsolidationType
    assert result.consolidated_id
    assert 0 <= result.confidence <= 1
    
    # Get summary
    summary = consolidator.get_summary()
    assert summary["total_candidates"] == 0  # Should be removed after consolidation
    assert summary["total_consolidations"] == 1
    
    print("  Memory Consolidation: PASS")
    return True


def test_calibration_engine():
    """Test calibration engine capabilities."""
    print("Testing Calibration Engine...")
    
    engine = CalibrationEngine()
    
    # Record a prediction
    record = engine.record_prediction(
        calibration_type=CalibrationType.CONFIDENCE,
        predicted_value=0.8,
        confidence_estimate=0.7
    )
    
    assert record.calibration_type == CalibrationType.CONFIDENCE
    assert record.predicted_value == 0.8
    assert record.actual_value is None
    
    # Record the outcome
    engine.record_outcome(record.id, actual_value=0.75)
    
    # Get calibration score
    score = engine.get_calibration_score(CalibrationType.CONFIDENCE)
    assert 0 <= score <= 1
    
    # Adjust confidence based on calibration
    adjusted = engine.adjust_confidence(0.8, CalibrationType.CONFIDENCE)
    assert 0 <= adjusted <= 1
    
    # Get bias feedback
    feedback = engine.get_bias_feedback(CalibrationType.CONFIDENCE)
    assert isinstance(feedback, str)
    
    # Get summary
    summary = engine.get_summary()
    assert summary["total_records"] == 1
    assert summary["records_with_outcomes"] == 1
    
    print("  Calibration Engine: PASS")
    return True


def test_user_models():
    """Test user-specific model capabilities."""
    print("Testing User Models...")
    
    manager = UserModelManager()
    
    # Create a user model
    model = manager.create_user_model(
        user_id="user_123",
        model_type=ModelType.COMMUNICATION,
        initial_features={"style": "concise", "formality": "formal"}
    )
    
    assert model.user_id == "user_123"
    assert model.model_type == ModelType.COMMUNICATION
    assert len(model.features) == 2
    
    # Update a feature
    manager.update_feature(
        user_id="user_123",
        model_type=ModelType.COMMUNICATION,
        feature_name="style",
        feature_value="detailed"
    )
    
    # Get the updated feature
    feature = manager.get_feature("user_123", ModelType.COMMUNICATION, "style")
    assert feature.value == "detailed"
    assert feature.confidence > 0.5  # Should have increased
    
    # Get high-confidence features
    high_conf = manager.get_high_confidence_features("user_123", ModelType.COMMUNICATION, min_confidence=0.6)
    assert isinstance(high_conf, list)
    
    # Personalize response
    personalized = manager.personalize_response("user_123", "This is a response.")
    assert isinstance(personalized, str)
    
    # Get summary
    summary = manager.get_summary()
    assert summary["total_users"] == 1
    assert summary["total_models"] == 1
    
    print("  User Models: PASS")
    return True


def test_feedback_learning():
    """Test feedback learning capabilities."""
    print("Testing Feedback Learning...")
    
    learner = FeedbackLearner()
    
    # Record feedback events
    learner.record_feedback(
        feedback_type=FeedbackType.EXPLICIT_POSITIVE,
        feedback_category=FeedbackCategory.ACCURACY,
        context="career advice",
        content="The advice was accurate and helpful"
    )
    
    learner.record_feedback(
        feedback_type=FeedbackType.EXPLICIT_POSITIVE,
        feedback_category=FeedbackCategory.ACCURACY,
        context="salary advice",
        content="Salary estimate was spot on"
    )
    
    learner.record_feedback(
        feedback_type=FeedbackType.EXPLICIT_NEGATIVE,
        feedback_category=FeedbackCategory.CLARITY,
        context="technical explanation",
        content="The explanation was too complex"
    )
    
    # Get feedback by category
    accuracy_feedback = learner.get_feedback_by_category(FeedbackCategory.ACCURACY)
    assert len(accuracy_feedback) >= 2
    
    # Get feedback by type
    positive_feedback = learner.get_feedback_by_type(FeedbackType.EXPLICIT_POSITIVE)
    assert len(positive_feedback) >= 2
    
    # Analyze feedback patterns
    insights = learner.analyze_feedback_patterns()
    assert len(insights) >= 0
    
    # Get learning insights
    learning_insights = learner.get_learning_insights()
    assert len(learning_insights) >= 0
    
    # Get summary
    summary = learner.get_summary()
    assert summary["total_feedback"] == 3
    assert summary["total_insights"] >= 0
    
    print("  Feedback Learning: PASS")
    return True


def test_learning_integration():
    """Test integration of learning components."""
    print("Testing Learning Integration...")
    
    # Memory consolidation + calibration
    consolidator = MemoryConsolidator()
    calibrator = CalibrationEngine()
    
    candidate = consolidator.add_candidate(
        content={"prediction": "career success"},
        source_memory_type="working",
        importance_score=0.9
    )
    
    result = consolidator.consolidate(candidate.id)
    assert result.success == True
    
    # Calibration with confidence adjustment
    record = calibrator.record_prediction(
        calibration_type=CalibrationType.PREDICTION,
        predicted_value=0.8,
        confidence_estimate=0.7
    )
    
    calibrator.record_outcome(record.id, actual_value=0.85)
    
    adjusted_confidence = calibrator.adjust_confidence(0.75, CalibrationType.PREDICTION)
    assert 0 <= adjusted_confidence <= 1
    
    # User models + feedback learning
    user_manager = UserModelManager()
    feedback_learner = FeedbackLearner()
    
    user_manager.create_user_model(
        user_id="user_456",
        model_type=ModelType.PREFERENCE,
        initial_features={"detail_level": "high"}
    )
    
    feedback_learner.record_feedback(
        feedback_type=FeedbackType.EXPLICIT_POSITIVE,
        feedback_category=FeedbackCategory.USEFULNESS,
        context="detailed response",
        content="The detailed response was very helpful"
    )
    
    # Both systems should have collected data
    assert user_manager.get_summary()["total_users"] == 1
    assert feedback_learner.get_summary()["total_feedback"] == 1
    
    print("  Learning Integration: PASS")
    return True


def test():
    """Run all Phase 10 tests."""
    print("=" * 70)
    print("    AURELIA COGNITIVE OS V3 - PHASE 10 LEARNING TESTS")
    print("=" * 70)
    print()
    
    tests = [
        test_memory_consolidation,
        test_calibration_engine,
        test_user_models,
        test_feedback_learning,
        test_learning_integration
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
        print("SUCCESS: All Phase 10 learning tests passed!")
        print()
        print("Learning system ready:")
        print("  - Memory Consolidation (working to long-term memory transfer)")
        print("  - Calibration Engine (confidence and prediction accuracy)")
        print("  - User-Specific Models (personalization and adaptation)")
        print("  - Feedback Learning (improvement from user feedback)")
        print()
        print("PHASE 10 COMPLETE!")
        print()
        print("Next: Phase 11 - Evaluation (Golden suite, Adversarial conversations, Hallucination tests, Memory tests, Planning tests)")
        print("=" * 70)
        return True
    else:
        print("FAILURE: Some tests failed. Please fix the issues.")
        print("=" * 70)
        return False


if __name__ == "__main__":
    success = test()
    sys.exit(0 if success else 1)