#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aurelia Cognitive OS V3 - Phase 1 Contract Tests
================================================
Tests the foundational cognitive contracts to ensure they work correctly.
"""

import sys
sys.path.insert(0, 'C:\\Users\\vivek\\Desktop\\Aurelia-Chan')

from aurelia.cognition.contracts import (
    MeaningFrame,
    Intent,
    EntityRef,
    RelativeDuration,
    Evidence,
    DialogueAct,
    ConfidenceLevel,
    FactTier,
    MemoryFact,
    WorldState,
    WorkingMemory,
    RoleState,
    Goal,
    ResponsePlan,
    ResponseClaim,
    CognitiveAssessment,
    COGNITIVE_INVARIANTS
)
from datetime import datetime


def test_meaning_frame():
    """Test MeaningFrame construction."""
    print("Testing MeaningFrame...")
    
    frame = MeaningFrame(
        dialogue_act=DialogueAct.CAREER_ADVICE,
        intents=[
            Intent(type="evaluate_promotion_readiness", confidence=0.96)
        ],
        subject=EntityRef(type="user", value="current_user"),
        target_role=EntityRef(type="job_role", value="Director"),
        alternatives=["pursue_director_now", "wait_approximately_one_year"],
        temporal_refs={
            "another_year": RelativeDuration(years=1)
        },
        emotional_signals={
            "uncertainty": 0.61,
            "ambition": 0.78
        },
        confidence=0.94,
        raw_text="Do you think I'm ready for director yet or should I stay another year?"
    )
    
    assert frame.dialogue_act == DialogueAct.CAREER_ADVICE
    assert len(frame.intents) == 1
    assert frame.intents[0].confidence == 0.96
    assert frame.target_role.value == "Director"
    assert "another_year" in frame.temporal_refs
    assert frame.temporal_refs["another_year"].years == 1
    assert frame.confidence == 0.94
    
    print("  MeaningFrame: PASS")
    return True


def test_memory_fact():
    """Test MemoryFact with provenance."""
    print("Testing MemoryFact...")
    
    fact = MemoryFact(
        subject="user",
        predicate="has_skill",
        object="Python",
        confidence=0.91,
        evidence=[
            Evidence(
                source="resume_upload",
                reference="resume_2026_08",
                confidence=0.95
            )
        ],
        tier=FactTier.A
    )
    
    assert fact.subject == "user"
    assert fact.predicate == "has_skill"
    assert fact.object == "Python"
    assert fact.confidence == 0.91
    assert len(fact.evidence) == 1
    assert fact.evidence[0].source == "resume_upload"
    assert fact.tier == FactTier.A
    
    print("  MemoryFact: PASS")
    return True


def test_world_state():
    """Test WorldState construction."""
    print("Testing WorldState...")
    
    world = WorldState(
        user=RoleState(
            current_role="Senior Manager",
            confidence=0.98,
            level="Senior",
            company="TechCorp"
        ),
        career={
            "target_role": "Director",
            "industry": "Technology"
        },
        data_freshness={
            "salary_data": "FRESH",
            "market_trends": "AGING"
        }
    )
    
    assert world.user.current_role == "Senior Manager"
    assert world.user.confidence == 0.98
    assert world.career["target_role"] == "Director"
    assert world.data_freshness["salary_data"] == "FRESH"
    
    print("  WorldState: PASS")
    return True


def test_working_memory():
    """Test WorkingMemory construction."""
    print("Testing WorkingMemory...")
    
    memory = WorkingMemory(
        conversation_goal="prepare_for_director_transition",
        active_entities=[
            EntityRef(type="user", value="current_user"),
            EntityRef(type="job_role", value="Director")
        ],
        pending_questions=["What's the timeline?"],
        active_plan="director_transition_plan_v1"
    )
    
    assert memory.conversation_goal == "prepare_for_director_transition"
    assert len(memory.active_entities) == 2
    assert len(memory.pending_questions) == 1
    assert memory.active_plan == "director_transition_plan_v1"
    
    print("  WorkingMemory: PASS")
    return True


def test_goal():
    """Test Goal construction."""
    print("Testing Goal...")
    
    goal = Goal(
        id="goal_27",
        type="career_transition",
        target="Engineering Director",
        desired_by="2027-08",
        state="ACTIVE",
        milestones=["complete_finance_course", "lead_budget_project"],
        blockers=["current_role_unclear"],
        progress=0.36
    )
    
    assert goal.id == "goal_27"
    assert goal.type == "career_transition"
    assert goal.target == "Engineering Director"
    assert goal.state == "ACTIVE"
    assert goal.progress == 0.36
    assert len(goal.milestones) == 2
    
    print("  Goal: PASS")
    return True


def test_response_plan():
    """Test ResponsePlan before LLM rendering."""
    print("Testing ResponsePlan...")
    
    plan = ResponsePlan(
        intent="recommendation",
        claims=[
            ResponseClaim(
                text="You currently meet 7 of 10 Director competencies.",
                evidence=[],
                verified=True,
                confidence=0.85
            )
        ],
        recommendations=["Wait 3-6 months", "Complete budget ownership"],
        uncertainty=["Executive communication score near threshold"],
        questions=["Can you discuss recent leadership experiences?"],
        tone="supportive_direct"
    )
    
    assert plan.intent == "recommendation"
    assert len(plan.claims) == 1
    assert plan.claims[0].verified == True
    assert len(plan.recommendations) == 2
    assert plan.tone == "supportive_direct"
    
    print("  ResponsePlan: PASS")
    return True


def test_cognitive_assessment():
    """Test CognitiveAssessment (metacognition)."""
    print("Testing CognitiveAssessment...")
    
    assessment = CognitiveAssessment(
        understanding_confidence=0.94,
        evidence_sufficiency=0.71,
        conflict_detected=False,
        clarification_needed=False,
        requires_llm=True
    )
    
    assert assessment.understanding_confidence == 0.94
    assert assessment.evidence_sufficiency == 0.71
    assert assessment.conflict_detected == False
    assert assessment.requires_llm == True
    
    print("  CognitiveAssessment: PASS")
    return True


def test_cognitive_invariants():
    """Test that cognitive invariants are defined."""
    print("Testing Cognitive Invariants...")
    
    assert len(COGNITIVE_INVARIANTS) == 20
    assert "LLM output is never automatically treated as fact" in COGNITIVE_INVARIANTS
    assert "Every consequential factual claim must have evidence" in COGNITIVE_INVARIANTS
    assert "Aurelia never pretends to perceive or know things for which no actual data source exists" in COGNITIVE_INVARIANTS
    
    print(f"  Cognitive Invariants: PASS ({len(COGNITIVE_INVARIANTS)} invariants defined)")
    return True


def main():
    print("=" * 70)
    print("    AURELIA COGNITIVE OS V3 - PHASE 1 CONTRACT TESTS")
    print("=" * 70)
    print()
    
    tests = [
        test_meaning_frame,
        test_memory_fact,
        test_world_state,
        test_working_memory,
        test_goal,
        test_response_plan,
        test_cognitive_assessment,
        test_cognitive_invariants
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
            failed += 1
    
    print()
    print("=" * 70)
    print("    TEST RESULTS")
    print("=" * 70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print()
        print("SUCCESS: All Phase 1 cognitive contracts are working correctly!")
        print()
        print("Next: Proceed to Phase 2 - Domain Intelligence")
    else:
        print()
        print("FAILURE: Some tests failed. Please fix the issues.")
    
    print("=" * 70)


if __name__ == "__main__":
    main()