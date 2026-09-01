"""
Aurelia Cognitive OS V5 - Value of Information & Active Learning Engine
=======================================================================
Quantifies decision uncertainty, calculates Expected Value of Information (EVOI),
and prioritizes high-leverage diagnostic clarification questions.
"""

from typing import Dict, Any, List, Optional
from aurelia.contracts.v5_contracts import InformationNeed


class InformationValueEngine:
    """
    Ranks missing variables by Expected Value of Information (EVOI).
    """

    COST_MULTIPLIERS = {
        "LOW": 1.0,      # Single number or boolean clarification
        "MEDIUM": 0.8,   # Document lookup or timeline review
        "HIGH": 0.5      # Sensitive internal disclosure or complex tax document
    }

    @classmethod
    def evaluate_information_need(
        cls,
        variable_name: str,
        current_uncertainty: float,
        expected_decision_impact: float,
        acquisition_cost: str = "LOW"
    ) -> InformationNeed:
        """Computes EVOI priority score for an unknown variable."""
        cost_factor = cls.COST_MULTIPLIERS.get(acquisition_cost, 1.0)
        # Priority = (Impact * Uncertainty) * Cost Discount
        priority = (expected_decision_impact * current_uncertainty) * cost_factor
        
        return InformationNeed(
            variable_name=variable_name,
            current_uncertainty=round(current_uncertainty, 3),
            expected_decision_impact=round(expected_decision_impact, 3),
            acquisition_cost=acquisition_cost,
            priority_score=round(priority, 4)
        )

    @classmethod
    def select_highest_priority_question(
        cls,
        candidate_needs: List[InformationNeed]
    ) -> Optional[InformationNeed]:
        """Returns the single highest-value variable to ask the user next."""
        if not candidate_needs:
            return None
        return max(candidate_needs, key=lambda x: x.priority_score)
