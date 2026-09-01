"""
Aurelia Cognitive OS V5 - Phase 8 Plan Drift Test Suite
========================================================
Tests plan drift calculation and replan recommendation triggers.
"""

import unittest
from aurelia.forecasting.drift import PlanDriftDetector


class TestV5Phase8PlanDrift(unittest.TestCase):
    """Test suite for Phase 8 Plan Drift."""

    def test_nominal_pacing(self):
        """Test on-track execution pacing."""
        report = PlanDriftDetector.evaluate_drift(
            goal_id="g_vp",
            planned_actions_per_week=2.0,
            actual_actions_completed=6,
            evaluation_period_weeks=3.0
        )
        self.assertEqual(report.drift_severity, "NOMINAL")
        self.assertFalse(report.requires_replan)
        self.assertAlmostEqual(report.drift_percentage, 0.0)

    def test_critical_drift_triggers_replan(self):
        """Test severe execution lag triggering a transparent replan."""
        report = PlanDriftDetector.evaluate_drift(
            goal_id="g_vp",
            planned_actions_per_week=2.0, # Expected 6 actions
            actual_actions_completed=1,   # Completed only 1 action
            evaluation_period_weeks=3.0
        )
        self.assertEqual(report.drift_severity, "CRITICAL")
        self.assertTrue(report.requires_replan)
        self.assertLess(report.drift_percentage, -60.0)
        self.assertIn("Transparent replan recommended", report.recommended_adjustment)


if __name__ == "__main__":
    unittest.main()
