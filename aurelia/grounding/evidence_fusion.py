"""
Aurelia Cognitive OS V6 - Source Dependence Graph & Evidence Fusion
====================================================================
Maintains causal origin DAGs and prevents false confidence multiplication
when multiple observations derive from the same root source.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Set, Tuple
from aurelia.contracts.v6_contracts import (
    SourceDependencyRecord,
    ObservationSource
)


@dataclass(frozen=True)
class FusedEvidence:
    """Consolidated multimodal evidence item with root source count."""
    claim: str
    fused_confidence: float
    independent_root_sources_count: int
    derived_observation_ids: Tuple[str, ...]
    is_multi_source_verified: bool


class SourceDependenceGraph:
    """
    Tracks lineage from root sources to derived observations.
    """

    def __init__(self):
        # root_source_id -> Set of observation_ids
        self.root_to_derived: Dict[str, Set[str]] = {}
        # observation_id -> root_source_id
        self.derived_to_root: Dict[str, str] = {}

    def register_observation(
        self,
        observation_id: str,
        root_source_id: str,
        source_type: ObservationSource
    ) -> SourceDependencyRecord:
        """Registers observation under its root source."""
        if root_source_id not in self.root_to_derived:
            self.root_to_derived[root_source_id] = set()
        self.root_to_derived[root_source_id].add(observation_id)
        self.derived_to_root[observation_id] = root_source_id

        return SourceDependencyRecord(
            root_source_id=root_source_id,
            derived_observation_ids=tuple(self.root_to_derived[root_source_id]),
            root_source_type=source_type,
            is_composite=len(self.root_to_derived[root_source_id]) > 1
        )

    def get_root_source(self, observation_id: str) -> Optional[str]:
        return self.derived_to_root.get(observation_id)


class EvidenceFusionEngine:
    """
    Fuses confidence scores across observations while enforcing independence guards.
    """

    @classmethod
    def fuse_evidence(
        cls,
        claim: str,
        observations: List[Tuple[str, float, str]], # (obs_id, confidence, root_source_id)
    ) -> FusedEvidence:
        """
        Fuses confidence. Observations with identical root_source_id are grouped
        by max(confidence) rather than compounded.
        """
        if not observations:
            return FusedEvidence(claim, 0.0, 0, (), False)

        # 1. Group by root_source_id
        source_confidences: Dict[str, float] = {}
        obs_ids = []

        for oid, conf, root_id in observations:
            obs_ids.append(oid)
            current_max = source_confidences.get(root_id, 0.0)
            source_confidences[root_id] = max(current_max, conf)

        # 2. Independent source fusion: P_fused = 1 - prod(1 - P_i)
        independent_count = len(source_confidences)
        unconfidence = 1.0
        for root_id, root_conf in source_confidences.items():
            unconfidence *= (1.0 - root_conf)

        fused_conf = 1.0 - unconfidence
        is_verified = (independent_count >= 2 and fused_conf >= 0.90)

        return FusedEvidence(
            claim=claim,
            fused_confidence=round(min(0.99, fused_conf), 3),
            independent_root_sources_count=independent_count,
            derived_observation_ids=tuple(obs_ids),
            is_multi_source_verified=is_verified
        )
