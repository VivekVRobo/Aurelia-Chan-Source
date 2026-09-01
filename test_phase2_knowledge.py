#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aurelia Cognitive OS V3 - Phase 2 Knowledge Tests
==================================================
Tests the skill ontology and career graph systems.
"""

import sys
sys.path.insert(0, 'C:\\Users\\vivek\\Desktop\\Aurelia-Chan')

from aurelia.knowledge.ontology import (
    normalize_skill,
    get_skill_hierarchy,
    get_all_related_skills,
    get_required_level_for_role,
    SKILL_ONTOLOGY,
    SkillCategory
)
from aurelia.knowledge.career_graph import (
    CareerGraph,
    create_sample_career_graph,
    analyze_career_path,
    EdgeType
)


def test_skill_normalization():
    """Test skill name normalization."""
    print("Testing Skill Normalization...")
    
    # Test various aliases
    test_cases = [
        ("team leadership", "skill.people_management"),
        ("people management", "skill.people_management"),
        ("strategic thinking", "skill.strategic_leadership"),
        ("conflict resolution", "skill.conflict_management"),
        ("financial management", "skill.budget_ownership"),
    ]
    
    for input_skill, expected_id in test_cases:
        result = normalize_skill(input_skill)
        assert result == expected_id, f"Expected {expected_id}, got {result} for {input_skill}"
    
    print("  Skill Normalization: PASS")
    return True


def test_skill_hierarchy():
    """Test skill hierarchy retrieval."""
    print("Testing Skill Hierarchy...")
    
    hierarchy = get_skill_hierarchy("skill.people_management")
    assert "skill.leadership" in hierarchy
    assert "skill.people_management" in hierarchy
    assert hierarchy[0] == "skill.leadership"
    
    print("  Skill Hierarchy: PASS")
    return True


def test_related_skills():
    """Test related skills retrieval."""
    print("Testing Related Skills...")
    
    related = get_all_related_skills("skill.people_management")
    assert "skill.leadership" in related
    assert "skill.people_management" in related
    # Should include siblings if they exist
    
    print("  Related Skills: PASS")
    return True


def test_role_requirements():
    """Test role skill requirements."""
    print("Testing Role Requirements...")
    
    director_people_mgmt = get_required_level_for_role("skill.people_management", "Director")
    assert director_people_mgmt == 4
    
    manager_people_mgmt = get_required_level_for_role("skill.people_management", "Manager")
    assert manager_people_mgmt == 2
    
    print("  Role Requirements: PASS")
    return True


def test_career_graph_creation():
    """Test career graph creation."""
    print("Testing Career Graph Creation...")
    
    graph = create_sample_career_graph()
    
    # Check nodes exist
    assert "Software Engineer" in graph.nodes
    assert "Director of Engineering" in graph.nodes
    assert "Team Leadership" in graph.nodes
    
    # Check edges exist
    assert len(graph.get_neighbors("Software Engineer")) > 0
    assert len(graph.get_neighbors("Director of Engineering", EdgeType.REQUIRES)) > 0
    
    print("  Career Graph Creation: PASS")
    return True


def test_career_path_analysis():
    """Test career path analysis."""
    print("Testing Career Path Analysis...")
    
    graph = create_sample_career_graph()
    
    # Test path from Senior Engineer to Director
    analysis = analyze_career_path(graph, "Senior Software Engineer", "Director of Engineering")
    
    assert analysis["status"] == "success"
    assert len(analysis["paths"]) > 0
    assert analysis["current_role"] == "Senior Software Engineer"
    assert analysis["target_role"] == "Director of Engineering"
    
    # Check that paths include required skills
    for path in analysis["paths"]:
        assert "path" in path
        assert "steps" in path
        assert "required_skills" in path
    
    print("  Career Path Analysis: PASS")
    return True


def test_shortest_path():
    """Test shortest path finding."""
    print("Testing Shortest Path...")
    
    graph = create_sample_career_graph()
    
    path = graph.get_shortest_path("Software Engineer", "Director of Engineering")
    
    assert path is not None
    assert path[0] == "Software Engineer"
    assert path[-1] == "Director of Engineering"
    assert len(path) > 1
    
    print("  Shortest Path: PASS")
    return True


def test_skill_requirement_edges():
    """Test skill requirement edges."""
    print("Testing Skill Requirement Edges...")
    
    graph = create_sample_career_graph()
    
    director_skills = graph.get_neighbors("Director of Engineering", EdgeType.REQUIRES)
    
    assert "Team Leadership" in director_skills
    assert "Strategic Planning" in director_skills
    assert "Budget Ownership" in director_skills
    assert "Executive Communication" in director_skills
    
    print("  Skill Requirement Edges: PASS")
    return True


def main():
    print("=" * 70)
    print("    AURELIA COGNITIVE OS V3 - PHASE 2 KNOWLEDGE TESTS")
    print("=" * 70)
    print()
    
    tests = [
        test_skill_normalization,
        test_skill_hierarchy,
        test_related_skills,
        test_role_requirements,
        test_career_graph_creation,
        test_career_path_analysis,
        test_shortest_path,
        test_skill_requirement_edges
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print()
    print("=" * 70)
    print("    TEST RESULTS")
    print("=" * 70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print()
        print("SUCCESS: All Phase 2 knowledge systems are working correctly!")
        print()
        print("Knowledge systems ready:")
        print("  - Skill Ontology (canonical skill concepts)")
        print("  - Career Graph (role relationships and progression)")
        print("  - Path Analysis (career path finding)")
        print()
        print("Next: Continue Phase 2 - Resume parser, Gap analysis, Interview scoring, Salary engine")
    else:
        print()
        print("FAILURE: Some tests failed. Please fix the issues.")
    
    print("=" * 70)


if __name__ == "__main__":
    main()