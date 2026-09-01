"""
Aurelia Cognitive OS V3 - Phase 7: Context Compiler
====================================================
Compiles structured context for LLM consumption.

The context compiler converts structured system state (goals,
memory, evidence, etc.) into natural language context for the LLM.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from aurelia.cognition.contracts import MeaningFrame, WorldState, Evidence
from aurelia.memory.working_memory import WorkingMemory
from aurelia.memory.episodic import EpisodicMemory
from aurelia.memory.semantic import SemanticMemory
from aurelia.planning.goal_engine import GoalEngine


class ContextScope(Enum):
    """Scope of context to include."""
    MINIMAL = "minimal"  # Only current request
    CONVERSATION = "conversation"  # Recent conversation context
    SESSION = "session"  # Current session context
    COMPREHENSIVE = "comprehensive"  # Full system context


@dataclass
class CompiledContext:
    """
    Compiled context for LLM consumption.
    
    Converts structured system state into natural language.
    """
    user_message: str
    system_context: str
    conversation_history: str
    goals_context: str
    memory_context: str
    evidence_context: str
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextCompiler:
    """
    Compiles structured context for LLM consumption.
    
    The context compiler:
    - Converts structured system state to natural language
    - Manages context scope and size
    - Prioritizes relevant information
    - Formats context for optimal LLM understanding
    """
    
    def __init__(self):
        self.max_context_length = 4000  # Characters
        self.context_priorities = {
            "user_message": 1.0,
            "current_goal": 0.9,
            "recent_evidence": 0.8,
            "conversation_history": 0.7,
            "long_term_memory": 0.6,
            "system_state": 0.5
        }
    
    def compile_context(
        self,
        meaning_frame: MeaningFrame,
        working_memory: Optional[WorkingMemory] = None,
        episodic_memory: Optional[EpisodicMemory] = None,
        semantic_memory: Optional[SemanticMemory] = None,
        goal_engine: Optional[GoalEngine] = None,
        scope: ContextScope = ContextScope.SESSION
    ) -> CompiledContext:
        """
        Compile comprehensive context for LLM.
        
        Converts structured system state into natural language context.
        """
        # User message
        user_message = meaning_frame.raw_text
        
        # System context
        system_context = self._compile_system_context(meaning_frame)
        
        # Conversation history
        conversation_history = self._compile_conversation_history(episodic_memory, scope)
        
        # Goals context
        goals_context = self._compile_goals_context(goal_engine, scope)
        
        # Memory context
        memory_context = self._compile_memory_context(working_memory, semantic_memory, scope)
        
        # Evidence context
        evidence_list = getattr(meaning_frame, 'evidence', [])
        evidence_context = self._compile_evidence_context(evidence_list)
        
        # Constraints
        constraints = self._generate_constraints()
        
        return CompiledContext(
            user_message=user_message,
            system_context=system_context,
            conversation_history=conversation_history,
            goals_context=goals_context,
            memory_context=memory_context,
            evidence_context=evidence_context,
            constraints=constraints,
            metadata={"scope": scope.value}
        )
    
    def _compile_system_context(self, meaning_frame: MeaningFrame) -> str:
        """Compile system context from meaning frame."""
        context_parts = []
        
        if meaning_frame.subject:
            context_parts.append(f"Current subject: {meaning_frame.subject.value}")
        
        if meaning_frame.target_role:
            context_parts.append(f"Target role: {meaning_frame.target_role.value}")
        
        if meaning_frame.dialogue_act:
            context_parts.append(f"Dialogue act: {meaning_frame.dialogue_act.value}")
        
        if meaning_frame.confidence:
            context_parts.append(f"Understanding confidence: {meaning_frame.confidence:.2f}")
        
        return " | ".join(context_parts) if context_parts else "No system context available"
    
    def _compile_conversation_history(
        self,
        episodic_memory: Optional[EpisodicMemory],
        scope: ContextScope
    ) -> str:
        """Compile conversation history from episodic memory."""
        if not episodic_memory:
            return "No conversation history available"
        
        if scope == ContextScope.MINIMAL:
            return "Conversation history: Not included in minimal scope"
        
        recent_events = episodic_memory.get_recent_events(limit=5)
        
        if not recent_events:
            return "No recent conversation events"
        
        history_parts = []
        for event in recent_events:
            if event.event_type.value == "conversation":
                history_parts.append(f"- {event.description}")
        
        return "Recent conversation:\n" + "\n".join(history_parts)
    
    def _compile_goals_context(
        self,
        goal_engine: Optional[GoalEngine],
        scope: ContextScope
    ) -> str:
        """Compile goals context from goal engine."""
        if not goal_engine:
            return "No goals set"
        
        if scope == ContextScope.MINIMAL:
            return "Goals: Not included in minimal scope"
        
        active_goals = goal_engine.get_active_goals()
        
        if not active_goals:
            return "No active goals"
        
        goals_parts = []
        for goal in active_goals[:3]:  # Limit to top 3
            goals_parts.append(f"- {goal.title} (Progress: {goal.completion_percentage:.0%})")
        
        return "Active goals:\n" + "\n".join(goals_parts)
    
    def _compile_memory_context(
        self,
        working_memory: Optional[WorkingMemory],
        semantic_memory: Optional[SemanticMemory],
        scope: ContextScope
    ) -> str:
        """Compile memory context from working and semantic memory."""
        memory_parts = []
        
        # Working memory
        if working_memory and scope != ContextScope.MINIMAL:
            if working_memory.conversation_goal:
                memory_parts.append(f"Current conversation goal: {working_memory.conversation_goal}")
            
            if working_memory.active_entities:
                entities = ", ".join([e.value for e in working_memory.active_entities[:3]])
                memory_parts.append(f"Active entities: {entities}")
        
        # Semantic memory
        if semantic_memory and scope == ContextScope.COMPREHENSIVE:
            high_conf_facts = semantic_memory.get_high_confidence_facts(min_confidence=0.8)
            if high_conf_facts:
                facts = [f"{f.subject} {f.predicate} {f.object}" for f in high_conf_facts[:3]]
                memory_parts.append(f"Known facts: {', '.join(facts)}")
        
        return "Memory context:\n" + "\n".join(memory_parts) if memory_parts else "No relevant memory context"
    
    def _compile_evidence_context(self, evidence: List[Evidence]) -> str:
        """Compile evidence context."""
        if not evidence:
            return "No evidence available"
        
        evidence_parts = []
        for ev in evidence[:5]:  # Limit to top 5
            evidence_parts.append(f"- {ev.source}: {ev.reference}")
        
        return "Evidence:\n" + "\n".join(evidence_parts)
    
    def _generate_constraints(self) -> List[str]:
        """Generate system constraints for the LLM."""
        return [
            "Only respond based on provided evidence and context",
            "Do not hallucinate or make up information",
            "If uncertain, acknowledge uncertainty",
            "Maintain professional executive mentor persona",
            "Focus on actionable, specific advice",
            "Distinguish between facts and opinions"
        ]
    
    def format_for_llm(self, compiled_context: CompiledContext) -> str:
        """Format compiled context as a single string for LLM."""
        parts = []
        
        parts.append("SYSTEM CONTEXT:")
        parts.append(compiled_context.system_context)
        parts.append("")
        
        if compiled_context.goals_context:
            parts.append("GOALS:")
            parts.append(compiled_context.goals_context)
            parts.append("")
        
        if compiled_context.memory_context:
            parts.append("MEMORY:")
            parts.append(compiled_context.memory_context)
            parts.append("")
        
        if compiled_context.evidence_context:
            parts.append("EVIDENCE:")
            parts.append(compiled_context.evidence_context)
            parts.append("")
        
        if compiled_context.conversation_history:
            parts.append("RECENT CONVERSATION:")
            parts.append(compiled_context.conversation_history)
            parts.append("")
        
        parts.append("CONSTRAINTS:")
        for constraint in compiled_context.constraints:
            parts.append(f"- {constraint}")
        parts.append("")
        
        parts.append("USER MESSAGE:")
        parts.append(compiled_context.user_message)
        
        return "\n".join(parts)
    
    def optimize_context_length(self, context: str) -> str:
        """Optimize context to fit within max length."""
        if len(context) <= self.max_context_length:
            return context
        
        # Simple truncation - in full system would use smarter summarization
        overage = len(context) - self.max_context_length
        context = context[:-overage - 100] + "\n...[context truncated due to length]..."
        
        return context