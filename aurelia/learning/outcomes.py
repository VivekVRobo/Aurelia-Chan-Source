"""
Aurelia Cognitive OS V5 - Outcome Learning Engine
==================================================
Tracks what happens after recommendations are made, records observed outcomes,
evaluates strategy effectiveness, and updates belief models.
"""

import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from aurelia.contracts.v5_contracts import (
    RecommendationOutcome,
    RecommendationStatus,
    LearningReceipt
)


class OutcomeTracker:
    """
    Tracks recommendation follow-through and measures real-world efficacy.
    """

    def __init__(self):
        self.outcomes: Dict[str, RecommendationOutcome] = {}
        self.strategy_effectiveness: Dict[str, List[float]] = {}

    def record_recommendation(
        self,
        recommendation_id: str,
        predicted_effect: str,
        strategy_tag: str = "general"
    ) -> RecommendationOutcome:
        """Registers a newly issued recommendation."""
        outcome = RecommendationOutcome(
            recommendation_id=recommendation_id,
            action_taken=False,
            status=RecommendationStatus.RECOMMENDED,
            recommended_at=datetime.now(timezone.utc),
            completed_at=None,
            predicted_effect=predicted_effect,
            observed_effect=None,
            success_score=0.0,
            measured_improvement=0.0
        )
        self.outcomes[recommendation_id] = outcome
        if strategy_tag not in self.strategy_effectiveness:
            self.strategy_effectiveness[strategy_tag] = []
        return outcome

    def complete_recommendation(
        self,
        recommendation_id: str,
        observed_effect: str,
        measured_improvement: float,
        strategy_tag: str = "general"
    ) -> Tuple[RecommendationOutcome, LearningReceipt]:
        """
        Marks recommendation complete with measured improvement,
        calculates success score, and generates an immutable LearningReceipt.
        """
        if recommendation_id not in self.outcomes:
            raise KeyError(f"Recommendation {recommendation_id} not found in tracker.")

        prior = self.outcomes[recommendation_id]
        success_score = max(0.0, min(1.0, 0.5 + (measured_improvement * 1.25)))
        
        updated_outcome = RecommendationOutcome(
            recommendation_id=recommendation_id,
            action_taken=True,
            status=RecommendationStatus.COMPLETED,
            recommended_at=prior.recommended_at,
            completed_at=datetime.now(timezone.utc),
            predicted_effect=prior.predicted_effect,
            observed_effect=observed_effect,
            success_score=success_score,
            measured_improvement=measured_improvement
        )
        self.outcomes[recommendation_id] = updated_outcome
        
        # Record effectiveness metric
        self.strategy_effectiveness[strategy_tag].append(success_score)
        
        # Generate Learning Receipt
        receipt = LearningReceipt(
            receipt_id=f"lr_{int(time.time()*1000)}",
            insight_or_belief_id=f"strat_{strategy_tag}",
            previous_belief=f"Strategy '{strategy_tag}' baseline expectation",
            new_evidence_refs=(f"outcome_{recommendation_id}",),
            updated_belief=f"Strategy '{strategy_tag}' efficacy updated to {self.get_strategy_efficacy(strategy_tag):.2f}",
            update_method="Empirical_Outcome_Measurement",
            confidence_delta=0.05
        )
        
        return updated_outcome, receipt

    def get_strategy_efficacy(self, strategy_tag: str) -> float:
        """Returns mean observed success score for a strategy."""
        scores = self.strategy_effectiveness.get(strategy_tag, [])
        if not scores:
            return 0.5 # Prior
        return sum(scores) / len(scores)
