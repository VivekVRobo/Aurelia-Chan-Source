"""
Aurelia Cognitive OS V5 - Phase 3 Goal Forecasting Test Suite
==============================================================
Tests Critical Path Method (CPM) calculation and probabilistic goal forecasting.
"""

import unittest
from aurelia.forecasting.critical_path import CriticalPathEngine, PrerequisiteDependency
from aurelia.forecasting.goal_forecast import GoalForecastingEngine
from aurelia.contracts.v5_contracts import GoalStatusEnum, CompetencyVelocityRecord


class TestV5Phase3GoalForecast(unittest.TestCase):
    """Test suite for Phase 3 Goal Forecasting."""

    def test_critical_path_computation(self):
        """Test CPM forward/backward passes and bottleneck identification."""
        competencies = {
            "c_comm": {"name": "Executive Communication", "current": 3.0, "target": 4.0, "weeks_needed": 6.0},
            "c_budget": {"name": "Budget Ownership", "current": 2.0, "target": 4.0, "weeks_needed": 12.0},
            "c_org": {"name": "Organizational Influence", "current": 3.2, "target": 4.0, "weeks_needed": 4.0},
            "c_director": {"name": "Director Ready", "current": 2.5, "target": 4.5, "weeks_needed": 2.0}
        }
        
        # c_comm -> c_director; c_budget -> c_director; c_org -> c_director
        deps = [
            PrerequisiteDependency("c_comm", "c_director"),
            PrerequisiteDependency("c_budget", "c_director"),
            PrerequisiteDependency("c_org", "c_director")
        ]
        
        nodes, bottleneck = CriticalPathEngine.compute_critical_path(competencies, deps)
        
        self.assertTrue(nodes["c_budget"].is_on_critical_path)
        self.assertTrue(nodes["c_director"].is_on_critical_path)
        self.assertEqual(nodes["c_budget"].slack_weeks, 0.0)
        self.assertGreater(nodes["c_org"].slack_weeks, 0.0) # has slack
        self.assertEqual(bottleneck, "Budget Ownership")

    def test_goal_forecast_status_and_probability(self):
        """Test probabilistic goal forecast on track vs at risk."""
        competencies = {
            "c_budget": {"name": "Budget Ownership", "current": 2.0, "target": 4.0, "weeks_needed": 12.0},
            "c_director": {"name": "Director Ready", "current": 2.5, "target": 4.5, "weeks_needed": 2.0}
        }
        deps = [PrerequisiteDependency("c_budget", "c_director")]
        
        velocities = {
            "c_budget": CompetencyVelocityRecord("c_budget", 2.0, 0.35, 0.0, False, False, 10.0, 4)
        }
        
        # Case A: Ample target timeline (9 months) -> ON_TRACK
        forecast_on_track = GoalForecastingEngine.forecast_goal(
            goal_id="g_dir",
            target_role="Director of Engineering",
            target_timeline_months=9.0,
            competency_data=competencies,
            dependencies=deps,
            velocities=velocities
        )
        self.assertIn(forecast_on_track.status, [GoalStatusEnum.ON_TRACK, GoalStatusEnum.AHEAD_OF_PLAN])
        self.assertGreater(forecast_on_track.probability_of_completion, 0.70)
        
        # Case B: Compressed timeline (2 months vs ~3.2 months required) -> AT_RISK / BLOCKED
        forecast_at_risk = GoalForecastingEngine.forecast_goal(
            goal_id="g_dir",
            target_role="Director of Engineering",
            target_timeline_months=2.0,
            competency_data=competencies,
            dependencies=deps,
            velocities=velocities
        )
        self.assertIn(forecast_at_risk.status, [GoalStatusEnum.AT_RISK, GoalStatusEnum.BLOCKED])
        self.assertLess(forecast_at_risk.probability_of_completion, 0.50)


if __name__ == "__main__":
    unittest.main()
