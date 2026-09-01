"""
Aurelia Cognitive OS V6 - Multimodal Perception Contracts & Invariants
=======================================================================
Immutable data types governing environmental observation, multimodal grounding,
provenance, quality scoring, source-dependency, and transactional promotion.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Tuple, Optional, Set
import uuid


class Modality(str, Enum):
    """Supported input perception modalities."""
    SCREEN = "SCREEN"
    AUDIO = "AUDIO"
    DOCUMENT = "DOCUMENT"
    SYSTEM_STATE = "SYSTEM_STATE"
    USER_INTERACTION = "USER_INTERACTION"


class ObservationSource(str, Enum):
    """Hierarchical perception acquisition sources."""
    OS_METADATA = "OS_METADATA"                     # Tier 0
    ACCESSIBILITY_TREE = "ACCESSIBILITY_TREE"       # Tier 1
    STRUCTURED_DOCUMENT = "STRUCTURED_DOCUMENT"     # Tier 2
    OCR_EXTRACTOR = "OCR_EXTRACTOR"                 # Tier 2.5
    LIGHT_VISION = "LIGHT_VISION"                   # Tier 3
    DEEP_VISION = "DEEP_VISION"                     # Tier 4
    SPEECH_TRANSCRIBER = "SPEECH_TRANSCRIBER"
    PROSODY_ANALYZER = "PROSODY_ANALYZER"
    USER_EXPLICIT = "USER_EXPLICIT"


class PrivacyClass(str, Enum):
    """Perception privacy sensitivity classification."""
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    RESTRICTED = "RESTRICTED"
    DENIED = "DENIED" # Pre-capture block (password managers, banking, incognito)


class ObservationPromotionStage(str, Enum):
    """Deterministic observation promotion lifecycle."""
    RAW_OBSERVATION = "RAW_OBSERVATION"
    NORMALIZED_OBSERVATION = "NORMALIZED_OBSERVATION"
    GROUNDED_OBSERVATION = "GROUNDED_OBSERVATION"
    EVIDENCE = "EVIDENCE"
    FACT_CANDIDATE = "FACT_CANDIDATE"
    WORLD_STATE_MEMORY = "WORLD_STATE_MEMORY"


class ConflictSeverity(str, Enum):
    """Cross-source discrepancy severity."""
    COSMETIC = "COSMETIC"     # e.g. minor whitespace / typo difference
    MINOR = "MINOR"           # e.g. team size 11 vs 12
    MATERIAL = "MATERIAL"     # e.g. ₹28L vs ₹38L compensation discrepancy
    CRITICAL = "CRITICAL"     # e.g. contradictory role offers or conflicting dates


class SessionMode(str, Enum):
    """Environmental perception capture mode."""
    OFF = "OFF"
    PUSH_TO_TALK = "PUSH_TO_TALK"
    CONVERSATION_SESSION = "CONVERSATION_SESSION"
    AMBIENT = "AMBIENT"


class EntityVisibility(str, Enum):
    """Visibility state of an observed UI/Screen entity."""
    CURRENTLY_VISIBLE = "CURRENTLY_VISIBLE"
    NOT_CURRENTLY_VISIBLE = "NOT_CURRENTLY_VISIBLE"
    OBSCURED = "OBSCURED"


class EntityExistence(str, Enum):
    """Ontological existence state independent of viewport visibility."""
    PERSISTENT = "PERSISTENT"
    TRANSIENT = "TRANSIENT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Provenance:
    """Causal lineage and physical location of an observation."""
    root_source_id: str
    source_type: ObservationSource
    file_path: Optional[str] = None
    page_or_region: Optional[str] = None
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ObservationQuality:
    """Multi-dimensional measurement of observation fidelity."""
    confidence: float          # 0.0 to 1.0 (model/sensor certainty)
    completeness: float        # 0.0 to 1.0 (fraction of visible entity captured)
    ambiguity: float           # 0.0 to 1.0 (presence of competing interpretations)
    source_reliability: float  # 0.0 to 1.0 (historical accuracy of source)
    freshness: float           # 0.0 to 1.0 (temporal decay score)


@dataclass(frozen=True)
class ObservedEntity:
    """Discrete entity discovered within an observation."""
    entity_id: str
    entity_type: str # e.g. "COMPENSATION_AMOUNT", "DEADLINE_DATE", "JOB_TITLE"
    raw_text: str
    normalized_value: Any
    bounding_box: Optional[Tuple[int, int, int, int]] = None # (x, y, w, h)
    confidence: float = 0.90


@dataclass(frozen=True)
class ObservedEntityState:
    """Tracks entity visibility vs persistence."""
    entity_id: str
    visibility: EntityVisibility
    existence: EntityExistence
    last_observed_at: datetime


@dataclass(frozen=True)
class ObservationPayload:
    """Parsed semantic content of an observation."""
    structured_data: Dict[str, Any]
    summary_text: str
    raw_token_count: int = 0


@dataclass(frozen=True)
class Observation:
    """Immutable discrete perception data point."""
    observation_id: str
    session_id: str
    modality: Modality
    source: ObservationSource
    observed_at: datetime
    expires_at: Optional[datetime] # Explicit TTL
    entities: Tuple[ObservedEntity, ...]
    content: ObservationPayload
    quality: ObservationQuality
    provenance: Provenance
    privacy_class: PrivacyClass
    stage: ObservationPromotionStage = ObservationPromotionStage.RAW_OBSERVATION


@dataclass(frozen=True)
class ObservationSession:
    """Bounded perception capture session with explicit consent and policies."""
    session_id: str
    mode: SessionMode
    allowed_modalities: Set[Modality]
    started_at: datetime
    retention_policy: str = "DISCARD_RAW_IMMEDIATELY"
    ended_at: Optional[datetime] = None


@dataclass(frozen=True)
class SourceDependencyRecord:
    """Lineage DAG tracking shared origins to prevent artificial confidence multiplication."""
    root_source_id: str
    derived_observation_ids: Tuple[str, ...]
    root_source_type: ObservationSource
    is_composite: bool


@dataclass(frozen=True)
class PerceptionReceipt:
    """Immutable audit trail for grounded perception and evidence promotion."""
    receipt_id: str
    session_id: str
    modality: Modality
    root_source_id: str
    raw_retained: bool
    observations_created: Tuple[str, ...]
    evidence_promoted: Tuple[str, ...]
    world_state_changes: Tuple[str, ...]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class ContextCandidate:
    """Single candidate environmental context for scene routing."""
    context_key: str # e.g. "vscode_python_debugging", "resume_audit", "salary_negotiation"
    description: str
    confidence_score: float # 0.0 to 1.0
    evidence_refs: Tuple[str, ...]


@dataclass(frozen=True)
class ContextCandidateSet:
    """Ranked set of environmental contexts with confidence separation."""
    candidates: Tuple[ContextCandidate, ...]
    separation_ratio: float # (Top - SecondTop) / Top
    selected_context: Optional[str]
    is_ambiguous: bool
