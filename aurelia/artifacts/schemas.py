"""
Aurelia Cognitive OS V4 - Artifact Workspace Schemas & Lineage
===============================================================
Defines typed, versioned executive artifacts with causal lineage.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Tuple, Optional, Any


class ArtifactType(Enum):
    ROADMAP_90_DAY = "roadmap_90_day"
    NEGOTIATION_SCRIPT = "negotiation_script"
    DECISION_MATRIX = "decision_matrix"
    STAR_CARD = "star_card"
    STAKEHOLDER_MAP = "stakeholder_map"


@dataclass(frozen=True)
class ArtifactMilestone:
    """A milestone in an executive roadmap."""
    id: str
    phase_name: str                     # e.g., "Days 1-30: Discover & Audit"
    goal: str
    actions: Tuple[str, ...]
    deliverables: Tuple[str, ...]
    is_completed: bool = False


@dataclass(frozen=True)
class ExecutiveArtifact:
    """Base container for a versioned executive artifact with causal lineage."""
    artifact_id: str
    artifact_type: ArtifactType
    title: str
    version: int
    created_from_decision_id: str
    updated_from_event_id: Optional[str]
    payload: Dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ArtifactWorkspaceCompiler:
    """
    Builds, versions, and applies delta-updates to executive artifacts.
    """

    @classmethod
    def create_90_day_roadmap(
        cls,
        artifact_id: str,
        title: str,
        decision_id: str,
        milestones: List[ArtifactMilestone]
    ) -> ExecutiveArtifact:
        """Compiles a new 90-Day Transition Roadmap."""
        payload = {
            "milestones": [
                {
                    "id": m.id,
                    "phase_name": m.phase_name,
                    "goal": m.goal,
                    "actions": list(m.actions),
                    "deliverables": list(m.deliverables),
                    "is_completed": m.is_completed
                }
                for m in milestones
            ]
        }
        return ExecutiveArtifact(
            artifact_id=artifact_id,
            artifact_type=ArtifactType.ROADMAP_90_DAY,
            title=title,
            version=1,
            created_from_decision_id=decision_id,
            updated_from_event_id=None,
            payload=payload
        )

    @classmethod
    def update_milestone_status(
        cls,
        existing: ExecutiveArtifact,
        milestone_id: str,
        is_completed: bool,
        event_id: str
    ) -> ExecutiveArtifact:
        """
        Applies a clean delta-update to an existing artifact without rewriting it.
        Increments the version number and preserves lineage.
        """
        new_payload = dict(existing.payload)
        milestones = new_payload.get("milestones", [])
        
        for m in milestones:
            if m.get("id") == milestone_id:
                m["is_completed"] = is_completed
                break
                
        return ExecutiveArtifact(
            artifact_id=existing.artifact_id,
            artifact_type=existing.artifact_type,
            title=existing.title,
            version=existing.version + 1,
            created_from_decision_id=existing.created_from_decision_id,
            updated_from_event_id=event_id,
            payload=new_payload
        )
