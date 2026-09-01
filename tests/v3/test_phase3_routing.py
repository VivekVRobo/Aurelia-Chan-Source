#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aurelia Cognitive OS V3 - Phase 3 Cognitive Routing Tests
==========================================================
Tests the cognitive router, capability registry, and execution engine.
"""

import sys
sys.path.insert(0, 'C:\\Users\\vivek\\Desktop\\Aurelia-Chan')

from aurelia.execution.capability_registry import (
    CapabilityRegistry,
    Capability,
    CapabilityType,
    register_initial_capabilities,
    capability_registry
)
from aurelia.execution.router import (
    CognitiveRouter,
    ExecutionPlan,
    IntelligenceLevel
)
from aurelia.execution.executor import (
    ExecutionEngine,
    ExecutionStatus
)
from aurelia.cognition.contracts import (
    MeaningFrame,
    DialogueAct,
    Intent,
    EntityRef
)


def test_capability_registry():
    """Test capability registry."""
    print("Testing Capability Registry...")
    
    # Register initial capabilities
    register_initial_capabilities()
    
    # Test listing capabilities
    all_caps = capability_registry.capabilities
    assert len(all_caps) > 0
    
    # Test getting specific capability
    salary_cap = capability_registry.get("salary.benchmark")
    assert salary_cap is not None
    assert salary_cap.name == "salary.benchmark"
    assert salary_cap.capability_type == CapabilityType.SKILL
    
    # Test filtering by category
    career_caps = capability_registry.list_by_category("career")
    assert len(career_caps) > 0
    
    # Test finding deterministic capabilities
    deterministic = capability_registry.find_deterministic()
    assert len(deterministic) > 0
    
    print("  Capability Registry: PASS")
    return True


def test_cognitive_router_reflex():
    """Test routing for reflex-level requests."""
    print("Testing Cognitive Router (Reflex Level)...")
    
    router = CognitiveRouter(capability_registry)
    
    # Test greeting
    greeting_frame = MeaningFrame(
        dialogue_act=DialogueAct.GREETING,
        intents=[Intent(type="greeting", confidence=0.99)],
        subject=EntityRef(type="user", value="current_user"),
        target_role=None,
        raw_text="Hello Aurelia",
        confidence=0.99
    )
    
    plan = router.route(greeting_frame)
    
    assert plan.intelligence_level == IntelligenceLevel.REFLEX
    assert len(plan.required_capabilities) == 0
    assert plan.llm_required == False
    assert plan.estimated_cost == "NONE"
    assert plan.estimated_latency == "INSTANT"
    
    print("  Cognitive Router (Reflex): PASS")
    return True


def test_cognitive_router_analytical():
    """Test routing for analytical-level requests."""
    print("Testing Cognitive Router (Analytical Level)...")
    
    router = CognitiveRouter(capability_registry)
    
    # Test resume review
    resume_frame = MeaningFrame(
        dialogue_act=DialogueAct.RESUME_REVIEW,
        intents=[Intent(type="resume_analysis", confidence=0.95)],
        subject=EntityRef(type="user", value="current_user"),
        target_role=None,
        raw_text="Can you review my resume?",
        confidence=0.95
    )
    
    plan = router.route(resume_frame)
    
    assert plan.intelligence_level == IntelligenceLevel.ANALYTICAL
    assert "resume.parse" in plan.required_capabilities
    assert plan.estimated_cost == "LOW"
    assert plan.estimated_latency == "FAST"
    
    print("  Cognitive Router (Analytical): PASS")
    return True


def test_cognitive_router_llm():
    """Test routing for LLM-level requests."""
    print("Testing Cognitive Router (LLM Level)...")
    
    router = CognitiveRouter(capability_registry)
    
    # Test complex career advice
    career_frame = MeaningFrame(
        dialogue_act=DialogueAct.CAREER_ADVICE,
        intents=[Intent(type="career_guidance", confidence=0.85)],
        subject=EntityRef(type="user", value="current_user"),
        target_role=EntityRef(type="job_role", value="Director"),
        raw_text="What's the best strategy for transitioning to Director?",
        confidence=0.85
    )
    
    plan = router.route(career_frame)
    
    assert plan.intelligence_level == IntelligenceLevel.LLM_REASONING
    assert plan.llm_required == True
    assert plan.estimated_cost in ["MEDIUM", "HIGH"]
    
    print("  Cognitive Router (LLM): PASS")
    return True


def test_execution_engine_reflex():
    """Test execution engine for reflex responses."""
    print("Testing Execution Engine (Reflex)...")
    
    engine = ExecutionEngine(capability_registry)
    
    response = engine.execute_reflex("Hello Aurelia")
    
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0
    
    print("  Execution Engine (Reflex): PASS")
    return True


def test_execution_engine_capability():
    """Test execution engine for specific capabilities."""
    print("Testing Execution Engine (Capability Execution)...")
    
    engine = ExecutionEngine(capability_registry)
    
    # Test salary benchmark
    context = {
        "role": "Director of Engineering",
        "level": "director_level",
        "location": "San Francisco",
        "industry": "Technology"
    }
    
    result = engine.execute_capability("salary.benchmark", context)
    
    assert result.status == ExecutionStatus.COMPLETED
    assert result.result is not None
    assert result.capability_name == "salary.benchmark"
    assert result.execution_time_ms >= 0
    
    print("  Execution Engine (Capability): PASS")
    return True


def test_execution_plan():
    """Test executing a complete plan."""
    print("Testing Execution Plan...")
    
    router = CognitiveRouter(capability_registry)
    engine = ExecutionEngine(capability_registry)
    
    # Create a plan for salary inquiry
    salary_frame = MeaningFrame(
        dialogue_act=DialogueAct.SALARY_DISCUSSION,
        intents=[Intent(type="salary_inquiry", confidence=0.95)],
        subject=EntityRef(type="user", value="current_user"),
        target_role=EntityRef(type="job_role", value="Director of Engineering"),
        raw_text="What's the salary for Director of Engineering in San Francisco?",
        confidence=0.95
    )
    
    plan = router.route(salary_frame)
    
    # Execute the plan
    context = {
        "role": "Director of Engineering",
        "level": "director_level",
        "location": "San Francisco",
        "industry": "Technology"
    }
    
    summary = engine.execute_plan(plan, context)
    
    assert summary.success == True
    assert len(summary.results) > 0
    assert summary.combined_result is not None
    assert summary.total_execution_time_ms >= 0
    
    print("  Execution Plan: PASS")
    return True


def test_cognitive_assessment():
    """Test cognitive assessment (metacognition)."""
    print("Testing Cognitive Assessment...")
    
    router = CognitiveRouter(capability_registry)
    
    # Test with high confidence
    confident_frame = MeaningFrame(
        dialogue_act=DialogueAct.CAREER_ADVICE,
        intents=[Intent(type="career_guidance", confidence=0.95)],
        subject=EntityRef(type="user", value="current_user"),
        target_role=EntityRef(type="job_role", value="Director"),
        raw_text="I want to be a Director",
        confidence=0.95
    )
    
    plan = router.route(confident_frame)
    assessment = router.create_cognitive_assessment(confident_frame, plan)
    
    assert assessment.understanding_confidence >= 0.9
    assert assessment.requires_llm == plan.llm_required
    
    # Test with low confidence
    uncertain_frame = MeaningFrame(
        dialogue_act=DialogueAct.CAREER_ADVICE,
        intents=[Intent(type="career_guidance", confidence=0.5)],
        subject=EntityRef(type="user", value="current_user"),
        target_role=None,
        unresolved_references=["that role"],
        raw_text="What about that role?",
        confidence=0.5
    )
    
    uncertain_plan = router.route(uncertain_frame)
    uncertain_assessment = router.create_cognitive_assessment(uncertain_frame, uncertain_plan)
    
    assert uncertain_assessment.understanding_confidence < 0.7
    assert uncertain_assessment.clarification_needed == True
    
    print("  Cognitive Assessment: PASS")
    return True


def test_hierarchical_intelligence():
    """Test hierarchical intelligence levels."""
    print("Testing Hierarchical Intelligence Levels...")
    
    router = CognitiveRouter(capability_registry)
    
    # Test that different requests get different intelligence levels
    greeting = MeaningFrame(
        dialogue_act=DialogueAct.GREETING,
        intents=[Intent(type="greeting", confidence=0.99)],
        subject=EntityRef(type="user", value="current_user"),
        target_role=None,
        raw_text="Hello",
        confidence=0.99
    )
    
    career_advice = MeaningFrame(
        dialogue_act=DialogueAct.CAREER_ADVICE,
        intents=[Intent(type="career_guidance", confidence=0.85)],
        subject=EntityRef(type="user", value="current_user"),
        target_role=EntityRef(type="job_role", value="Director"),
        raw_text="Career advice needed",
        confidence=0.85
    )
    
    greeting_plan = router.route(greeting)
    career_plan = router.route(career_advice)
    
    assert greeting_plan.intelligence_level == IntelligenceLevel.REFLEX
    assert career_plan.intelligence_level == IntelligenceLevel.LLM_REASONING
    # Reflex should be cheaper than LLM reasoning
    assert greeting_plan.estimated_cost == "NONE"
    assert career_plan.estimated_cost in ["MEDIUM", "HIGH"]
    
    print("  Hierarchical Intelligence: PASS")
    return True


def main():
    print("=" * 70)
    print("    AURELIA COGNITIVE OS V3 - PHASE 3 ROUTING TESTS")
    print("=" * 70)
    print()
    
    tests = [
        test_capability_registry,
        test_cognitive_router_reflex,
        test_cognitive_router_analytical,
        test_cognitive_router_llm,
        test_execution_engine_reflex,
        test_execution_engine_capability,
        test_execution_plan,
        test_cognitive_assessment,
        test_hierarchical_intelligence
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
        print("SUCCESS: All Phase 3 cognitive routing tests passed!")
        print()
        print("Cognitive routing system ready:")
        print("  - Capability Registry (discover and advertise capabilities)")
        print("  - Cognitive Router (decides which systems to invoke)")
        print("  - Execution Engine (orchestrates specialist capabilities)")
        print("  - Hierarchical Intelligence (Reflex -> Deterministic -> Analytical -> LLM)")
        print()
        print("PHASE 3 COMPLETE!")
        print()
        print("Next: Phase 4 - Memory (Working memory, Episodic memory, Semantic memory, Provenance, Reference resolution)")
    else:
        print()
        print("FAILURE: Some tests failed. Please fix the issues.")
    
    print("=" * 70)


if __name__ == "__main__":
    main()