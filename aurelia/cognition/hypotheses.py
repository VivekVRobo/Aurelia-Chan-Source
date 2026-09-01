"""
Aurelia Cognitive OS V4 - Strategic Hypotheses & Beam Search
=============================================================
Replaces open-ended LLM guessing with structured hypothesis objects,
deterministic beam search, hard constraint pruning, and utility scoring.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
from aurelia.contracts.core_types import EvidenceRef


@dataclass(frozen=True)
class StrategicHypothesis:
    """A fully specified strategic trajectory candidate."""
    id: str
    strategy_type: str                   # e.g., "Internal_Promotion", "External_Search", "Startup_Pivot"
    title: str
    assumptions: Tuple[str, ...]
    actions: Tuple[str, ...]
    
    # Quantitative & Value Attributes
    expected_value_usd: float
    strategic_value_score: float         # 0.0 to 1.0 (leadership scope, brand)
    reversibility_score: float           # 0.0 to 1.0 (ease of undoing decision)
    risk_penalty: float                  # 0.0 to 1.0
    time_to_value_months: float
    effort_cost: float                   # 0.0 to 1.0
    uncertainty_penalty: float           # 0.0 to 1.0
    
    # Hard Constraints & Prerequisites
    required_prerequisites: Tuple[str, ...] = field(default_factory=tuple)
    violates_hard_constraints: bool = False
    
    # Lineage & Provenance
    evidence: Tuple[EvidenceRef, ...] = field(default_factory=tuple)
    confidence: float = 0.80

    def calculate_utility(self) -> float:
        """
        Calculates deterministic strategic utility score.
        If it violates hard constraints, utility is -999.0 (pruned).
        """
        if self.violates_hard_constraints:
            return -999.0
            
        # Utility formula
        utility = (
            (self.strategic_value_score * 0.35) +
            ((self.expected_value_usd / 500000.0) * 0.25) +
            (self.reversibility_score * 0.15) -
            (self.risk_penalty * 0.20) -
            (self.uncertainty_penalty * 0.15) -
            ((self.time_to_value_months / 24.0) * 0.10)
        )
        return utility


class CognitiveSearchEngine:
    """
    Beam search over complete strategy spaces with hard constraint pruning.
    """

    @classmethod
    def evaluate_and_rank(
        cls,
        hypotheses: List[StrategicHypothesis],
        user_hard_constraints: List[str],
        user_known_skills: List[str],
        beam_width: int = 3
    ) -> List[StrategicHypothesis]:
        """
        Prunes invalid strategies and returns the top-k highest utility candidates.
        """
        valid_candidates: List[StrategicHypothesis] = []
        
        for hyp in hypotheses:
            is_pruned = False
            
            # 1. Prune if violates user hard constraints
            for action in hyp.actions:
                for constraint in user_hard_constraints:
                    if constraint.lower() in action.lower():
                        is_pruned = True
                        break
                        
            # 2. Prune if missing required skill prerequisites
            for prereq in hyp.required_prerequisites:
                if prereq not in user_known_skills:
                    is_pruned = True
                    break
                    
            if not is_pruned and not hyp.violates_hard_constraints:
                valid_candidates.append(hyp)
                
        # Sort descending by calculated utility
        valid_candidates.sort(key=lambda h: h.calculate_utility(), reverse=True)
        return valid_candidates[:beam_width]
