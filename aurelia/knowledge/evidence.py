"""
Aurelia Cognitive OS V4 - Evidence & Provenance Model
=====================================================
Calculates observed competency scores, weights evidence by source reliability,
and maintains temporal validity for every fact in the cognitive brain.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Tuple, Optional
from aurelia.contracts.core_types import EvidenceRef, EvidenceReliability, VerifiedValue, ConfidenceScore


@dataclass(frozen=True)
class CompetencyRequirement:
    """Standardized competency level required for an executive role."""
    competency_id: str
    name: str                           # e.g., "Budget Ownership", "People Leadership"
    required_level: float               # 1.0 (Junior) to 5.0 (Executive VP/C-Suite)
    is_hard_gate: bool = True           # Must be satisfied for promotion/readiness
    weight: float = 1.0


@dataclass(frozen=True)
class CompetencyAssessment:
    """Calculated evidence score for a specific competency."""
    competency_id: str
    name: str
    observed_score: float               # e.g., 3.7 / 5.0
    required_score: float               # e.g., 4.0 / 5.0
    gap: float                          # required - observed
    evidence_items: Tuple[EvidenceRef, ...]
    is_satisfied: bool
    confidence: float


class CompetencyEvidenceEngine:
    """
    Deterministic calculator of user competency readiness based on observed evidence.
    """

    @staticmethod
    def calculate_readiness_score(
        requirements: List[CompetencyRequirement],
        assessments: List[CompetencyAssessment]
    ) -> Tuple[float, List[str], List[str]]:
        """
        Calculates overall role readiness (0.0 to 1.0), lists met competencies,
        and flags remaining critical bottlenecks.
        """
        if not requirements:
            return 1.0, [], []
            
        assessment_map = {a.competency_id: a for a in assessments}
        
        total_weight = 0.0
        weighted_score = 0.0
        met_competencies = []
        bottlenecks = []
        
        for req in requirements:
            total_weight += req.weight
            assess = assessment_map.get(req.competency_id)
            
            if assess:
                # Score capped at 1.0 ratio per competency
                ratio = min(1.0, assess.observed_score / max(0.1, req.required_level))
                weighted_score += ratio * req.weight
                
                if assess.observed_score >= req.required_level:
                    met_competencies.append(f"{req.name} ({assess.observed_score:.1f}/{req.required_level:.1f})")
                else:
                    bottlenecks.append(f"{req.name} gap: {assess.observed_score:.1f}/{req.required_level:.1f} (need +{req.required_level - assess.observed_score:.1f})")
            else:
                bottlenecks.append(f"{req.name}: No verified evidence (0.0/{req.required_level:.1f})")
                
        readiness_pct = (weighted_score / total_weight) * 100.0 if total_weight > 0 else 0.0
        return readiness_pct, met_competencies, bottlenecks
