"""
Aurelia Cognitive OS V3 - Knowledge Module
==========================================
Knowledge graph, ontology, and evidence systems.
"""

from .ontology import (
    SkillConcept,
    SkillCategory,
    SKILL_ONTOLOGY,
    normalize_skill,
    get_skill_hierarchy,
    get_all_related_skills,
    get_required_level_for_role
)

from .career_graph import (
    Node,
    Edge,
    EdgeType,
    CareerGraph,
    create_sample_career_graph,
    analyze_career_path
)

__all__ = [
    # Ontology
    'SkillConcept',
    'SkillCategory',
    'SKILL_ONTOLOGY',
    'normalize_skill',
    'get_skill_hierarchy',
    'get_all_related_skills',
    'get_required_level_for_role',
    
    # Career Graph
    'Node',
    'Edge',
    'EdgeType',
    'CareerGraph',
    'create_sample_career_graph',
    'analyze_career_path'
]