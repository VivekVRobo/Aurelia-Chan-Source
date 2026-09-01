"""
Aurelia Cognitive OS V3 - Phase 2: Skill Ontology
=================================================
Canonical skill concepts and hierarchy.

Avoids string chaos by creating standardized skill concepts
with aliases and relationships.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class SkillCategory(Enum):
    """High-level skill categories."""
    LEADERSHIP = "leadership"
    TECHNICAL = "technical"
    STRATEGIC = "strategic"
    COMMUNICATION = "communication"
    ANALYTICAL = "analytical"
    OPERATIONAL = "operational"
    INTERPERSONAL = "interpersonal"


@dataclass
class SkillConcept:
    """
    Canonical skill concept with aliases and hierarchy.
    
    Prevents "leadership", "team leadership", "people management"
    from being treated as unrelated skills.
    """
    id: str  # e.g., "skill.people_management"
    name: str  # Canonical name
    category: SkillCategory
    aliases: List[str] = field(default_factory=list)
    parent: Optional[str] = None  # Parent skill ID
    children: List[str] = field(default_factory=list)
    description: str = ""
    level_required_for: Dict[str, int] = field(default_factory=dict)  # role -> required level


# Canonical skill ontology
SKILL_ONTOLOGY: Dict[str, SkillConcept] = {
    # Leadership skills
    "skill.leadership": SkillConcept(
        id="skill.leadership",
        name="Leadership",
        category=SkillCategory.LEADERSHIP,
        aliases=["leadership", "management"],
        description="Ability to guide and motivate teams toward goals"
    ),
    
    "skill.people_management": SkillConcept(
        id="skill.people_management",
        name="People Management",
        category=SkillCategory.LEADERSHIP,
        aliases=["team leadership", "people management", "staff leadership", "team management"],
        parent="skill.leadership",
        description="Managing team members, performance, and development"
    ),
    
    "skill.strategic_leadership": SkillConcept(
        id="skill.strategic_leadership",
        name="Strategic Leadership",
        category=SkillCategory.LEADERSHIP,
        aliases=["strategic thinking", "visionary leadership", "strategic direction"],
        parent="skill.leadership",
        description="Setting strategic direction and long-term vision"
    ),
    
    "skill.conflict_management": SkillConcept(
        id="skill.conflict_management",
        name="Conflict Management",
        category=SkillCategory.LEADERSHIP,
        aliases=["conflict resolution", "dispute resolution", "mediation"],
        parent="skill.leadership",
        description="Resolving interpersonal and team conflicts"
    ),
    
    # Strategic skills
    "skill.strategic_planning": SkillConcept(
        id="skill.strategic_planning",
        name="Strategic Planning",
        category=SkillCategory.STRATEGIC,
        aliases=["strategic planning", "business strategy", "strategic development"],
        description="Creating and executing strategic plans"
    ),
    
    "skill.budget_ownership": SkillConcept(
        id="skill.budget_ownership",
        name="Budget Ownership",
        category=SkillCategory.STRATEGIC,
        aliases=["financial management", "budget management", "P&L responsibility"],
        description="Managing budgets and financial resources"
    ),
    
    "skill.cross_functional_influence": SkillConcept(
        id="skill.cross_functional_influence",
        name="Cross-functional Influence",
        category=SkillCategory.STRATEGIC,
        aliases=["stakeholder management", "cross-team collaboration", "organizational influence"],
        description="Influencing decisions across organizational boundaries"
    ),
    
    # Communication skills
    "skill.executive_communication": SkillConcept(
        id="skill.executive_communication",
        name="Executive Communication",
        category=SkillCategory.COMMUNICATION,
        aliases=["executive presence", "senior communication", "board communication"],
        description="Communicating effectively with executives and stakeholders"
    ),
    
    "skill.public_speaking": SkillConcept(
        id="skill.public_speaking",
        name="Public Speaking",
        category=SkillCategory.COMMUNICATION,
        aliases=["presentation skills", "speaking", "presentations"],
        description="Delivering effective presentations and speeches"
    ),
    
    "skill.written_communication": SkillConcept(
        id="skill.written_communication",
        name="Written Communication",
        category=SkillCategory.COMMUNICATION,
        aliases=["writing", "business writing", "documentation"],
        description="Creating clear written communications and documentation"
    ),
    
    # Technical skills (examples - would be expanded)
    "skill.software_engineering": SkillConcept(
        id="skill.software_engineering",
        name="Software Engineering",
        category=SkillCategory.TECHNICAL,
        aliases=["software development", "programming", "coding", "engineering"],
        description="Designing and building software systems"
    ),
    
    "skill.data_analysis": SkillConcept(
        id="skill.data_analysis",
        name="Data Analysis",
        category=SkillCategory.ANALYTICAL,
        aliases=["analytics", "data science", "statistical analysis"],
        description="Analyzing data to derive insights"
    ),
    
    # Operational skills
    "skill.project_management": SkillConcept(
        id="skill.project_management",
        name="Project Management",
        category=SkillCategory.OPERATIONAL,
        aliases=["PM", "project coordination", "delivery management"],
        description="Managing projects from initiation to completion"
    ),
    
    "skill.process_optimization": SkillConcept(
        id="skill.process_optimization",
        name="Process Optimization",
        category=SkillCategory.OPERATIONAL,
        aliases=["process improvement", "operational excellence", "efficiency"],
        description="Improving operational processes and efficiency"
    ),
}


def normalize_skill(skill_name: str) -> Optional[str]:
    """
    Normalize a skill name to its canonical ID.
    
    Example:
    "team leadership" -> "skill.people_management"
    "strategic thinking" -> "skill.strategic_leadership"
    """
    skill_name_lower = skill_name.lower().strip()
    
    for skill_id, concept in SKILL_ONTOLOGY.items():
        # Check exact match
        if concept.name.lower() == skill_name_lower:
            return skill_id
        
        # Check aliases
        for alias in concept.aliases:
            if alias.lower() == skill_name_lower:
                return skill_id
    
    return None


def get_skill_hierarchy(skill_id: str) -> List[str]:
    """
    Get the full hierarchy of a skill (parent chain).
    
    Example:
    "skill.people_management" -> ["skill.leadership", "skill.people_management"]
    """
    hierarchy = [skill_id]
    current = skill_id
    
    while current in SKILL_ONTOLOGY:
        parent = SKILL_ONTOLOGY[current].parent
        if parent:
            hierarchy.insert(0, parent)
            current = parent
        else:
            break
    
    return hierarchy


def get_all_related_skills(skill_id: str) -> List[str]:
    """
    Get all related skills (parent + children + siblings).
    """
    related = set()
    
    # Add hierarchy
    related.update(get_skill_hierarchy(skill_id))
    
    # Add children
    if skill_id in SKILL_ONTOLOGY:
        related.update(SKILL_ONTOLOGY[skill_id].children)
    
    # Add siblings (same parent)
    if skill_id in SKILL_ONTOLOGY:
        parent = SKILL_ONTOLOGY[skill_id].parent
        if parent:
            for other_id, concept in SKILL_ONTOLOGY.items():
                if concept.parent == parent and other_id != skill_id:
                    related.add(other_id)
    
    return list(related)


def get_required_level_for_role(skill_id: str, role: str) -> Optional[int]:
    """
    Get the required skill level for a specific role.
    
    Returns None if not defined.
    """
    if skill_id in SKILL_ONTOLOGY:
        return SKILL_ONTOLOGY[skill_id].level_required_for.get(role)
    return None


def set_role_requirements():
    """
    Set skill requirements for common roles.
    
    This would typically be loaded from a database or configuration.
    """
    # Director requirements
    SKILL_ONTOLOGY["skill.people_management"].level_required_for["Director"] = 4
    SKILL_ONTOLOGY["skill.strategic_leadership"].level_required_for["Director"] = 4
    SKILL_ONTOLOGY["skill.strategic_planning"].level_required_for["Director"] = 4
    SKILL_ONTOLOGY["skill.budget_ownership"].level_required_for["Director"] = 3
    SKILL_ONTOLOGY["skill.cross_functional_influence"].level_required_for["Director"] = 4
    SKILL_ONTOLOGY["skill.executive_communication"].level_required_for["Director"] = 4
    
    # Senior Manager requirements
    SKILL_ONTOLOGY["skill.people_management"].level_required_for["Senior Manager"] = 3
    SKILL_ONTOLOGY["skill.strategic_leadership"].level_required_for["Senior Manager"] = 3
    SKILL_ONTOLOGY["skill.strategic_planning"].level_required_for["Senior Manager"] = 3
    SKILL_ONTOLOGY["skill.executive_communication"].level_required_for["Senior Manager"] = 3
    
    # Manager requirements
    SKILL_ONTOLOGY["skill.people_management"].level_required_for["Manager"] = 2
    SKILL_ONTOLOGY["skill.project_management"].level_required_for["Manager"] = 3
    SKILL_ONTOLOGY["skill.conflict_management"].level_required_for["Manager"] = 2


# Initialize role requirements
set_role_requirements()