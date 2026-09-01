"""
Aurelia Cognitive OS V3 - Phase 4: Working Memory
=================================================
Short-term cognitive workspace for active cognition.

Working memory is NOT just the last 20 chat messages.
It's structured state derived from conversation and evidence.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from aurelia.cognition.contracts import (
    WorkingMemory as BaseWorkingMemory,
    EntityRef,
    Hypothesis
)


@dataclass
class ActiveTask:
    """A task currently being worked on."""
    id: str
    description: str
    status: str  # "active", "blocked", "completed"
    started_at: datetime
    priority: float  # 0-1 scale


@dataclass
class PendingClarification:
    """A clarification that needs to be addressed."""
    question: str
    context: str
    urgency: str  # "low", "medium", "high"
    created_at: datetime


class WorkingMemory:
    """
    Short-term cognitive workspace.
    
    Unlike simple conversation history, this is structured state
    derived from conversation and evidence.
    """
    
    def __init__(self):
        self.conversation_goal: Optional[str] = None
        self.active_entities: List[EntityRef] = []
        self.current_hypotheses: List[Hypothesis] = []
        self.pending_questions: List[str] = []
        self.active_tasks: List[ActiveTask] = []
        self.pending_clarifications: List[PendingClarification] = []
        self.recently_retrieved_evidence: List[Any] = []
        self.unresolved_refs: List[str] = []
        self.last_updated: datetime = datetime.now()
    
    def set_goal(self, goal: str):
        """Set the current conversation goal."""
        self.conversation_goal = goal
        self.last_updated = datetime.now()
    
    def add_entity(self, entity: EntityRef):
        """Add an active entity to working memory."""
        # Avoid duplicates
        if not any(e.type == entity.type and e.value == entity.value for e in self.active_entities):
            self.active_entities.append(entity)
        self.last_updated = datetime.now()
    
    def add_hypothesis(self, hypothesis: Hypothesis):
        """Add a working hypothesis."""
        self.current_hypotheses.append(hypothesis)
        self.last_updated = datetime.now()
    
    def add_pending_question(self, question: str):
        """Add a question that needs answering."""
        if question not in self.pending_questions:
            self.pending_questions.append(question)
        self.last_updated = datetime.now()
    
    def add_task(self, task: ActiveTask):
        """Add an active task."""
        self.active_tasks.append(task)
        self.last_updated = datetime.now()
    
    def add_clarification(self, clarification: PendingClarification):
        """Add a pending clarification."""
        self.pending_clarifications.append(clarification)
        self.last_updated = datetime.now()
    
    def add_evidence(self, evidence: Any):
        """Add recently retrieved evidence."""
        self.recently_retrieved_evidence.append(evidence)
        self.last_updated = datetime.now()
    
    def add_unresolved_ref(self, ref: str):
        """Add an unresolved reference."""
        if ref not in self.unresolved_refs:
            self.unresolved_refs.append(ref)
        self.last_updated = datetime.now()
    
    def resolve_ref(self, ref: str):
        """Mark a reference as resolved."""
        if ref in self.unresolved_refs:
            self.unresolved_refs.remove(ref)
        self.last_updated = datetime.now()
    
    def clear_completed_tasks(self):
        """Remove completed tasks."""
        self.active_tasks = [t for t in self.active_tasks if t.status != "completed"]
        self.last_updated = datetime.now()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of current working memory state."""
        return {
            "goal": self.conversation_goal,
            "active_entity_count": len(self.active_entities),
            "hypothesis_count": len(self.current_hypotheses),
            "pending_question_count": len(self.pending_questions),
            "active_task_count": len(self.active_tasks),
            "clarification_count": len(self.pending_clarifications),
            "evidence_count": len(self.recently_retrieved_evidence),
            "unresolved_ref_count": len(self.unresolved_refs),
            "last_updated": self.last_updated.isoformat()
        }
    
    def is_idle(self) -> bool:
        """Check if working memory is idle (no active tasks)."""
        return (
            len(self.active_tasks) == 0 and
            len(self.pending_clarifications) == 0 and
            len(self.pending_questions) == 0
        )
    
    def clear(self):
        """Clear working memory (e.g., for new conversation)."""
        self.conversation_goal = None
        self.active_entities = []
        self.current_hypotheses = []
        self.pending_questions = []
        self.active_tasks = []
        self.pending_clarifications = []
        self.recently_retrieved_evidence = []
        self.unresolved_refs = []
        self.last_updated = datetime.now()