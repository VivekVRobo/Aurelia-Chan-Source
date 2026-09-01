"""
Aurelia Cognitive OS V3 - Cognition Module
=========================================
Core cognitive runtime and state management.
"""

from .contracts import (
    # Enums
    ConfidenceLevel,
    FactTier,
    DialogueAct,
    
    # Core data structures
    Intent,
    EntityRef,
    RelativeDuration,
    Evidence,
    MeaningFrame,
    MemoryFact,
    TemporalFact,
    
    # State models
    RoleState,
    CompetencyState,
    SkillGap,
    CareerGapResult,
    Goal,
    PlanStep,
    Constraints,
    Prediction,
    Hypothesis,
    KnowledgeConflict,
    
    # Response structures
    ResponseClaim,
    ResponsePlan,
    CognitiveAssessment,
    
    # World and memory
    WorldState,
    WorkingMemory,
    
    # Domain-specific evidence
    AchievementEvidence,
    InterviewEvidence,
    
    # Character state
    AureliaState,
    AffectState,
    
    # Meta-cognition
    DecisionExplanation,
    KnowledgeRecord,
    
    # Constants
    FRESHNESS_STATES,
    COGNITIVE_INVARIANTS
)

__all__ = [
    # Enums
    'ConfidenceLevel',
    'FactTier',
    'DialogueAct',
    
    # Core data structures
    'Intent',
    'EntityRef',
    'RelativeDuration',
    'Evidence',
    'MeaningFrame',
    'MemoryFact',
    'TemporalFact',
    
    # State models
    'RoleState',
    'CompetencyState',
    'SkillGap',
    'CareerGapResult',
    'Goal',
    'PlanStep',
    'Constraints',
    'Prediction',
    'Hypothesis',
    'KnowledgeConflict',
    
    # Response structures
    'ResponseClaim',
    'ResponsePlan',
    'CognitiveAssessment',
    
    # World and memory
    'WorldState',
    'WorkingMemory',
    
    # Domain-specific evidence
    'AchievementEvidence',
    'InterviewEvidence',
    
    # Character state
    'AureliaState',
    'AffectState',
    
    # Meta-cognition
    'DecisionExplanation',
    'KnowledgeRecord',
    
    # Constants
    'FRESHNESS_STATES',
    'COGNITIVE_INVARIANTS'
]