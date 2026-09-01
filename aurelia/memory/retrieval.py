"""
Aurelia Cognitive OS V4 - Hybrid Evidence & Memory Retriever
=============================================================
Combines lexical matching, entity overlap, temporal proximity,
active goal relevance, and evidence quality into an explicit composite score.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Tuple, Any, Optional
from aurelia.contracts.core_types import EvidenceRef, Fact, UserGoal


@dataclass(frozen=True)
class RetrievedMemoryItem:
    """A scored memory or evidence item returned by hybrid retrieval."""
    item_id: str
    content: str
    composite_score: float
    lexical_score: float
    entity_score: float
    temporal_score: float
    goal_relevance_score: float
    evidence_quality: float
    source_type: str


class HybridMemoryRetriever:
    """
    Multi-dimensional evidence and memory retriever.
    Never relies on isolated raw embeddings; uses explicit multi-signal scoring.
    """

    @classmethod
    def retrieve(
        cls,
        query_text: str,
        query_entities: List[str],
        active_goal: Optional[UserGoal],
        candidate_items: List[Dict[str, Any]],
        now: Optional[datetime] = None,
        top_k: int = 5
    ) -> List[RetrievedMemoryItem]:
        """
        Ranks candidate memory items across 5 weighted dimensions.
        """
        current_time = now or datetime.now(timezone.utc)
        query_lower = query_text.lower()
        query_tokens = set(query_lower.split())
        
        results: List[RetrievedMemoryItem] = []
        
        for item in candidate_items:
            content = str(item.get("content", ""))
            content_lower = content.lower()
            content_tokens = set(content_lower.split())
            
            # 1. Lexical Overlap Score (0.0 to 1.0)
            overlap = query_tokens.intersection(content_tokens)
            lexical_score = len(overlap) / max(1, len(query_tokens))
            
            # 2. Entity Overlap Score (0.0 to 1.0)
            matched_entities = [e for e in query_entities if e.lower() in content_lower]
            entity_score = len(matched_entities) / max(1, len(query_entities)) if query_entities else 0.5
            
            # 3. Temporal Relevance Score (Decays smoothly over 180 days)
            item_time = item.get("timestamp") or current_time
            age_days = (current_time - item_time).total_seconds() / 86400.0
            temporal_score = max(0.2, 1.0 - (age_days / 180.0))
            
            # 4. Active Goal Relevance Score (0.0 to 1.0)
            goal_relevance = 0.5
            if active_goal:
                if active_goal.target_role.lower() in content_lower:
                    goal_relevance = 1.0
                elif any(c.lower() in content_lower for c in active_goal.success_conditions):
                    goal_relevance = 0.85
                    
            # 5. Evidence Quality Weight
            evidence_weight = float(item.get("reliability_weight", 0.70))
            
            # Composite Scoring Formula
            composite = (
                (lexical_score * 0.30) +
                (entity_score * 0.25) +
                (temporal_score * 0.15) +
                (goal_relevance * 0.15) +
                (evidence_weight * 0.15)
            )
            
            results.append(RetrievedMemoryItem(
                item_id=str(item.get("id", "mem_unknown")),
                content=content,
                composite_score=composite,
                lexical_score=lexical_score,
                entity_score=entity_score,
                temporal_score=temporal_score,
                goal_relevance_score=goal_relevance,
                evidence_quality=evidence_weight,
                source_type=str(item.get("source_type", "general_memory"))
            ))
            
        # Sort descending by composite score
        results.sort(key=lambda x: x.composite_score, reverse=True)
        return results[:top_k]
