"""
Aurelia Cognitive OS V5 - Artifact Dependency Graph & Staleness Engine
======================================================================
Maintains a causal dependency DAG between active goals, executive artifacts,
and underlying facts, automatically invalidating stale deliverables upon upstream changes.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Set, Optional, Tuple
from aurelia.contracts.v5_contracts import StalenessStatus, ArtifactStalenessRecord


@dataclass
class ArtifactDependencyNode:
    """Node representing an artifact and its upstream dependencies."""
    artifact_id: str
    title: str
    goal_id: str
    dependent_fact_keys: Set[str] # e.g. {"team_size", "current_role", "market_target"}
    status: StalenessStatus = StalenessStatus.FRESH
    stale_reason: Optional[str] = None
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ArtifactDependencyGraph:
    """
    Manages artifact-to-fact dependency graph and propagates staleness triggers.
    """

    def __init__(self):
        self.nodes: Dict[str, ArtifactDependencyNode] = {}
        self.staleness_records: List[ArtifactStalenessRecord] = []

    def register_artifact(
        self,
        artifact_id: str,
        title: str,
        goal_id: str,
        dependent_fact_keys: Set[str]
    ) -> ArtifactDependencyNode:
        """Registers an artifact with its prerequisite fact dependencies."""
        node = ArtifactDependencyNode(
            artifact_id=artifact_id,
            title=title,
            goal_id=goal_id,
            dependent_fact_keys=dependent_fact_keys,
            status=StalenessStatus.FRESH
        )
        self.nodes[artifact_id] = node
        return node

    def trigger_fact_update(
        self,
        modified_fact_key: str,
        new_value: Any,
        triggering_event_id: str = "evt_manual_edit"
    ) -> List[ArtifactStalenessRecord]:
        """
        Traverses the graph, marks all dependent artifacts as STALE,
        and logs explicit causal reasons.
        """
        affected_records: List[ArtifactStalenessRecord] = []

        for art_id, node in self.nodes.items():
            if modified_fact_key in node.dependent_fact_keys and node.status == StalenessStatus.FRESH:
                reason = f"Upstream fact '{modified_fact_key}' was modified to '{new_value}'."
                node.status = StalenessStatus.STALE
                node.stale_reason = reason

                rec = ArtifactStalenessRecord(
                    artifact_id=art_id,
                    status=StalenessStatus.STALE,
                    stale_reason=reason,
                    triggering_event_id=triggering_event_id,
                    detected_at=datetime.now(timezone.utc)
                )
                self.staleness_records.append(rec)
                affected_records.append(rec)

        return affected_records

    def revalidate_artifact(
        self,
        artifact_id: str
    ) -> bool:
        """Marks a revised artifact as FRESH again."""
        if artifact_id in self.nodes:
            self.nodes[artifact_id].status = StalenessStatus.FRESH
            self.nodes[artifact_id].stale_reason = None
            self.nodes[artifact_id].last_updated = datetime.now(timezone.utc)
            return True
        return False
