"""
Aurelia Cognitive OS V5 - Phase 1 Outcomes Test Suite
======================================================
Tests outcome tracking, success scoring, and LearningReceipt emission.
"""

import unittest
from aurelia.learning.outcomes import OutcomeTracker
from aurelia.contracts.v5_contracts import RecommendationStatus


class TestV5Phase1Outcomes(unittest.TestCase):
    """Test suite for Phase 1 Outcome Learning."""

    def test_outcome_lifecycle_and_receipt_emission(self):
        """Test full recommendation lifecycle from issue to measured outcome."""
        tracker = OutcomeTracker()
        
        # 1. Issue Recommendation
        rec = tracker.record_recommendation(
            recommendation_id="rec_mock_01",
            predicted_effect="Improve STAR clarity by +0.3",
            strategy_tag="structured_mock_interview"
        )
        self.assertEqual(rec.status, RecommendationStatus.RECOMMENDED)
        self.assertFalse(rec.action_taken)
        
        # 2. Complete with measured outcome
        completed, receipt = tracker.complete_recommendation(
            recommendation_id="rec_mock_01",
            observed_effect="Interview score jumped from 65 to 88 (+0.4)",
            measured_improvement=0.4,
            strategy_tag="structured_mock_interview"
        )
        
        self.assertEqual(completed.status, RecommendationStatus.COMPLETED)
        self.assertTrue(completed.action_taken)
        self.assertGreater(completed.success_score, 0.8)
        self.assertIsNotNone(receipt.receipt_id)
        self.assertEqual(receipt.update_method, "Empirical_Outcome_Measurement")
        
        # 3. Check strategy efficacy update
        efficacy = tracker.get_strategy_efficacy("structured_mock_interview")
        self.assertGreater(efficacy, 0.8)


if __name__ == "__main__":
    unittest.main()
