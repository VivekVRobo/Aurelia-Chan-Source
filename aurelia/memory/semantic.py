"""
Aurelia Cognitive OS V3 - Phase 4: Semantic Memory
================================================
Stable knowledge learned about the situation.

Semantic memory stores learned facts about the user that persist
across sessions, unlike episodic memory which stores specific events.

Examples:
- User has 6 years of project leadership
- Target role usually requires budget ownership
- Communication is currently a development area
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
from aurelia.cognition.contracts import MemoryFact, Evidence, FactTier


class KnowledgeCategory(Enum):
    """Categories of semantic knowledge."""
    SKILL = "skill"
    EXPERIENCE = "experience"
    PREFERENCE = "preference"
    CONSTRAINT = "constraint"
    GOAL = "goal"
    TREND = "trend"


@dataclass
class SemanticFact:
    """
    A fact in semantic memory.
    
    Unlike episodic events, semantic facts are stable knowledge
    derived from patterns in episodic memory.
    """
    id: str
    category: KnowledgeCategory
    subject: str
    predicate: str
    object: Any
    confidence: float
    evidence: List[Evidence]
    first_learned: datetime
    last_confirmed: datetime
    confirmation_count: int  # How many times this has been confirmed
    tier: FactTier = FactTier.C


class SemanticMemory:
    """
    Stable knowledge learned about the situation.
    
    Examples:
    - User has 6 years of project leadership
    - Target role usually requires budget ownership
    - Communication is currently a development area
    """
    
    def __init__(self):
        self.facts: Dict[str, SemanticFact] = {}  # fact_id -> SemanticFact
        self.fact_counter = 0
    
    def add_fact(self, fact: SemanticFact):
        """Add a semantic fact."""
        self.facts[fact.id] = fact
        self.fact_counter += 1
    
    def create_fact(
        self,
        category: KnowledgeCategory,
        subject: str,
        predicate: str,
        obj: Any,
        confidence: float,
        evidence: List[Evidence],
        tier: FactTier = FactTier.C
    ) -> SemanticFact:
        """Create and add a new semantic fact."""
        fact_id = f"fact_{self.fact_counter}"
        
        fact = SemanticFact(
            id=fact_id,
            category=category,
            subject=subject,
            predicate=predicate,
            object=obj,
            confidence=confidence,
            evidence=evidence,
            first_learned=datetime.now(),
            last_confirmed=datetime.now(),
            confirmation_count=1,
            tier=tier
        )
        
        self.add_fact(fact)
        return fact
    
    def confirm_fact(self, fact_id: str):
        """Confirm an existing fact (increases confidence)."""
        if fact_id in self.facts:
            fact = self.facts[fact_id]
            fact.last_confirmed = datetime.now()
            fact.confirmation_count += 1
            # Increase confidence with each confirmation
            fact.confidence = min(1.0, fact.confidence + 0.05)
    
    def get_fact(self, fact_id: str) -> Optional[SemanticFact]:
        """Get a fact by ID."""
        return self.facts.get(fact_id)
    
    def get_facts_by_subject(self, subject: str) -> List[SemanticFact]:
        """Get all facts about a specific subject."""
        return [f for f in self.facts.values() if f.subject == subject]
    
    def get_facts_by_category(self, category: KnowledgeCategory) -> List[SemanticFact]:
        """Get all facts in a category."""
        return [f for f in self.facts.values() if f.category == category]
    
    def get_facts_by_tier(self, tier: FactTier) -> List[SemanticFact]:
        """Get all facts of a specific tier."""
        return [f for f in self.facts.values() if f.tier == tier]
    
    def query(self, subject: Optional[str] = None, predicate: Optional[str] = None, obj: Optional[Any] = None) -> List[SemanticFact]:
        """
        Query semantic memory flexibly.
        
        Can query by subject, predicate, object, or combination.
        """
        results = []
        
        for fact in self.facts.values():
            match = True
            
            if subject is not None and fact.subject != subject:
                match = False
            if predicate is not None and fact.predicate != predicate:
                match = False
            if obj is not None and fact.object != obj:
                match = False
            
            if match:
                results.append(fact)
        
        return results
    
    def get_high_confidence_facts(self, min_confidence: float = 0.8) -> List[SemanticFact]:
        """Get facts with confidence above threshold."""
        return [f for f in self.facts.values() if f.confidence >= min_confidence]
    
    def get_facts_by_recency(self, days: int = 30) -> List[SemanticFact]:
        """Get facts confirmed within the last N days."""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)
        return [f for f in self.facts.values() if f.last_confirmed >= cutoff]
    
    def consolidate_from_episodic(self, episodic_patterns: Dict[str, int], min_occurrences: int = 3):
        """
        Consolidate repeated episodic patterns into semantic facts.
        
        Example:
        Episode 1: interview weak on metrics
        Episode 2: interview weak on metrics
        Episode 3: interview weak on metrics
        
        Consolidates into:
        Development trend: quantified outcomes need improvement
        """
        new_facts = []
        
        for pattern, count in episodic_patterns.items():
            if count >= min_occurrences:
                # This pattern is stable - create semantic fact
                if "interview" in pattern and "scored" in pattern:
                    # Interview scoring happened multiple times
                    fact = self.create_fact(
                        category=KnowledgeCategory.TREND,
                        subject="user",
                        predicate="has_interview_experience",
                        obj=True,
                        confidence=min(0.9, 0.5 + (count * 0.1)),
                        evidence=[],
                        tier=FactTier.C
                    )
                    new_facts.append(fact)
                
                elif "resume" in pattern and "parsed" in pattern:
                    # Resume parsing happened multiple times
                    fact = self.create_fact(
                        category=KnowledgeCategory.TREND,
                        subject="user",
                        predicate="iterates_on_resume",
                        obj=True,
                        confidence=min(0.9, 0.5 + (count * 0.1)),
                        evidence=[],
                        tier=FactTier.C
                    )
                    new_facts.append(fact)
        
        return new_facts
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of semantic memory state."""
        return {
            "total_facts": len(self.facts),
            "facts_by_category": {cat.value: len(self.get_facts_by_category(cat)) for cat in KnowledgeCategory},
            "high_confidence_facts": len(self.get_high_confidence_facts()),
            "tier_distribution": {tier.value: len(self.get_facts_by_tier(tier)) for tier in FactTier}
        }