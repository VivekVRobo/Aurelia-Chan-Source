"""
Aurelia Cognitive OS V5 - Phase 6 Value of Information Test Suite
==================================================================
Tests EVOI calculation and active learning diagnostic question selection.
"""

import unittest
from aurelia.information.value_of_information import InformationValueEngine
from aurelia.contracts.v5_contracts import InformationNeed


class TestV5Phase6ValueOfInformation(unittest.TestCase):
    """Test suite for Phase 6 Value of Information."""

    def test_evoi_calculation_and_ranking(self):
        """Test that high-impact low-cost questions rank above trivial questions."""
        engine = InformationValueEngine()
        
        # Variable 1: Startup Runway (High impact 0.85, High uncertainty 0.90, Low cost -> ~0.765)
        need_runway = engine.evaluate_information_need(
            variable_name="startup_runway_months",
            current_uncertainty=0.90,
            expected_decision_impact=0.85,
            acquisition_cost="LOW"
        )
        
        # Variable 2: Office Commute (Low impact 0.15, Medium uncertainty 0.50, Low cost -> ~0.075)
        need_commute = engine.evaluate_information_need(
            variable_name="commute_distance_miles",
            current_uncertainty=0.50,
            expected_decision_impact=0.15,
            acquisition_cost="LOW"
        )
        
        # Variable 3: Cap Table Liquidation Preference (High impact 0.90, High uncertainty 0.90, High cost -> ~0.405)
        need_liquidation = engine.evaluate_information_need(
            variable_name="liquidation_preference_tier",
            current_uncertainty=0.90,
            expected_decision_impact=0.90,
            acquisition_cost="HIGH"
        )
        
        highest = engine.select_highest_priority_question([need_commute, need_runway, need_liquidation])
        self.assertIsNotNone(highest)
        self.assertEqual(highest.variable_name, "startup_runway_months")
        self.assertGreater(need_runway.priority_score, need_liquidation.priority_score)
        self.assertGreater(need_liquidation.priority_score, need_commute.priority_score)


if __name__ == "__main__":
    unittest.main()
