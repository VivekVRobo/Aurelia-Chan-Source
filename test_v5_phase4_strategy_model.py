"""
Aurelia Cognitive OS V5 - Phase 4 Strategy Model Test Suite
============================================================
Tests personalized follow-through adaptation and optimal intervention selection.
"""

import unittest
from aurelia.learning.strategy_model import PersonalStrategyModelManager


class TestV5Phase4StrategyModel(unittest.TestCase):
    """Test suite for Phase 4 Personal Strategy Model."""

    def test_follow_through_bayesian_adaptation(self):
        """Test adaptation of follow-through probability upon observed behavior."""
        mgr = PersonalStrategyModelManager("user_1")
        
        # User repeatedly skips reading assignments (completed=False)
        for _ in range(4):
            mgr.record_action_follow_through("reading_assignment", completed=False)
            
        # User consistently completes mock interviews (completed=True)
        for _ in range(3):
            mgr.record_action_follow_through("mock_interview", completed=True)
            
        model = mgr.model
        self.assertLess(model.follow_through_by_modality["reading_assignment"], 0.30)
        self.assertGreater(model.follow_through_by_modality["mock_interview"], 0.88)
        self.assertEqual(model.preferred_learning_mode, "mock_interview")

    def test_optimal_intervention_selection(self):
        """Test selecting the most personalized format for an intervention."""
        mgr = PersonalStrategyModelManager("user_1")
        candidates = ["reading_assignment", "mock_interview", "structured_plan"]
        
        best = mgr.select_optimal_intervention(candidates)
        self.assertEqual(best, "mock_interview")


if __name__ == "__main__":
    unittest.main()
