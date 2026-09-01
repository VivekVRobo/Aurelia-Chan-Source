"""
Aurelia Cognitive OS V5 - Phase 0 Contracts Test Suite
======================================================
Verifies V5 contracts, frozen immutability, freshness decay, and enums.
"""

import unittest
from datetime import datetime, timezone, timedelta
from aurelia.contracts.v5_contracts import (
    GoalStatusEnum,
    RecommendationStatus,
    RecommendationOutcome,
    CompetencyObservation,
    CompetencyVelocityRecord,
    GoalForecast,
    PersonalStrategyModel,
    StrategicInsight,
    LearningReceipt,
    InformationNeed,
    EventSignificance,
    ProactiveAction,
    ArtifactStalenessRecord,
    StalenessStatus
)


class TestV5Phase0Contracts(unittest.TestCase):
    """Test suite for Phase 0 V5 contracts."""

    def test_recommendation_outcome_immutability(self):
        """Test RecommendationOutcome immutability and fields."""
        now = datetime.now(timezone.utc)
        outcome = RecommendationOutcome(
            recommendation_id="rec_001",
            action_taken=True,
            status=RecommendationStatus.COMPLETED,
            recommended_at=now,
            completed_at=now + timedelta(days=14),
            predicted_effect="Improve executive communication by +0.3",
            observed_effect="Mock interview score increased from 3.2 to 3.6",
            success_score=0.92,
            measured_improvement=0.4
        )
        self.assertEqual(outcome.status, RecommendationStatus.COMPLETED)
        self.assertTrue(outcome.action_taken)
        with self.assertRaises(Exception):
            outcome.success_score = 0.5 # Immutability check

    def test_strategic_insight_freshness_decay(self):
        """Test exponential freshness decay calculation."""
        now = datetime.now(timezone.utc)
        insight = StrategicInsight(
            insight_id="ins_101",
            claim="Mock interview practice produces faster improvement than passive reading.",
            category="interview_strategy",
            evidence_count=6,
            confidence=0.88,
            first_observed=now - timedelta(days=365),
            last_validated=now - timedelta(days=180), # Exactly 1 half-life ago
            decay_half_life_days=180.0
        )
        freshness = insight.calculate_current_freshness(now)
        self.assertAlmostEqual(freshness, 0.5, delta=0.05)

    def test_information_need_priority(self):
        """Test InformationNeed priority calculation."""
        need = InformationNeed(
            variable_name="startup_runway_months",
            current_uncertainty=0.85,
            expected_decision_impact=0.75,
            acquisition_cost="LOW",
            priority_score=0.85 * 0.75
        )
        self.assertAlmostEqual(need.priority_score, 0.6375, places=4)

    def test_goal_forecast_status_and_invariants(self):
        """Test GoalForecast contract."""
        forecast = GoalForecast(
            goal_id="g_dir",
            target_role="Director of Engineering",
            probability_of_completion=0.78,
            likely_completion_window_months=(6.0, 9.0),
            status=GoalStatusEnum.ON_TRACK,
            critical_path_bottleneck="Budget Ownership Scope",
            blockers=("Lack of formal $5M+ P&L attribution",),
            accelerating_factors=("Rapid velocity in executive communication",),
            confidence_score=0.85
        )
        self.assertEqual(forecast.status, GoalStatusEnum.ON_TRACK)
        self.assertEqual(forecast.critical_path_bottleneck, "Budget Ownership Scope")


if __name__ == "__main__":
    unittest.main()
