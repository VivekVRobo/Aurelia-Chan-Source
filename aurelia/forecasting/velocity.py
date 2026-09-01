"""
Aurelia Cognitive OS V5 - Longitudinal Competency Velocity Engine
==================================================================
Calculates mathematical velocity, acceleration, plateau detection, and
projected time-to-target for individual user competencies over time.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from aurelia.contracts.v5_contracts import (
    CompetencyObservation,
    CompetencyVelocityRecord
)


class LongitudinalCompetencyTracker:
    """
    Stores historical observations and computes trajectory metrics.
    """

    def __init__(self):
        # competency_id -> sorted list of CompetencyObservation
        self.history: Dict[str, List[CompetencyObservation]] = {}

    def record_observation(
        self,
        competency_id: str,
        score: float,
        confidence: float,
        source_context: str,
        observed_at: Optional[datetime] = None,
        evidence_id: str = "ev_direct"
    ) -> CompetencyObservation:
        """Appends a timestamped observation to historical record."""
        obs = CompetencyObservation(
            competency_id=competency_id,
            observed_at=observed_at or datetime.now(timezone.utc),
            score=max(1.0, min(5.0, score)),
            confidence=max(0.0, min(1.0, confidence)),
            source_context=source_context,
            evidence_id=evidence_id
        )
        if competency_id not in self.history:
            self.history[competency_id] = []
        self.history[competency_id].append(obs)
        # Keep sorted by timestamp
        self.history[competency_id].sort(key=lambda x: x.observed_at)
        return obs

    def calculate_velocity(
        self,
        competency_id: str,
        target_score: float = 4.0
    ) -> CompetencyVelocityRecord:
        """
        Computes velocity (points/month), acceleration, plateau, and projected weeks.
        """
        observations = self.history.get(competency_id, [])
        if not observations:
            return CompetencyVelocityRecord(
                competency_id=competency_id,
                current_score=1.0,
                velocity_per_month=0.0,
                acceleration_per_month=0.0,
                is_plateaued=False,
                is_regressing=False,
                projected_weeks_to_target=None,
                historical_count=0
            )

        if len(observations) == 1:
            current = observations[0].score
            return CompetencyVelocityRecord(
                competency_id=competency_id,
                current_score=current,
                velocity_per_month=0.0,
                acceleration_per_month=0.0,
                is_plateaued=False,
                is_regressing=False,
                projected_weeks_to_target=None,
                historical_count=1
            )

        # Multi-observation calculation
        t_first = observations[0].observed_at
        t_last = observations[-1].observed_at
        total_days = max(1.0, (t_last - t_first).total_seconds() / 86400.0)
        total_months = total_days / 30.0

        current_score = observations[-1].score
        first_score = observations[0].score
        overall_velocity = (current_score - first_score) / max(0.1, total_months)

        # Compute mid-point velocity to calculate acceleration
        acceleration = 0.0
        if len(observations) >= 3:
            mid_idx = len(observations) // 2
            v1 = (observations[mid_idx].score - observations[0].score) / max(0.1, ((observations[mid_idx].observed_at - t_first).total_seconds() / 86400.0) / 30.0)
            v2 = (current_score - observations[mid_idx].score) / max(0.1, ((t_last - observations[mid_idx].observed_at).total_seconds() / 86400.0) / 30.0)
            acceleration = (v2 - v1) / max(0.1, total_months / 2.0)

        # Plateau detection: >= 3 observations over >= 45 days with delta score < 0.15
        is_plateaued = False
        if len(observations) >= 3 and total_days >= 45.0 and abs(current_score - first_score) < 0.15:
            is_plateaued = True

        # Regression detection
        is_regressing = overall_velocity < -0.05

        # Projected weeks to target
        projected_weeks = None
        gap = target_score - current_score
        if gap > 0 and overall_velocity > 0.05:
            months_needed = gap / overall_velocity
            projected_weeks = round(months_needed * 4.33, 1)
        elif gap <= 0:
            projected_weeks = 0.0

        return CompetencyVelocityRecord(
            competency_id=competency_id,
            current_score=current_score,
            velocity_per_month=round(overall_velocity, 3),
            acceleration_per_month=round(acceleration, 3),
            is_plateaued=is_plateaued,
            is_regressing=is_regressing,
            projected_weeks_to_target=projected_weeks,
            historical_count=len(observations)
        )
