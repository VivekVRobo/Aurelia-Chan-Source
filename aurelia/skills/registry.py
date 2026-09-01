"""
Aurelia Cognitive OS V3 - Phase 3: Skill Registry
================================================
Registry of all specialist skills and their contracts.

Every specialist skill publishes its contract so the cognitive
router can discover and invoke it appropriately.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable, Optional, Type
from enum import Enum
from abc import ABC, abstractmethod


class CostLevel(Enum):
    """Cost levels for skill execution."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class LatencyLevel(Enum):
    """Latency levels for skill execution."""
    INSTANT = "instant"  # < 10ms
    FAST = "fast"  # < 100ms
    MEDIUM = "medium"  # < 1s
    SLOW = "slow"  # > 1s


@dataclass
class SkillContract:
    """
    Contract for a specialist skill.
    
    Every specialist skill must publish its contract so the system
    knows how to use it.
    """
    name: str  # e.g., "career.gap_analysis"
    display_name: str  # Human-readable name
    description: str
    
    # Input/output schemas (simplified as type hints for now)
    input_type: str
    output_type: str
    
    # Execution characteristics
    deterministic: bool
    cost: CostLevel
    latency: LatencyLevel
    
    # Dependencies
    required_data: List[str] = field(default_factory=list)
    required_skills: List[str] = field(default_factory=list)
    
    # Metadata
    category: str = "general"
    version: str = "1.0"
    available: bool = True


class SpecialistSkill(ABC):
    """
    Base class for all specialist skills.
    
    Provides a common interface for the cognitive router.
    """
    
    @classmethod
    @abstractmethod
    def get_contract(cls) -> SkillContract:
        """Return the skill's contract."""
        pass
    
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """Execute the skill with the given input."""
        pass


class SkillRegistry:
    """
    Registry of all specialist skills.
    
    The cognitive router queries this registry to discover available
    skills and their contracts.
    """
    
    def __init__(self):
        self.skills: Dict[str, Type[SpecialistSkill]] = {}
        self.contracts: Dict[str, SkillContract] = {}
    
    def register(self, skill_class: Type[SpecialistSkill]):
        """Register a specialist skill."""
        contract = skill_class.get_contract()
        self.skills[contract.name] = skill_class
        self.contracts[contract.name] = contract
    
    def get_skill(self, name: str) -> Optional[Type[SpecialistSkill]]:
        """Get a skill by name."""
        return self.skills.get(name)
    
    def get_contract(self, name: str) -> Optional[SkillContract]:
        """Get a skill's contract by name."""
        return self.contracts.get(name)
    
    def list_skills(self, category: Optional[str] = None) -> List[SkillContract]:
        """List all skills, optionally filtered by category."""
        if category is None:
            return list(self.contracts.values())
        return [c for c in self.contracts.values() if c.category == category]
    
    def find_skills_by_capability(self, capability: str) -> List[SkillContract]:
        """Find skills that provide a specific capability."""
        return [c for c in self.contracts.values() if capability in c.description.lower()]
    
    def get_deterministic_skills(self) -> List[SkillContract]:
        """Get all deterministic skills (no randomness)."""
        return [c for c in self.contracts.values() if c.deterministic]
    
    def get_low_cost_skills(self) -> List[SkillContract]:
        """Get all low-cost skills."""
        return [c for c in self.contracts.values() if c.cost in [CostLevel.NONE, CostLevel.LOW]]
    
    def get_fast_skills(self) -> List[SkillContract]:
        """Get all fast skills (instant or fast latency)."""
        return [c for c in self.contracts.values() if c.latency in [LatencyLevel.INSTANT, LatencyLevel.FAST]]


# Global registry instance
skill_registry = SkillRegistry()


def register_skill(skill_class: Type[SpecialistSkill]):
    """Decorator to register a skill class."""
    skill_registry.register(skill_class)
    return skill_class