"""
Aurelia Cognitive OS V4 - Counterfactual Sensitivity Engine
============================================================
Calculates sensitivity boundaries: "What exact parameter change would
alter Aurelia's recommendation?"
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional


@dataclass(frozen=True)
class SensitivityFactor:
    """A variable parameter and its impact weight on the final decision."""
    variable_name: str                   # e.g., "startup_valuation_growth", "budget_ownership_score"
    current_value: float
    decision_threshold_value: float      # Value at which recommendation flips
    sensitivity_percentage: float        # Relative weight in overall decision
    direction_needed: str                # "increase" or "decrease"


class CounterfactualEngine:
    """
    Computes sensitivity bounds for executive decisions.
    """

    @staticmethod
    def calculate_decision_sensitivity(
        current_readiness: float,
        target_threshold: float = 80.0,
        competency_gaps: Optional[Dict[str, float]] = None
    ) -> List[SensitivityFactor]:
        """
        Determines the single most impactful lever required to flip a 'WAIT' into 'APPLY NOW'.
        """
        factors: List[SensitivityFactor] = []
        gaps = competency_gaps or {"Budget Ownership": 1.2, "Exec Presentation": 0.8}
        
        total_gap = sum(gaps.values())
        
        for comp_name, gap in gaps.items():
            weight = (gap / max(0.1, total_gap)) * 100.0
            factors.append(SensitivityFactor(
                variable_name=comp_name,
                current_value=3.0 - gap,
                decision_threshold_value=3.0,
                sensitivity_percentage=weight,
                direction_needed="increase"
            ))
            
        factors.sort(key=lambda x: x.sensitivity_percentage, reverse=True)
        return factors
