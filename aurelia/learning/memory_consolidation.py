"""
Aurelia Cognitive OS V3 - Phase 10: Memory Consolidation
========================================================
Consolidates memories from working memory to long-term storage.

Memory consolidation moves important information from working memory
to appropriate long-term memory systems (episodic, semantic, procedural, strategic).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class ConsolidationType(Enum):
    """Types of memory consolidation."""
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    STRATEGIC = "strategic"


class ConsolidationPriority(Enum):
    """Priority levels for consolidation."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ConsolidationCandidate:
    """
    A memory candidate for consolidation.
    
    Represents information that could be consolidated to long-term memory.
    """
    id: str
    content: Any
    source_memory_type: str  # "working", "episodic", etc.
    importance_score: float  # 0-1 scale
    access_count: int
    last_accessed: datetime
    created_at: datetime
    consolidation_type: Optional[ConsolidationType] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsolidationResult:
    """
    Result of a memory consolidation operation.
    
    Contains information about what was consolidated and where.
    """
    candidate_id: str
    success: bool
    target_memory_type: ConsolidationType
    consolidated_id: Optional[str]
    confidence: float
    reason: str


class MemoryConsolidator:
    """
    Consolidates memories from working memory to long-term storage.
    
    The memory consolidator:
    - Identifies important memories for consolidation
    - Determines appropriate target memory systems
    - Performs consolidation operations
    - Tracks consolidation history
    """
    
    def __init__(self):
        self.candidates: Dict[str, ConsolidationCandidate] = []
        self.consolidation_history: List[ConsolidationResult] = []
        self.candidate_counter = 0
    
    def add_candidate(
        self,
        content: Any,
        source_memory_type: str,
        importance_score: float,
        access_count: int = 1,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConsolidationCandidate:
        """Add a memory consolidation candidate."""
        candidate_id = f"candidate_{self.candidate_counter}"
        
        candidate = ConsolidationCandidate(
            id=candidate_id,
            content=content,
            source_memory_type=source_memory_type,
            importance_score=importance_score,
            access_count=access_count,
            last_accessed=datetime.now(),
            created_at=datetime.now(),
            metadata=metadata or {}
        )
        
        self.candidates.append(candidate)
        self.candidate_counter += 1
        
        return candidate
    
    def determine_consolidation_type(self, candidate: ConsolidationCandidate) -> ConsolidationType:
        """
        Determine the appropriate consolidation type for a candidate.
        
        Analyzes the candidate's content and characteristics to decide
        which long-term memory system it should be consolidated to.
        """
        # Simple logic based on content type and importance
        if isinstance(candidate.content, dict):
            # Check for strategic patterns
            if candidate.importance_score > 0.8:
                return ConsolidationType.STRATEGIC
            # Check for semantic facts
            elif "fact" in candidate.metadata.get("type", "").lower():
                return ConsolidationType.SEMANTIC
            # Check for procedures
            elif "procedure" in candidate.metadata.get("type", "").lower():
                return ConsolidationType.PROCEDURAL
            else:
                return ConsolidationType.EPISODIC
        else:
            # Default to episodic for simple content
            return ConsolidationType.EPISODIC
    
    def calculate_consolidation_priority(self, candidate: ConsolidationCandidate) -> ConsolidationPriority:
        """Calculate consolidation priority based on importance and access patterns."""
        # Priority based on importance score and access count
        combined_score = candidate.importance_score + (candidate.access_count * 0.05)
        combined_score = min(1.0, combined_score)
        
        if combined_score >= 0.9:
            return ConsolidationPriority.CRITICAL
        elif combined_score >= 0.7:
            return ConsolidationPriority.HIGH
        elif combined_score >= 0.5:
            return ConsolidationPriority.MEDIUM
        else:
            return ConsolidationPriority.LOW
    
    def consolidate(self, candidate_id: str) -> ConsolidationResult:
        """
        Consolidate a memory candidate to long-term storage.
        
        Moves the candidate to the appropriate long-term memory system.
        """
        candidate = self.get_candidate(candidate_id)
        if not candidate:
            return ConsolidationResult(
                candidate_id=candidate_id,
                success=False,
                target_memory_type=ConsolidationType.EPISODIC,
                consolidated_id=None,
                confidence=0.0,
                reason="Candidate not found"
            )
        
        # Determine consolidation type
        consolidation_type = self.determine_consolidation_type(candidate)
        
        # Calculate confidence in consolidation decision
        confidence = self._calculate_consolidation_confidence(candidate, consolidation_type)
        
        # In full system, would actually move to the appropriate memory system
        # For now, simulate successful consolidation
        consolidated_id = f"{consolidation_type.value}_{candidate_id}"
        
        result = ConsolidationResult(
            candidate_id=candidate_id,
            success=True,
            target_memory_type=consolidation_type,
            consolidated_id=consolidated_id,
            confidence=confidence,
            reason=f"Consolidated to {consolidation_type.value} memory"
        )
        
        self.consolidation_history.append(result)
        
        # Remove candidate from list after successful consolidation
        if result.success:
            self.candidates = [c for c in self.candidates if c.id != candidate_id]
        
        return result
    
    def _calculate_consolidation_confidence(self, candidate: ConsolidationCandidate, consolidation_type: ConsolidationType) -> float:
        """Calculate confidence in consolidation decision."""
        # Base confidence based on importance
        base_confidence = candidate.importance_score
        
        # Adjust based on access count
        access_bonus = min(0.1, candidate.access_count * 0.02)
        
        return min(1.0, base_confidence + access_bonus)
    
    def get_candidates_by_priority(self, priority: ConsolidationPriority) -> List[ConsolidationCandidate]:
        """Get all candidates with a specific priority."""
        return [c for c in self.candidates if self.calculate_consolidation_priority(c) == priority]
    
    def get_candidate(self, candidate_id: str) -> Optional[ConsolidationCandidate]:
        """Get a candidate by ID."""
        for candidate in self.candidates:
            if candidate.id == candidate_id:
                return candidate
        return None
    
    def get_consolidation_history(self, limit: int = 10) -> List[ConsolidationResult]:
        """Get recent consolidation results."""
        return self.consolidation_history[-limit:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the memory consolidator state."""
        return {
            "total_candidates": len(self.candidates),
            "total_consolidations": len(self.consolidation_history),
            "successful_consolidations": len([r for r in self.consolidation_history if r.success]),
            "by_priority": {
                priority.value: len(self.get_candidates_by_priority(priority))
                for priority in ConsolidationPriority
            }
        }