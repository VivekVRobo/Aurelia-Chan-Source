"""
Aurelia Cognitive OS V3 - Phase 3: Cognitive Router
==================================================
Decides which systems are actually needed for each request.

Avoids the inefficiency of running every engine for every message.
Implements hierarchical intelligence levels.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum
from aurelia.cognition.contracts import (
    MeaningFrame,
    CognitiveAssessment,
    DialogueAct
)
from aurelia.execution.capability_registry import (
    Capability,
    CapabilityRegistry,
    capability_registry
)


class IntelligenceLevel(Enum):
    """Hierarchical intelligence levels."""
    REFLEX = 0  # Simple responses, no thinking needed
    DETERMINISTIC = 1  # Calculations, parsing, validation
    ANALYTICAL = 2  # Scoring, ranking, matching, statistics
    PLANNING = 3  # Multi-step goals, constraints, optimization
    LLM_REASONING = 4  # Ambiguity, hypotheses, synthesis
    VERIFICATION = 5  # Evidence, consistency, policy, confidence
    LANGUAGE_RENDERING = 6  # Aurelia response


@dataclass
class ExecutionPlan:
    """
    Plan for which systems to invoke.
    
    The router creates this plan, then the executor runs it.
    """
    intelligence_level: IntelligenceLevel
    required_capabilities: List[str]  # Capability names to invoke
    llm_required: bool
    knowledge_required: bool
    memory_required: bool
    estimated_cost: str  # "NONE", "LOW", "MEDIUM", "HIGH"
    estimated_latency: str  # "INSTANT", "FAST", "MEDIUM", "SLOW"
    confidence: float  # Confidence in this plan


class CognitiveRouter:
    """
    Decides which systems are actually needed for each request.
    
    Key insight: If user says "Thanks", you should NOT run three
    career-analysis engines. Only invoke what's actually needed.
    """
    
    def __init__(self, capability_registry: CapabilityRegistry):
        self.capability_registry = capability_registry
    
    def assess_intelligence_level(self, meaning_frame: MeaningFrame) -> IntelligenceLevel:
        """
        Determine the intelligence level needed for this request.
        
        Routes from cheapest/deterministic to more expensive reasoning.
        """
        # REFLEX: Simple greetings, thanks, basic commands
        if meaning_frame.dialogue_act in [DialogueAct.GREETING, DialogueAct.GRATITUDE]:
            return IntelligenceLevel.REFLEX
        
        # DETERMINISTIC: Lookups, simple queries
        if meaning_frame.dialogue_act == DialogueAct.GENERAL_INQUIRY:
            # Check if it's a simple factual query
            if any(word in meaning_frame.raw_text.lower() for word in ["what is", "what's", "how many"]):
                return IntelligenceLevel.DETERMINISTIC
        
        # ANALYTICAL: Scoring, ranking, matching
        if meaning_frame.dialogue_act in [DialogueAct.RESUME_REVIEW, DialogueAct.INTERVIEW_PRACTICE]:
            return IntelligenceLevel.ANALYTICAL
        
        # PLANNING: Multi-step goals, constraints
        if meaning_frame.dialogue_act in [DialogueAct.GOAL_SETTING, DialogueAct.PLAN_REVIEW]:
            return IntelligenceLevel.PLANNING
        
        # LLM_REASONING: Ambiguity, complex reasoning
        if meaning_frame.confidence < 0.7:  # Low confidence in understanding
            return IntelligenceLevel.LLM_REASONING
        
        if len(meaning_frame.unresolved_references) > 0:
            return IntelligenceLevel.LLM_REASONING
        
        # Default to LLM for career advice (complex domain)
        if meaning_frame.dialogue_act == DialogueAct.CAREER_ADVICE:
            return IntelligenceLevel.LLM_REASONING
        
        return IntelligenceLevel.LLM_REASONING
    
    def determine_required_capabilities(self, meaning_frame: MeaningFrame) -> List[str]:
        """
        Determine which capabilities are needed for this request.
        
        Only invoke what's actually needed - this is a key efficiency.
        """
        required = []
        
        # Resume-related
        if meaning_frame.dialogue_act == DialogueAct.RESUME_REVIEW:
            required.append("resume.parse")
        
        # Interview-related
        if meaning_frame.dialogue_act == DialogueAct.INTERVIEW_PRACTICE:
            required.append("interview.score_response")
        
        # Salary-related
        if meaning_frame.dialogue_act == DialogueAct.SALARY_DISCUSSION:
            required.append("salary.benchmark")
        
        # Career path-related
        if meaning_frame.dialogue_act == DialogueAct.CAREER_ADVICE:
            # Check if asking about career progression
            text_lower = meaning_frame.raw_text.lower()
            if any(word in text_lower for word in ["path", "progress", "move", "transition", "advance"]):
                required.append("career.find_path")
            
            # Check if asking about readiness/gaps
            if any(word in text_lower for word in ["ready", "gap", "skill", "competency", "prepared"]):
                required.append("career.gap_analysis")
        
        return required
    
    def route(self, meaning_frame: MeaningFrame) -> ExecutionPlan:
        """
        Create an execution plan for the given meaning frame.
        
        This is the heart of efficient cognitive routing.
        """
        # Determine intelligence level
        intelligence_level = self.assess_intelligence_level(meaning_frame)
        
        # Determine required capabilities
        required_capabilities = self.determine_required_capabilities(meaning_frame)
        
        # Determine if LLM is needed
        llm_required = intelligence_level in [
            IntelligenceLevel.LLM_REASONING,
            IntelligenceLevel.LANGUAGE_RENDERING
        ]
        
        # Determine if knowledge is needed
        knowledge_required = any(cap in required_capabilities for cap in [
            "career.find_path",
            "salary.benchmark"
        ])
        
        # Determine if memory is needed
        memory_required = len(required_capabilities) > 0
        
        # Estimate cost and latency
        if required_capabilities:
            capabilities = [self.capability_registry.get(cap) for cap in required_capabilities if self.capability_registry.get(cap)]
            if capabilities:
                # Determine highest cost
                cost_order = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}
                max_cost = max(capabilities, key=lambda c: cost_order.get(c.cost, 0))
                estimated_cost = max_cost.cost
                
                # Determine highest latency
                latency_order = {"INSTANT": 0, "FAST": 1, "MEDIUM": 2, "SLOW": 3}
                max_latency = max(capabilities, key=lambda c: latency_order.get(c.latency, 0))
                estimated_latency = max_latency.latency
            else:
                estimated_cost = "LOW"
                estimated_latency = "FAST"
        else:
            estimated_cost = "NONE"
            estimated_latency = "INSTANT"
        
        # Add LLM cost if needed
        if llm_required:
            if estimated_cost == "NONE":
                estimated_cost = "MEDIUM"
            elif estimated_cost == "LOW":
                estimated_cost = "MEDIUM"
            estimated_latency = "MEDIUM"
        
        # Calculate confidence in this plan
        confidence = meaning_frame.confidence
        if len(required_capabilities) == 0 and intelligence_level != IntelligenceLevel.REFLEX:
            confidence *= 0.8  # Lower confidence if no capabilities selected
        
        return ExecutionPlan(
            intelligence_level=intelligence_level,
            required_capabilities=required_capabilities,
            llm_required=llm_required,
            knowledge_required=knowledge_required,
            memory_required=memory_required,
            estimated_cost=estimated_cost,
            estimated_latency=estimated_latency,
            confidence=confidence
        )
    
    def create_cognitive_assessment(self, meaning_frame: MeaningFrame, plan: ExecutionPlan) -> CognitiveAssessment:
        """
        Create metacognitive assessment before responding.
        
        Aurelia asks itself: Do I understand? Do I have enough evidence?
        """
        understanding_confidence = meaning_frame.confidence
        
        # Evidence sufficiency based on plan
        if len(plan.required_capabilities) > 0:
            evidence_sufficiency = 0.8  # We'll have data from capabilities
        elif plan.llm_required:
            evidence_sufficiency = 0.5  # LLM will need to infer
        else:
            evidence_sufficiency = 0.3  # No data available
        
        # Conflict detection (simplified - would be more sophisticated in full system)
        conflict_detected = False
        
        # Clarification needed
        clarification_needed = len(meaning_frame.unresolved_references) > 0
        
        return CognitiveAssessment(
            understanding_confidence=understanding_confidence,
            evidence_sufficiency=evidence_sufficiency,
            conflict_detected=conflict_detected,
            clarification_needed=clarification_needed,
            requires_llm=plan.llm_required
        )