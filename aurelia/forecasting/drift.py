"""
Aurelia Cognitive OS V5 - Plan Drift & Automatic Replanning Engine
===================================================================
Detects divergence between planned milestones and actual observed behavior,
and generates structured, transparent replanning recommendations.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple


@dataclass(frozen=True)
class PlanDriftReport:
    """Detailed diagnostic report on plan execution drift."""
    goal_id: str
    planned_pace_per_week: float
    observed_pace_per_week: float
    drift_percentage: float # e.g. -60% (lagging) or +25% (accelerated)
    drift_severity: str # "NOMINAL", "MODERATE", "CRITICAL"
    requires_replan: bool
    recommended_adjustment: str
    detected_at: datetime


class PlanDriftDetector:
    """
    Monitors execution pacing and triggers replan recommendations when necessary.
    """

    @classmethod
    def evaluate_drift(
        cls,
        goal_id: str,
        planned_actions_per_week: float, # e.g. 2.0 sessions / week
        actual_actions_completed: int,
        evaluation_period_weeks: float # e.g. 3.0 weeks
    ) -> PlanDriftReport:
        """
        Calculates drift percentage and evaluates if a replan is recommended.
        """
        expected_total = planned_actions_per_week * evaluation_period_weeks
        observed_pace = actual_actions_completed / max(0.5, evaluation_period_weeks)

        if expected_total <= 0:
            drift_pct = 0.0
        else:
            drift_pct = (actual_actions_completed - expected_total) / expected_total * 100.0

        if drift_pct < -50.0:
            severity = "CRITICAL"
            requires_replan = True
            recom = (
                f"Plan execution has drifted by {abs(drift_pct):.0f}% behind target pace over {evaluation_period_weeks:.0f} weeks. "
                "Transparent replan recommended: Re-anchor milestone timelines or compress secondary workstreams."
            )
        elif drift_pct < -25.0:
            severity = "MODERATE"
            requires_replan = False
            recom = "Moderate pacing lag detected. Prioritize critical path items to prevent deadline compression."
        else:
            severity = "NOMINAL"
            requires_replan = False
            recom = "Execution pacing is on track with baseline plan."

        return PlanDriftReport(
            goal_id=goal_id,
            planned_pace_per_week=planned_actions_per_week,
            observed_pace_per_week=round(observed_pace, 2),
            drift_percentage=round(drift_pct, 1),
            drift_severity=severity,
            requires_replan=requires_replan,
            recommended_adjustment=recom,
            detected_at=datetime.now(timezone.utc)
        )
