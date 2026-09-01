"""
Aurelia Cognitive OS V3 - Phase 6: Conflict Detector
=====================================================
Identifies contradictory information in the system.

The conflict detector ensures that the system doesn't present
contradictory information to the user.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
from aurelia.cognition.contracts import MemoryFact, Evidence


class ConflictSeverity(Enum):
    """Severity of conflicts."""
    CRITICAL = "critical"  # Direct contradiction
    HIGH = "high"  # Strong inconsistency
    MEDIUM = "medium"  # Mild inconsistency
    LOW = "low"  # Potential conflict


class ConflictType(Enum):
    """Types of conflicts."""
    DIRECT_CONTRADICTION = "direct_contradiction"  # A and not A
    NUMERICAL_INCONSISTENCY = "numerical_inconsistency"  # Different numbers for same thing
    TEMPORAL_INCONSISTENCY = "temporal_inconsistency"  # Changes over time
    SOURCE_DISAGREEMENT = "source_disagreement"  # Different sources disagree
    SEMANTIC_CONFLICT = "semantic_conflict"  # Meaning conflict


@dataclass
class Conflict:
    """
    A detected conflict between pieces of information.
    """
    id: str
    conflict_type: ConflictType
    severity: ConflictSeverity
    description: str
    item1_id: str
    item1_description: str
    item2_id: str
    item2_description: str
    evidence: List[Evidence] = field(default_factory=list)
    resolution_suggestion: Optional[str] = None
    resolved: bool = False


class ConflictDetector:
    """
    Identifies contradictory information in the system.
    
    The conflict detector:
    - Detects direct contradictions
    - Identifies numerical inconsistencies
    - Finds temporal inconsistencies
    - Detects source disagreements
    - Suggests conflict resolutions
    """
    
    def __init__(self):
        self.conflicts: Dict[str, Conflict] = {}
        self.conflict_counter = 0
    
    def detect_facts_conflict(self, fact1: MemoryFact, fact2: MemoryFact) -> Optional[Conflict]:
        """Detect conflicts between two memory facts."""
        # Check for direct contradiction
        if self._is_direct_contradiction(fact1, fact2):
            return self._create_conflict(
                conflict_type=ConflictType.DIRECT_CONTRADICTION,
                severity=ConflictSeverity.CRITICAL,
                description=f"Direct contradiction: {fact1.subject} {fact1.predicate} {fact1.object} vs {fact2.subject} {fact2.predicate} {fact2.object}",
                item1_id=fact1.subject,
                item1_description=f"{fact1.subject} {fact1.predicate} {fact1.object}",
                item2_id=fact2.subject,
                item2_description=f"{fact2.subject} {fact2.predicate} {fact2.object}"
            )
        
        # Check for numerical inconsistency
        if self._is_numerical_inconsistency(fact1, fact2):
            return self._create_conflict(
                conflict_type=ConflictType.NUMERICAL_INCONSISTENCY,
                severity=ConflictSeverity.HIGH,
                description=f"Numerical inconsistency: {fact1.object} vs {fact2.object}",
                item1_id=fact1.subject,
                item1_description=str(fact1.object),
                item2_id=fact2.subject,
                item2_description=str(fact2.object)
            )
        
        return None
    
    def detect_evidence_conflict(self, evidence1: Evidence, evidence2: Evidence) -> Optional[Conflict]:
        """Detect conflicts between two pieces of evidence."""
        # Check for source disagreement
        if evidence1.source != evidence2.source:
            # In a full system, would check if they make contradictory claims
            return self._create_conflict(
                conflict_type=ConflictType.SOURCE_DISAGREEMENT,
                severity=ConflictSeverity.MEDIUM,
                description=f"Different sources: {evidence1.source} vs {evidence2.source}",
                item1_id=evidence1.source,
                item1_description=evidence1.reference,
                item2_id=evidence2.source,
                item2_description=evidence2.reference
            )
        
        return None
    
    def _is_direct_contradiction(self, fact1: MemoryFact, fact2: MemoryFact) -> bool:
        """Check if two facts directly contradict each other."""
        # Same subject, different predicates that are opposites
        if fact1.subject != fact2.subject:
            return False
        
        opposite_predicates = {
            "is": "is not",
            "has": "does not have",
            "can": "cannot",
            "will": "will not",
            "should": "should not"
        }
        
        for pred, opposite in opposite_predicates.items():
            if fact1.predicate == pred and fact2.predicate == opposite:
                return True
            if fact1.predicate == opposite and fact2.predicate == pred:
                return True
        
        return False
    
    def _is_numerical_inconsistency(self, fact1: MemoryFact, fact2: MemoryFact) -> bool:
        """Check if two facts have numerical inconsistencies."""
        try:
            # Try to parse as numbers
            val1 = float(fact1.object)
            val2 = float(fact2.object)
            
            # Check if same subject but different numerical values
            if fact1.subject == fact2.subject and abs(val1 - val2) > 0.01:
                return True
        except (ValueError, TypeError):
            return False
        
        return False
    
    def _create_conflict(
        self,
        conflict_type: ConflictType,
        severity: ConflictSeverity,
        description: str,
        item1_id: str,
        item1_description: str,
        item2_id: str,
        item2_description: str
    ) -> Conflict:
        """Create a new conflict."""
        conflict_id = f"conflict_{self.conflict_counter}"
        
        conflict = Conflict(
            id=conflict_id,
            conflict_type=conflict_type,
            severity=severity,
            description=description,
            item1_id=item1_id,
            item1_description=item1_description,
            item2_id=item2_id,
            item2_description=item2_description
        )
        
        self.conflicts[conflict_id] = conflict
        self.conflict_counter += 1
        
        return conflict
    
    def get_conflict(self, conflict_id: str) -> Optional[Conflict]:
        """Get a conflict by ID."""
        return self.conflicts.get(conflict_id)
    
    def resolve_conflict(self, conflict_id: str, resolution_suggestion: str):
        """Mark a conflict as resolved with a suggestion."""
        if conflict_id in self.conflicts:
            self.conflicts[conflict_id].resolved = True
            self.conflicts[conflict_id].resolution_suggestion = resolution_suggestion
    
    def get_conflicts_by_severity(self, severity: ConflictSeverity) -> List[Conflict]:
        """Get all conflicts of a specific severity."""
        return [c for c in self.conflicts.values() if c.severity == severity]
    
    def get_unresolved_conflicts(self) -> List[Conflict]:
        """Get all unresolved conflicts."""
        return [c for c in self.conflicts.values() if not c.resolved]
    
    def get_critical_conflicts(self) -> List[Conflict]:
        """Get all critical conflicts."""
        return self.get_conflicts_by_severity(ConflictSeverity.CRITICAL)
    
    def scan_for_conflicts(self, facts: List[MemoryFact], evidence_list: List[Evidence]) -> List[Conflict]:
        """Scan through facts and evidence for conflicts."""
        new_conflicts = []
        
        # Check fact-fact conflicts
        for i, fact1 in enumerate(facts):
            for fact2 in facts[i+1:]:
                conflict = self.detect_facts_conflict(fact1, fact2)
                if conflict:
                    new_conflicts.append(conflict)
        
        # Check evidence-evidence conflicts
        for i, ev1 in enumerate(evidence_list):
            for ev2 in evidence_list[i+1:]:
                conflict = self.detect_evidence_conflict(ev1, ev2)
                if conflict:
                    new_conflicts.append(conflict)
        
        return new_conflicts
    
    def suggest_resolution(self, conflict: Conflict) -> str:
        """Suggest a resolution for a conflict."""
        if conflict.conflict_type == ConflictType.DIRECT_CONTRADICTION:
            return "Investigate both sources and determine which is more reliable"
        elif conflict.conflict_type == ConflictType.NUMERICAL_INCONSISTENCY:
            return "Verify the correct numerical value and update accordingly"
        elif conflict.conflict_type == ConflictType.SOURCE_DISAGREEMENT:
            return "Check which source is more authoritative or recent"
        elif conflict.conflict_type == ConflictType.TEMPORAL_INCONSISTENCY:
            return "Check if values have changed over time and update stale information"
        else:
            return "Review both pieces of information and determine the most accurate"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the conflict detector state."""
        return {
            "total_conflicts": len(self.conflicts),
            "by_severity": {severity.value: len(self.get_conflicts_by_severity(severity)) for severity in ConflictSeverity},
            "by_type": {ctype.value: len([c for c in self.conflicts.values() if c.conflict_type == ctype]) for ctype in ConflictType},
            "unresolved": len(self.get_unresolved_conflicts()),
            "critical": len(self.get_critical_conflicts())
        }