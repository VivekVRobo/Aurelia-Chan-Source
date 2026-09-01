"""
Aurelia Cognitive OS V6 - Attention, Relevance & Purpose Limitation Engine
==========================================================================
Enforces purpose limitation on perception requests and calculates multi-factor
attention scores to filter background noise from the cognitive snapshot.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from aurelia.contracts.v6_contracts import Modality


@dataclass(frozen=True)
class PerceptionRequest:
    """Explicit purpose-bound request for environmental perception."""
    request_id: str
    modality: Modality
    purpose: str # e.g. "resolve_user_reference", "audit_salary_field", "extract_traceback"
    requested_regions: Optional[Tuple[str, ...]] = None # Bounding region IDs or page numbers
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class AttentionScore:
    """Multi-factor relevance measurement for snapshot promotion."""
    recency: float            # 0.0 to 1.0 (temporal proximity)
    user_interaction: float   # 0.0 to 1.0 (foreground focus, click, typing)
    semantic_relevance: float # 0.0 to 1.0 (similarity to user prompt/active goal)
    composite_score: float    # 0.0 to 1.0
    passes_threshold: bool


class AttentionEngine:
    """
    Evaluates attention scores and gates snapshot injection.
    """

    @classmethod
    def calculate_attention(
        cls,
        recency: float,
        user_interaction: float,
        semantic_relevance: float,
        threshold: float = 0.65
    ) -> AttentionScore:
        """
        Computes composite attention: 0.40*recency + 0.35*interaction + 0.25*relevance.
        """
        rec = max(0.0, min(1.0, recency))
        inter = max(0.0, min(1.0, user_interaction))
        rel = max(0.0, min(1.0, semantic_relevance))

        composite = (0.40 * rec) + (0.35 * inter) + (0.25 * rel)
        passes = composite >= threshold

        return AttentionScore(
            recency=round(rec, 3),
            user_interaction=round(inter, 3),
            semantic_relevance=round(rel, 3),
            composite_score=round(composite, 3),
            passes_threshold=passes
        )
