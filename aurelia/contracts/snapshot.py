"""
Aurelia Cognitive OS V4 - Immutable Cognitive Snapshot
======================================================
Every cognitive cycle operates on a single versioned, immutable snapshot
of facts, memory, knowledge, and goals to guarantee zero state drift.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Tuple, Any, Optional
from aurelia.contracts.core_types import Fact, UserGoal, Inference, UserPreference
from aurelia.contracts.meaning_frame import MeaningFrame


@dataclass(frozen=True)
class DataFreshnessRecord:
    """Tracks age and provenance of local knowledge packs."""
    pack_name: str
    version: str
    age_days: int
    is_stale: bool = False
    warning_message: Optional[str] = None


@dataclass(frozen=True)
class CognitiveSnapshot:
    """
    Immutable versioned state for a single cognitive cycle.
    Guarantees that all specialists, solvers, and reasoning models
    evaluate against identical world and user states.
    """
    snapshot_id: str
    created_at: datetime
    meaning: MeaningFrame
    
    # User Profile & History Snapshot
    user_id: str
    current_role: str
    current_level: str
    years_experience: float
    active_goals: Tuple[UserGoal, ...]
    user_preferences: Tuple[UserPreference, ...]
    
    # Verified Facts & Inferences
    verified_facts: Tuple[Fact, ...]
    active_inferences: Tuple[Inference, ...]
    
    # Relevant Memory Items
    episodic_memories: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    semantic_insights: Tuple[str, ...] = field(default_factory=tuple)
    
    # Knowledge Provenance & Freshness
    knowledge_versions: Dict[str, str] = field(default_factory=dict)
    data_freshness: Tuple[DataFreshnessRecord, ...] = field(default_factory=tuple)
    
    # Deterministic Execution Anchor
    deterministic_seed: int = 42
