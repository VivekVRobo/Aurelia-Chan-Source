"""
Aurelia Cognitive OS V3 - Phase 3: Capability Registry
========================================================
Registry of all system capabilities (skills + tools + functions).

Every system function advertises its capabilities so the planner
can choose the right tools for each task.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable, Optional
from enum import Enum


class CapabilityType(Enum):
    """Types of capabilities."""
    SKILL = "skill"  # Specialist intelligence
    TOOL = "tool"  # External tool or API
    FUNCTION = "function"  # Simple function
    DATABASE = "database"  # Data query
    CALCULATION = "calculation"  # Mathematical operation


@dataclass
class Capability:
    """
    A system capability.
    
    Every capability in the system must be registered so the
    planner knows what's available and how to use it.
    """
    name: str  # e.g., "salary.lookup"
    display_name: str
    description: str
    
    # Type and classification
    capability_type: CapabilityType
    category: str  # e.g., "compensation", "career", "resume"
    
    # Input/output
    inputs: Dict[str, str]  # parameter name -> type description
    outputs: Dict[str, str]  # output name -> type description
    
    # Execution characteristics
    cost: str  # "NONE", "LOW", "MEDIUM", "HIGH"
    latency: str  # "INSTANT", "FAST", "MEDIUM", "SLOW"
    deterministic: bool
    
    # Dependencies
    requires_network: bool = False
    requires_llm: bool = False
    required_data: List[str] = field(default_factory=list)
    
    # Metadata
    version: str = "1.0"
    available: bool = True
    confidence: float = 1.0  # Confidence in the capability's results


class CapabilityRegistry:
    """
    Registry of all system capabilities.
    
    The planner queries this registry to find the right capabilities
    for each task.
    """
    
    def __init__(self):
        self.capabilities: Dict[str, Capability] = {}
    
    def register(self, capability: Capability):
        """Register a capability."""
        self.capabilities[capability.name] = capability
    
    def get(self, name: str) -> Optional[Capability]:
        """Get a capability by name."""
        return self.capabilities.get(name)
    
    def list_by_category(self, category: str) -> List[Capability]:
        """List all capabilities in a category."""
        return [c for c in self.capabilities.values() if c.category == category]
    
    def list_by_type(self, capability_type: CapabilityType) -> List[Capability]:
        """List all capabilities of a specific type."""
        return [c for c in self.capabilities.values() if c.capability_type == capability_type]
    
    def find_deterministic(self) -> List[Capability]:
        """Find all deterministic capabilities."""
        return [c for c in self.capabilities.values() if c.deterministic]
    
    def find_offline_capabilities(self) -> List[Capability]:
        """Find capabilities that don't require network."""
        return [c for c in self.capabilities.values() if not c.requires_network]
    
    def find_low_cost(self) -> List[Capability]:
        """Find low-cost capabilities."""
        return [c for c in self.capabilities.values() if c.cost in ["NONE", "LOW"]]
    
    def find_fast(self) -> List[Capability]:
        """Find fast capabilities."""
        return [c for c in self.capabilities.values() if c.latency in ["INSTANT", "FAST"]]
    
    def search(self, query: str) -> List[Capability]:
        """Search capabilities by name or description."""
        query_lower = query.lower()
        results = []
        
        for cap in self.capabilities.values():
            if (query_lower in cap.name.lower() or 
                query_lower in cap.description.lower() or
                query_lower in cap.display_name.lower()):
                results.append(cap)
        
        return results


# Global capability registry instance
capability_registry = CapabilityRegistry()


def register_initial_capabilities():
    """Register the capabilities from Phase 2 specialist engines."""
    
    # Career gap analysis capability
    capability_registry.register(Capability(
        name="career.gap_analysis",
        display_name="Career Gap Analysis",
        description="Analyze skill gaps between current capabilities and target role requirements",
        capability_type=CapabilityType.SKILL,
        category="career",
        inputs={
            "target_role": "Role name",
            "current_role": "Current role name",
            "user_skills": "List of user skills with levels"
        },
        outputs={
            "gaps": "List of skill gaps",
            "readiness_score": "Overall readiness score (0-1)",
            "strengths": "List of strengths"
        },
        cost="LOW",
        latency="FAST",
        deterministic=True,
        requires_network=False,
        requires_llm=False
    ))
    
    # Interview scoring capability
    capability_registry.register(Capability(
        name="interview.score_response",
        display_name="Interview Response Scoring",
        description="Score interview responses using STAR method and competency analysis",
        capability_type=CapabilityType.SKILL,
        category="interview",
        inputs={
            "question": "Interview question",
            "answer": "Candidate's answer"
        },
        outputs={
            "overall_score": "Overall score (0-10)",
            "star_completeness": "STAR method completeness (0-1)",
            "competency_scores": "Per-competency scores",
            "feedback": "Improvement suggestions"
        },
        cost="LOW",
        latency="FAST",
        deterministic=True,
        requires_network=False,
        requires_llm=False
    ))
    
    # Salary benchmark capability
    capability_registry.register(Capability(
        name="salary.benchmark",
        display_name="Salary Benchmarking",
        description="Provide salary benchmarks based on role, location, and industry",
        capability_type=CapabilityType.SKILL,
        category="compensation",
        inputs={
            "role": "Job role",
            "level": "Seniority level",
            "location": "Geographic location",
            "industry": "Industry sector"
        },
        outputs={
            "median_salary": "Market median salary",
            "salary_range": "Min and max salary range",
            "percentiles": "25th and 75th percentile salaries",
            "confidence": "Confidence in the benchmark"
        },
        cost="LOW",
        latency="FAST",
        deterministic=True,
        requires_network=False,
        requires_llm=False
    ))
    
    # Resume parsing capability
    capability_registry.register(Capability(
        name="resume.parse",
        display_name="Resume Parsing",
        description="Parse resume text into structured evidence",
        capability_type=CapabilityType.SKILL,
        category="resume",
        inputs={
            "resume_text": "Raw resume text"
        },
        outputs={
            "bullets": "Parsed bullet points",
            "achievements": "Structured achievement evidence",
            "metrics_count": "Number of quantified metrics",
            "leadership_score": "Leadership signal score"
        },
        cost="LOW",
        latency="FAST",
        deterministic=True,
        requires_network=False,
        requires_llm=False
    ))
    
    # Career path finding capability
    capability_registry.register(Capability(
        name="career.find_path",
        display_name="Career Path Finding",
        description="Find career progression paths using graph algorithms",
        capability_type=CapabilityType.SKILL,
        category="career",
        inputs={
            "current_role": "Current role",
            "target_role": "Target role"
        },
        outputs={
            "paths": "List of possible career paths",
            "shortest_path": "Shortest path between roles",
            "required_skills": "Skills needed for each path"
        },
        cost="LOW",
        latency="INSTANT",
        deterministic=True,
        requires_network=False,
        requires_llm=False
    ))