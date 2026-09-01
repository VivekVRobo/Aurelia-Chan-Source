"""
Aurelia Cognitive OS V5 - Phase 7 Adaptive Interview Test Suite
================================================================
Tests diagnostic interview question selection using Information Gain.
"""

import unittest
from aurelia.interview.adaptive_system import AdaptiveInterviewEngine


class TestV5Phase7AdaptiveInterview(unittest.TestCase):
    """Test suite for Phase 7 Adaptive Interview."""

    def test_information_gain_selection(self):
        """Test that unmeasured competencies with high uncertainty are prioritized."""
        engine = AdaptiveInterviewEngine()
        
        # User has verified strong stakeholder alignment (0.95 confidence)
        # But budget governance is completely unmeasured (0.10 confidence)
        confidences = {
            "financial_negotiation": 0.85,
            "stakeholder_alignment": 0.95,
            "budget_governance": 0.10,
            "org_scaling": 0.60
        }
        
        selected = engine.select_next_question(
            known_competency_confidence=confidences,
            asked_question_ids=[]
        )
        
        self.assertIsNotNone(selected)
        self.assertEqual(selected.question_id, "q_budget_cut")
        self.assertEqual(selected.target_competency, "budget_governance")

    def test_question_deduplication(self):
        """Test that already-asked questions are omitted from selection."""
        engine = AdaptiveInterviewEngine()
        confidences = {"budget_governance": 0.10}
        
        # If q_budget_cut was already asked, it should pick the next highest
        selected = engine.select_next_question(
            known_competency_confidence=confidences,
            asked_question_ids=["q_budget_cut"]
        )
        self.assertIsNotNone(selected)
        self.assertNotEqual(selected.question_id, "q_budget_cut")


if __name__ == "__main__":
    unittest.main()
