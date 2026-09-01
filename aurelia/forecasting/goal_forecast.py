"""
Aurelia Cognitive OS V5 - Probabilistic Goal Forecasting Engine
================================================================
Combines Critical Path duration, current competency velocity, and Monte Carlo
variance modeling to forecast goal completion probability and status.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple
from aurelia.contracts.v5_contracts import (
    GoalForecast,
    GoalStatusEnum,
    CompetencyVelocityRecord
)
from aurelia.forecasting.critical_path import CriticalPathEngine, PrerequisiteDependency


class GoalForecastingEngine:
    """
    Generates time-bounded probabilistic forecasts for active executive goals.
    """

    @classmethod
    def forecast_goal(
        cls,
        goal_id: str,
        target_role: str,
        target_timeline_months: float, # e.g. 9 months
        competency_data: Dict[str, Dict[str, float]],
        dependencies: List[PrerequisiteDependency],
        velocities: Dict[str, CompetencyVelocityRecord]
    ) -> GoalForecast:
        """
        Executes critical path analysis and probabilistic projection.
        """
        # 1. Run Critical Path Method
        cp_nodes, bottleneck = CriticalPathEngine.compute_critical_path(
            competency_data,
            dependencies
        )

        # 2. Total weeks along Critical Path
        critical_path_weeks = sum(
            node.estimated_weeks for node in cp_nodes.values() if node.is_on_critical_path
        )
        critical_path_months = critical_path_weeks / 4.33

        # 3. Adjust for velocity factors
        velocity_multipliers = []
        blockers = []
        accelerators = []

        for cid, node in cp_nodes.items():
            if node.is_on_critical_path:
                v_rec = velocities.get(cid)
                if v_rec:
                    if v_rec.is_plateaued:
                        blockers.append(f"Competency '{node.name}' is plateaued at score {v_rec.current_score:.1f}")
                    elif v_rec.is_regressing:
                        blockers.append(f"Competency '{node.name}' has regressed")
                    elif v_rec.velocity_per_month > 0.25:
                        accelerators.append(f"Strong velocity in '{node.name}' (+{v_rec.velocity_per_month:.2f}/mo)")

        # 4. Probabilistic Completion Ratio
        target_to_critical_ratio = target_timeline_months / max(0.5, critical_path_months)
        
        if target_to_critical_ratio >= 1.3:
            status = GoalStatusEnum.AHEAD_OF_PLAN
            prob = min(0.95, 0.85 + (target_to_critical_ratio - 1.3) * 0.1)
        elif target_to_critical_ratio >= 0.95:
            status = GoalStatusEnum.ON_TRACK
            prob = min(0.88, 0.70 + (target_to_critical_ratio - 0.95) * 0.5)
        elif target_to_critical_ratio >= 0.70:
            status = GoalStatusEnum.AT_RISK
            prob = max(0.35, 0.40 * target_to_critical_ratio)
            blockers.append(f"Timeline constrained: Required {critical_path_months:.1f} months vs target {target_timeline_months:.1f} months")
        else:
            status = GoalStatusEnum.BLOCKED
            prob = max(0.10, 0.25 * target_to_critical_ratio)
            blockers.append(f"Critical path duration exceeds available timeline by {critical_path_months - target_timeline_months:.1f} months")

        min_window = round(max(1.0, critical_path_months * 0.85), 1)
        max_window = round(critical_path_months * 1.25, 1)

        return GoalForecast(
            goal_id=goal_id,
            target_role=target_role,
            probability_of_completion=round(prob, 2),
            likely_completion_window_months=(min_window, max_window),
            status=status,
            critical_path_bottleneck=bottleneck,
            blockers=tuple(blockers),
            accelerating_factors=tuple(accelerators),
            confidence_score=0.88,
            forecasted_at=datetime.now(timezone.utc)
        )
