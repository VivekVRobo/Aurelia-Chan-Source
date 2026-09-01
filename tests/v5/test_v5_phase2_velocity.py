"""
Aurelia Cognitive OS V5 - Phase 2 Velocity Test Suite
======================================================
Tests longitudinal competency tracking, velocity, plateau, and projection.
"""

import unittest
from datetime import datetime, timezone, timedelta
from aurelia.forecasting.velocity import LongitudinalCompetencyTracker


class TestV5Phase2Velocity(unittest.TestCase):
    """Test suite for Phase 2 Velocity."""

    def test_velocity_and_projected_weeks(self):
        """Test steady progress velocity and projected weeks to 4.0."""
        tracker = LongitudinalCompetencyTracker()
        now = datetime.now(timezone.utc)
        
        # Observation 1: 3 months ago (score 2.5)
        tracker.record_observation("executive_communication", 2.5, 0.8, "Q1 Review", now - timedelta(days=90))
        # Observation 2: 1 month ago (score 3.0)
        tracker.record_observation("executive_communication", 3.0, 0.85, "Mock Interview", now - timedelta(days=30))
        # Observation 3: Today (score 3.3)
        tracker.record_observation("executive_communication", 3.3, 0.9, "VP Presentation", now)
        
        record = tracker.calculate_velocity("executive_communication", target_score=4.0)
        
        self.assertEqual(record.current_score, 3.3)
        self.assertGreater(record.velocity_per_month, 0.2) # ~0.27 pts/mo
        self.assertFalse(record.is_plateaued)
        self.assertFalse(record.is_regressing)
        self.assertIsNotNone(record.projected_weeks_to_target)
        self.assertGreater(record.projected_weeks_to_target, 5.0)

    def test_plateau_detection(self):
        """Test detection of stalled competency progress."""
        tracker = LongitudinalCompetencyTracker()
        now = datetime.now(timezone.utc)
        
        # 3 observations over 60 days with virtually no change (3.0 -> 3.05 -> 3.02)
        tracker.record_observation("system_architecture", 3.0, 0.9, "Obs 1", now - timedelta(days=60))
        tracker.record_observation("system_architecture", 3.05, 0.9, "Obs 2", now - timedelta(days=30))
        tracker.record_observation("system_architecture", 3.02, 0.9, "Obs 3", now)
        
        record = tracker.calculate_velocity("system_architecture", target_score=4.5)
        self.assertTrue(record.is_plateaued)

    def test_regression_detection(self):
        """Test detection of declining competency score."""
        tracker = LongitudinalCompetencyTracker()
        now = datetime.now(timezone.utc)
        
        tracker.record_observation("stakeholder_alignment", 3.8, 0.85, "Obs 1", now - timedelta(days=60))
        tracker.record_observation("stakeholder_alignment", 3.3, 0.85, "Obs 2", now)
        
        record = tracker.calculate_velocity("stakeholder_alignment", target_score=4.0)
        self.assertTrue(record.is_regressing)
        self.assertLess(record.velocity_per_month, 0.0)


if __name__ == "__main__":
    unittest.main()
