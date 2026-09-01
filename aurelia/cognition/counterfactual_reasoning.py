"""
Aurelia Cognitive OS V3 - Phase 9: Counterfactual Reasoning
=======================================================
Explores "what if" scenarios and alternative possibilities.

Counterfactual reasoning allows Aurelia to consider alternative
outcomes and test assumptions about causality.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class CounterfactualType(Enum):
    """Types of counterfactual questions."""
    WHAT_IF = "what_if"
    ONLY_IF = "only_if"
    EVEN_IF = "even_if"
    SUPPOSE_THAT = "suppose_that"


@dataclass
class Counterfactual:
    """
    A counterfactual question or scenario.
    
    Explores "what if" alternatives to actual situations.
    """
    id: str
    counterfactual_type: CounterfactualType
    original_situation: str
    counterfactual_situation: str
    premise: str
    plausibility: float
    implications: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)


@dataclass
class CounterfactualAnalysis:
    """
    Analysis of a counterfactual scenario.
    
    Evaluates whether the counterfactual is plausible and what
    would need to change for it to become true.
    """
    counterfactual_id: str
    is_plausible: bool
    plausibility_score: float
    required_changes: List[str]
    likelihood_estimate: str
    confidence: float
    alternative_counterfactuals: List[str] = field(default_factory=list)


class CounterfactualReasoner:
    """
    Explores "what if" scenarios and alternative possibilities.
    
    The counterfactual reasoner:
    - Formulates counterfactual questions
    - Evaluates plausibility of alternatives
    - Identifies required changes for counterfactuals
    - Tests assumptions about causality
    """
    
    def __init__(self):
        self.counterfactuals: Dict[str, Counterfactual] = {}
        self.analyses: Dict[str, CounterfactualAnalysis] = {}
        self.counterfactual_counter = 0
    
    def create_counterfactual(
        self,
        counterfactual_type: CounterfactualType,
        original_situation: str,
        counterfactual_situation: str,
        premise: str,
        assumptions: Optional[List[str]] = None
    ) -> Counterfactual:
        """Create a new counterfactual scenario."""
        counterfactual_id = f"counterfactual_{self.counterfactual_counter}"
        
        # Estimate initial plausibility
        plausibility = self._estimate_plausibility(
            original_situation,
            counterfactual_situation,
            assumptions or []
        )
        
        counterfactual = Counterfactual(
            id=counterfactual_id,
            counterfactual_type=counterfactual_type,
            original_situation=original_situation,
            counterfactual_situation=counterfactual_situation,
            premise=premise,
            plausibility=plausibility,
            assumptions=assumptions or []
        )
        
        self.counterfactuals[counterfactual_id] = counterfactual
        self.counterfactual_counter += 1
        
        return counterfactual
    
    def analyze_counterfactual(self, counterfactual_id: str) -> CounterfactualAnalysis:
        """
        Analyze a counterfactual scenario.
        
        Evaluates plausibility and identifies required changes.
        """
        counterfactual = self.get_counterfactual(counterfactual_id)
        if not counterfactual:
            raise ValueError(f"Counterfactual {counterfactual_id} not found")
        
        # Determine plausibility
        is_plausible = counterfactual.plausibility >= 0.5
        
        # Identify required changes
        required_changes = self._identify_required_changes(
            counterfactual.original_situation,
            counterfactual.counterfactual_situation
        )
        
        # Estimate likelihood
        likelihood = self._estimate_likelihood(
            is_plausible,
            required_changes,
            counterfactual.assumptions
        )
        
        # Generate alternative counterfactuals
        alternatives = self._generate_alternatives(counterfactual)
        
        analysis = CounterfactualAnalysis(
            counterfactual_id=counterfactual_id,
            is_plausible=is_plausible,
            plausibility_score=counterfactual.plausibility,
            required_changes=required_changes,
            likelihood_estimate=likelihood,
            confidence=0.7,
            alternative_counterfactuals=alternatives
        )
        
        self.analyses[counterfactual_id] = analysis
        return analysis
    
    def _estimate_plausibility(
        self,
        original: str,
        counterfactual: str,
        assumptions: List[str]
    ) -> float:
        """Estimate plausibility of counterfactual."""
        # Simple plausibility estimation based on assumption count
        base_plausibility = 0.5
        assumption_penalty = len(assumptions) * 0.1
        return max(0.1, base_plausibility - assumption_penalty)
    
    def _identify_required_changes(self, original: str, counterfactual: str) -> List[str]:
        """Identify what would need to change for counterfactual to be true."""
        # Simple keyword-based change detection
        changes = []
        
        # Look for key differences
        original_lower = original.lower()
        counterfactual_lower = counterfactual.lower()
        
        # Extract potential changes
        if "management" in counterfactual_lower and "management" not in original_lower:
            changes.append("Gain management experience")
        
        if "director" in counterfactual_lower and "director" not in original_lower:
            changes.append("Reach Director level")
        
        if "5 years" in counterfactual_lower and "5 years" not in original_lower:
            changes.append("Accumulate 5 years of experience")
        
        if not changes:
            changes.append("Additional analysis needed to identify specific changes")
        
        return changes
    
    def _estimate_likelihood(
        self,
        is_plausible: bool,
        required_changes: List[str],
        assumptions: List[str]
    ) -> str:
        """Estimate likelihood of counterfactual becoming true."""
        if not is_plausible:
            return "Unlikely"
        
        if len(required_changes) <= 1:
            return "Likely"
        elif len(required_changes) <= 3:
            return "Possible"
        else:
            return "Unlikely"
    
    def _generate_alternatives(self, counterfactual: Counterfactual) -> List[str]:
        """Generate alternative counterfactual scenarios."""
        alternatives = []
        
        # Generate alternatives based on type
        if counterfactual.counterfactual_type == CounterfactualType.WHAT_IF:
            alternatives.append("Consider if additional factors could enable this scenario")
            alternatives.append("Explore intermediate scenarios between current and counterfactual")
        
        return alternatives
    
    def get_counterfactual(self, counterfactual_id: str) -> Optional[Counterfactual]:
        """Get a counterfactual by ID."""
        return self.counterfactuals.get(counterfactual_id)
    
    def get_analysis(self, counterfactual_id: str) -> Optional[CounterfactualAnalysis]:
        """Get analysis for a counterfactual."""
        return self.analyses.get(counterfactual_id)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the counterfactual reasoner state."""
        return {
            "total_counterfactuals": len(self.counterfactuals),
            "total_analyses": len(self.analyses),
            "by_type": {ct.value: len([c for c in self.counterfactuals.values() if c.counterfactual_type == ct]) for ct in CounterfactualType},
            "plausible_count": len([c for c in self.counterfactuals.values() if c.plausibility >= 0.5])
        }