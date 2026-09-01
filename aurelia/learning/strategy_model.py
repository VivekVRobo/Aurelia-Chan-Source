"""
Aurelia Cognitive OS V5 - Personal Strategy Model
=================================================
Maintains an empirical, Bayesian-updated profile of what learning modalities,
feedback styles, and session paces produce the highest follow-through for the user.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from aurelia.contracts.v5_contracts import PersonalStrategyModel


class PersonalStrategyModelManager:
    """
    Manages and adapts the user's personal strategy model based on observed actions.
    """

    def __init__(self, user_id: str = "local_user"):
        self.user_id = user_id
        # Initialize with balanced uninformative priors
        self.model = PersonalStrategyModel(
            preferred_learning_mode="simulation",
            follow_through_by_modality={
                "mock_interview": 0.85,
                "structured_plan": 0.80,
                "simulation": 0.88,
                "reading_assignment": 0.40
            },
            response_to_feedback_style={
                "direct": 0.85,
                "gentle": 0.65
            },
            domain_learning_velocities={
                "executive_communication": 0.20,
                "financial_governance": 0.12,
                "organizational_leadership": 0.18
            },
            optimal_session_duration_minutes=25,
            last_updated=datetime.now(timezone.utc)
        )

    def record_action_follow_through(
        self,
        modality: str,
        completed: bool,
        learning_rate: float = 0.10
    ) -> PersonalStrategyModel:
        """
        Updates modality follow-through probability via Bayesian online update.
        """
        current_p = self.model.follow_through_by_modality.get(modality, 0.70)
        target_val = 1.0 if completed else 0.0
        new_p = current_p + learning_rate * (target_val - current_p)
        new_p = max(0.05, min(0.98, new_p))

        updated_modalities = dict(self.model.follow_through_by_modality)
        updated_modalities[modality] = round(new_p, 3)

        # Select highest-followthrough modality
        best_mode = max(updated_modalities.items(), key=lambda x: x[1])[0]

        self.model = PersonalStrategyModel(
            preferred_learning_mode=best_mode,
            follow_through_by_modality=updated_modalities,
            response_to_feedback_style=self.model.response_to_feedback_style,
            domain_learning_velocities=self.model.domain_learning_velocities,
            optimal_session_duration_minutes=self.model.optimal_session_duration_minutes,
            last_updated=datetime.now(timezone.utc)
        )
        return self.model

    def select_optimal_intervention(
        self,
        candidate_modalities: List[str]
    ) -> str:
        """
        Returns the candidate modality with the highest expected user follow-through.
        """
        return max(
            candidate_modalities,
            key=lambda m: self.model.follow_through_by_modality.get(m, 0.5)
        )
