"""
Aurelia Cognitive OS V3 - Phase 1: Cognitive Contracts
=====================================================
Foundational data structures that serve as universal contracts
between all components of the cognitive system.

These contracts define the language of cognition for Aurelia.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum


class ConfidenceLevel(Enum):
    """Confidence levels for cognitive assertions."""
    VERY_LOW = 0.0
    LOW = 0.25
    MEDIUM = 0.5
    HIGH = 0.75
    VERY_HIGH = 1.0


class FactTier(Enum):
    """Evidence tiers for fact classification."""
    A = "A"  # Directly observed
    B = "B"  # Structured authoritative data
    C = "C"  # Strong inference
    D = "D"  # Weak inference
    E = "E"  # LLM hypothesis


class DialogueAct(Enum):
    """Types of dialogue acts."""
    CAREER_ADVICE = "career_advice"
    RESUME_REVIEW = "resume_review"
    INTERVIEW_PRACTICE = "interview_practice"
    SALARY_DISCUSSION = "salary_discussion"
    GOAL_SETTING = "goal_setting"
    PLAN_REVIEW = "plan_review"
    GENERAL_INQUIRY = "general_inquiry"
    CORRECTION = "correction"
    GRATITUDE = "gratitude"
    GREETING = "greeting"


@dataclass
class Intent:
    """Represents a detected user intent."""
    type: str
    confidence: float
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EntityRef:
    """Reference to an entity (role, skill, company, etc.)."""
    type: str
    value: str
    confidence: float = 1.0


@dataclass
class RelativeDuration:
    """Relative time duration."""
    years: float = 0.0
    months: float = 0.0
    weeks: float = 0.0
    days: float = 0.0


@dataclass
class Evidence:
    """Source of evidence for a claim."""
    source: str  # e.g., "resume_upload", "conversation", "interview"
    reference: str  # ID or reference to the source
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0


@dataclass
class MeaningFrame:
    """
    Canonical representation of user input meaning.
    
    This is the universal contract between language understanding
    and actual cognition. All downstream systems work with this
    structured representation, not raw text.
    """
    dialogue_act: DialogueAct
    intents: List[Intent]
    subject: Optional[EntityRef]
    target_role: Optional[EntityRef]
    alternatives: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    temporal_refs: Dict[str, RelativeDuration] = field(default_factory=dict)
    emotional_signals: Dict[str, float] = field(default_factory=dict)
    unresolved_references: List[str] = field(default_factory=list)
    confidence: float = 1.0
    raw_text: str = ""


@dataclass
class MemoryFact:
    """
    A fact stored in memory with provenance and confidence.
    
    Unlike simple storage, every fact tracks WHY we believe it
    and HOW confident we are in that belief.
    """
    subject: str
    predicate: str
    object: str
    confidence: float
    evidence: List[Evidence]
    observed_at: datetime = field(default_factory=datetime.now)
    valid_until: Optional[datetime] = None
    tier: FactTier = FactTier.C


@dataclass
class TemporalFact:
    """
    A fact that is valid only within a specific time range.
    
    Enables temporal intelligence - understanding changes over time.
    """
    fact: str
    value: Any
    valid_from: datetime
    valid_to: Optional[datetime] = None
    confidence: float = 1.0


@dataclass
class RoleState:
    """
    Represents a user's role with uncertainty.
    
    Aurelia should know when it doesn't know - this is a key
    difference between a trustworthy system and a chatbot.
    """
    current_role: str
    confidence: float
    level: Optional[str] = None  # e.g., "Senior", "Director"
    company: Optional[str] = None
    industry: Optional[str] = None


@dataclass
class CompetencyState:
    """
    Dynamic competency model with evidence strength and trend.
    
    Instead of static scores, competencies are calculated from
    evidence and can show improvement over time.
    """
    competency: str
    estimated_level: float  # 0-10 scale
    evidence_strength: float
    trend: float  # Positive = improving, negative = declining
    last_evaluated: datetime = field(default_factory=datetime.now)


@dataclass
class SkillGap:
    """
    Represents a gap between current and required skill level.
    """
    skill: str
    required_level: float
    observed_level: float
    evidence: List[Evidence]
    confidence: float


@dataclass
class CareerGapResult:
    """
    Result of career gap analysis.
    
    Structured output from specialist engines that the LLM
    receives as input, not generates itself.
    """
    target_role: str
    strengths: List[str]
    gaps: List[SkillGap]
    readiness_score: float
    confidence: float


@dataclass
class Goal:
    """
    Represents an active career goal.
    
    Goals drive Aurelia's behavior and understanding of context.
    """
    id: str
    type: str  # e.g., "career_transition", "skill_development"
    target: str
    desired_by: Optional[str]  # ISO date format
    state: str  # "ACTIVE", "COMPLETED", "BLOCKED", "CANCELLED"
    milestones: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    progress: float = 0.0


@dataclass
class PlanStep:
    """
    A step in a development plan with dependencies.
    
    Enables dependency-aware planning rather than simple task lists.
    """
    id: str
    description: str
    depends_on: List[str] = field(default_factory=list)
    required_evidence: List[str] = field(default_factory=list)
    success_condition: Optional[str] = None
    estimated_duration: Optional[RelativeDuration] = None


@dataclass
class Constraints:
    """
    User constraints for planning.
    
    Enables constraint-based reasoning about feasibility.
    """
    deadline: Optional[RelativeDuration] = None
    weekly_time_budget: Optional[float] = None  # hours
    financial_constraints: Optional[Dict[str, float]] = None
    location_constraints: Optional[List[str]] = None


@dataclass
class Prediction:
    """
    A prediction with uncertainty quantification.
    
    Never fake precision - always include confidence intervals.
    """
    value: float
    interval: tuple[float, float]  # (lower, upper) bound
    confidence: float
    features: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)


@dataclass
class Hypothesis:
    """
    A working hypothesis about user intent or situation.
    
    Retain multiple possibilities until evidence resolves them.
    """
    proposition: str
    probability: float
    evidence: List[Evidence] = field(default_factory=list)


@dataclass
class KnowledgeConflict:
    """
    Detected conflict between evidence sources.
    
    Conflicts are not silently resolved - they are surfaced
    for clarification or qualified responses.
    """
    field: str
    values: List[tuple[Any, Evidence]]  # (value, evidence_source)
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResponseClaim:
    """
    A claim in Aurelia's response with verification status.
    
    Every consequential claim should be traceable to evidence.
    """
    text: str
    evidence: List[Evidence]
    verified: bool
    confidence: float


@dataclass
class ResponsePlan:
    """
    Plan for response before LLM rendering.
    
    Structure before prose - greatly reduces hallucinations.
    """
    intent: str
    claims: List[ResponseClaim]
    recommendations: List[str]
    uncertainty: List[str]
    questions: List[str]
    tone: str


@dataclass
class CognitiveAssessment:
    """
    Metacognitive assessment before responding.
    
    Aurelia asks itself: Do I understand? Do I have enough evidence?
    """
    understanding_confidence: float
    evidence_sufficiency: float
    conflict_detected: bool
    clarification_needed: bool
    requires_llm: bool


@dataclass
class WorldState:
    """
    Canonical representation of Aurelia's environment.
    
    Aurelia reasons over the world state, not raw messages.
    """
    now: datetime = field(default_factory=datetime.now)
    user: Optional[RoleState] = None
    career: Optional[Dict[str, Any]] = None
    market: Optional[Dict[str, Any]] = None
    documents: Optional[Dict[str, Any]] = None
    conversation: Optional[Dict[str, Any]] = None
    tasks: Optional[Dict[str, Any]] = None
    available_tools: List[str] = field(default_factory=list)
    data_freshness: Dict[str, str] = field(default_factory=dict)


@dataclass
class WorkingMemory:
    """
    Short-term cognitive workspace.
    
    Not just the last 20 messages - structured state derived
    from conversation and evidence.
    """
    conversation_goal: Optional[str] = None
    active_entities: List[EntityRef] = field(default_factory=list)
    current_hypotheses: List[Hypothesis] = field(default_factory=list)
    pending_questions: List[str] = field(default_factory=list)
    active_plan: Optional[str] = None
    recently_retrieved_evidence: List[Any] = field(default_factory=list)
    unresolved_refs: List[str] = field(default_factory=list)


@dataclass
class AchievementEvidence:
    """
    Structured evidence from resume achievements.
    
    A bullet point becomes structured data that career analysis
    can use directly.
    """
    action: str
    domain: str
    impact_type: str  # e.g., "cost reduction", "revenue growth"
    impact_value: float
    leadership_signal: float
    technical_signal: float
    strategic_signal: float


@dataclass
class InterviewEvidence:
    """
    Structured evidence from interview responses.
    
    Interview analysis produces competency scores, not just
    "good" or "bad" assessments.
    """
    competencies: Dict[str, float]
    missing_evidence: List[str]
    star_completeness: float
    specificity: float
    quantified_impact: float


@dataclass
class AureliaState:
    """
    Internal state of Aurelia's character.
    
    Separates user emotions from Aurelia's presentation state.
    """
    attention: str = "focused"
    interaction_mode: str = "coach"
    confidence: float = 0.9
    expression: str = "thoughtful"
    activity: Optional[str] = None


@dataclass
class AffectState:
    """
    Detected emotional state of the user.
    
    Multi-factor emotion detection, not just keyword matching.
    """
    frustration: float = 0.0
    confidence: float = 0.0
    uncertainty: float = 0.0
    excitement: float = 0.0
    anxiety: float = 0.0
    confidence_score: float = 0.0  # Confidence in this assessment


@dataclass
class DecisionExplanation:
    """
    Explanation for a recommendation.
    
    Enables "Why?" questions without rerunning analysis.
    """
    recommendation: str
    factors: List[tuple[str, float]]  # (factor_name, weight)
    evidence: List[Evidence]


@dataclass
class KnowledgeRecord:
    """
    External knowledge with freshness tracking.
    
    Prevents stale data from being presented as current.
    """
    value: Any
    last_updated: datetime
    freshness_policy: str  # e.g., "monthly", "quarterly"
    source: str


# Freshness states
FRESHNESS_STATES = {
    "FRESH": "Within policy timeframe",
    "AGING": "Approaching end of policy timeframe",
    "STALE": "Beyond policy timeframe",
    "UNKNOWN": "No freshness information"
}


# Cognitive invariants - rules that must never be violated
COGNITIVE_INVARIANTS = [
    "LLM output is never automatically treated as fact",
    "Every consequential factual claim must have evidence",
    "Numerical claims come from structured systems when possible",
    "Memory distinguishes observation from inference",
    "Ambiguity is preserved until resolved",
    "Specialist modules own domain calculations",
    "The LLM cannot directly mutate canonical state",
    "Tool calls are validated before execution",
    "Unsupported claims are removed before response delivery",
    "Conflicting evidence cannot be silently reconciled",
    "Old knowledge has explicit freshness",
    "Plans must contain measurable success conditions",
    "Goal progress must derive from evidence",
    "Persona cannot override factual correctness",
    "System remains partly functional when the LLM is offline",
    "Every major recommendation is explainable",
    "Decisions and scores are versioned",
    "User corrections outrank model inference",
    "Confidence must propagate through dependent reasoning",
    "Aurelia never pretends to perceive or know things for which no actual data source exists"
]