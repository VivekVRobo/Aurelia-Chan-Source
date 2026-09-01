#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aurelia Cognitive OS V3 - Phase 4 Memory Systems Tests
======================================================
Tests the four memory systems: Working, Episodic, Semantic, Procedural, Strategic.
"""

import sys
sys.path.insert(0, 'C:\\Users\\vivek\\Desktop\\Aurelia-Chan')

from aurelia.memory.working_memory import WorkingMemory, ActiveTask, PendingClarification
from aurelia.memory.episodic import EpisodicMemory, EpisodicEvent, EventType
from aurelia.memory.semantic import SemanticMemory, SemanticFact, KnowledgeCategory
from aurelia.memory.procedural import ProceduralMemory, Procedure, ProcedureExecution, ProcedureType
from aurelia.memory.strategic import StrategicMemory, StrategicLearning, LearningCategory
from aurelia.cognition.contracts import EntityRef, Hypothesis, Evidence, FactTier
from datetime import datetime


def test_working_memory():
    """Test working memory."""
    print("Testing Working Memory...")
    
    wm = WorkingMemory()
    
    # Test goal setting
    wm.set_goal("Achieve Director role within 2 years")
    assert wm.conversation_goal == "Achieve Director role within 2 years"
    
    # Test entity tracking
    entity = EntityRef(type="job_role", value="Director")
    wm.add_entity(entity)
    assert len(wm.active_entities) == 1
    
    # Test hypothesis tracking
    hypothesis = Hypothesis(
        proposition="User needs to improve strategic planning",
        probability=0.7,
        evidence=[Evidence(source="gap_analysis", reference="gap_1")]
    )
    wm.add_hypothesis(hypothesis)
    assert len(wm.current_hypotheses) == 1
    
    # Test task tracking
    task = ActiveTask(
        id="task_1",
        description="Create development plan",
        status="active",
        started_at=datetime.now(),
        priority=0.8
    )
    wm.add_task(task)
    assert len(wm.active_tasks) == 1
    
    # Test unresolved references
    wm.add_unresolved_ref("that role")
    assert len(wm.unresolved_refs) == 1
    wm.resolve_ref("that role")
    assert len(wm.unresolved_refs) == 0
    
    # Test summary
    summary = wm.get_summary()
    assert summary["active_entity_count"] == 1
    assert summary["hypothesis_count"] == 1
    assert summary["active_task_count"] == 1
    
    # Test idle check
    assert not wm.is_idle()
    wm.clear_completed_tasks()
    wm.active_tasks = []
    assert wm.is_idle()
    
    print("  Working Memory: PASS")
    return True


def test_episodic_memory():
    """Test episodic memory."""
    print("Testing Episodic Memory...")
    
    episodic = EpisodicMemory()
    
    # Test event creation
    event = episodic.create_event(
        event_type=EventType.RESUME_PARSED,
        description="User's resume was parsed successfully",
        data={"bullets_count": 15, "metrics_count": 5},
        confidence=0.95
    )
    
    assert event.event_type == EventType.RESUME_PARSED
    assert len(episodic.events) == 1
    
    # Test filtering by type
    resume_events = episodic.get_events_by_type(EventType.RESUME_PARSED)
    assert len(resume_events) == 1
    
    # Test recent events
    recent = episodic.get_recent_events(limit=5)
    assert len(recent) == 1
    
    # Test last occurrence
    last_resume = episodic.get_last_occurrence(EventType.RESUME_PARSED)
    assert last_resume is not None
    
    # Test pattern detection
    patterns = episodic.find_repeated_patterns()
    assert "resume_parsed" in patterns
    
    # Test multiple events
    episodic.create_event(EventType.INTERVIEW_SCORED, "Interview scored")
    episodic.create_event(EventType.INTERVIEW_SCORED, "Interview scored")
    episodic.create_event(EventType.INTERVIEW_SCORED, "Interview scored")
    
    patterns = episodic.find_repeated_patterns()
    assert patterns["interview_scored"] == 3
    
    print("  Episodic Memory: PASS")
    return True


def test_semantic_memory():
    """Test semantic memory."""
    print("Testing Semantic Memory...")
    
    semantic = SemanticMemory()
    
    # Test fact creation
    fact = semantic.create_fact(
        category=KnowledgeCategory.SKILL,
        subject="user",
        predicate="has_experience",
        obj="project_management",
        confidence=0.85,
        evidence=[Evidence(source="resume", reference="resume_1")],
        tier=FactTier.B
    )
    
    assert fact.category == KnowledgeCategory.SKILL
    assert fact.subject == "user"
    assert fact.confidence == 0.85
    
    # Test fact confirmation
    semantic.confirm_fact(fact.id)
    confirmed_fact = semantic.get_fact(fact.id)
    assert confirmed_fact.confirmation_count == 2
    assert confirmed_fact.confidence > 0.85
    
    # Test querying
    user_facts = semantic.get_facts_by_subject("user")
    assert len(user_facts) == 1
    
    skill_facts = semantic.get_facts_by_category(KnowledgeCategory.SKILL)
    assert len(skill_facts) == 1
    
    # Test high confidence filtering
    high_conf = semantic.get_high_confidence_facts(min_confidence=0.8)
    assert len(high_conf) >= 1
    
    # Test consolidation from episodic
    episodic_patterns = {"interview_scored": 5, "resume_parsed": 3}
    new_facts = semantic.consolidate_from_episodic(episodic_patterns, min_occurrences=3)
    assert len(new_facts) > 0
    
    print("  Semantic Memory: PASS")
    return True


def test_procedural_memory():
    """Test procedural memory."""
    print("Testing Procedural Memory...")
    
    procedural = ProceduralMemory()
    
    # Test procedure registration
    procedure = Procedure(
        name="test_procedure",
        procedure_type=ProcedureType.RESUME_AUDIT,
        description="Test procedure",
        steps=["Step 1", "Step 2"],
        required_capabilities=["test.capability"],
        success_criteria=["Success"]
    )
    procedural.register_procedure(procedure)
    
    assert len(procedural.procedures) == 1
    
    # Test procedure retrieval
    retrieved = procedural.get_procedure("test_procedure")
    assert retrieved is not None
    assert retrieved.name == "test_procedure"
    
    # Test execution recording
    execution = ProcedureExecution(
        procedure_name="test_procedure",
        timestamp=datetime.now(),
        success=True,
        execution_time_ms=150.0
    )
    procedural.record_execution(execution)
    
    assert len(procedural.execution_history) == 1
    
    # Test success rate
    success_rate = procedural.get_success_rate("test_procedure")
    assert success_rate == 1.0
    
    # Test average execution time
    avg_time = procedural.get_average_execution_time("test_procedure")
    assert avg_time == 150.0
    
    # Test default procedures
    procedural.initialize_default_procedures()
    assert len(procedural.procedures) > 1
    
    print("  Procedural Memory: PASS")
    return True


def test_strategic_memory():
    """Test strategic memory."""
    print("Testing Strategic Memory...")
    
    strategic = StrategicMemory()
    
    # Test learning creation
    learning = strategic.create_learning(
        category=LearningCategory.USER_PREFERENCE,
        proposition="User prefers actionable feedback",
        confidence=0.8,
        evidence=["Consistently asks for specific steps"],
        impact="high"
    )
    
    assert learning.category == LearningCategory.USER_PREFERENCE
    assert learning.confidence == 0.8
    assert learning.impact == "high"
    
    # Test learning confirmation
    strategic.confirm_learning(learning.id)
    confirmed = strategic.get_learning(learning.id)
    assert confirmed.confirmation_count == 2
    assert confirmed.confidence > 0.8
    
    # Test category filtering
    preference_learnings = strategic.get_learnings_by_category(LearningCategory.USER_PREFERENCE)
    assert len(preference_learnings) == 1
    
    # Test high impact filtering
    high_impact = strategic.get_high_impact_learnings()
    assert len(high_impact) == 1
    
    # Test query
    results = strategic.query("actionable")
    assert len(results) == 1
    
    # Test default learnings
    strategic.initialize_default_learnings()
    assert len(strategic.learnings) > 1
    
    print("  Strategic Memory: PASS")
    return True


def test_memory_integration():
    """Test integration between memory systems."""
    print("Testing Memory Integration...")
    
    # Create all memory systems
    working = WorkingMemory()
    episodic = EpisodicMemory()
    semantic = SemanticMemory()
    procedural = ProceduralMemory()
    strategic = StrategicMemory()
    
    # Simulate a workflow: User completes interview
    
    # 1. Working memory tracks the active task
    task = ActiveTask(
        id="interview_task",
        description="Complete interview simulation",
        status="active",
        started_at=datetime.now(),
        priority=0.9
    )
    working.add_task(task)
    
    # 2. Episodic memory records the event
    event = episodic.create_event(
        event_type=EventType.INTERVIEW_COMPLETED,
        description="User completed interview simulation",
        data={"score": 76, "duration_minutes": 15}
    )
    
    # 3. Semantic memory learns from repeated patterns
    patterns = episodic.find_repeated_patterns()
    # Add more events to create a pattern
    episodic.create_event(EventType.INTERVIEW_COMPLETED, "Interview completed")
    episodic.create_event(EventType.INTERVIEW_COMPLETED, "Interview completed")
    patterns = episodic.find_repeated_patterns()
    
    # 4. Procedural memory knows how to score interviews
    procedural.initialize_default_procedures()
    interview_procedure = procedural.get_procedure("interview_scoring_standard")
    assert interview_procedure is not None
    
    # 5. Strategic memory learns about user preferences
    strategic.initialize_default_learnings()
    
    # Verify integration
    assert len(working.active_tasks) == 1
    assert len(episodic.events) >= 3
    assert len(procedural.procedures) > 0
    assert len(strategic.learnings) > 0
    
    print("  Memory Integration: PASS")
    return True


def test_memory_summaries():
    """Test memory summary generation."""
    print("Testing Memory Summaries...")
    
    working = WorkingMemory()
    episodic = EpisodicMemory()
    semantic = SemanticMemory()
    procedural = ProceduralMemory()
    strategic = StrategicMemory()
    
    # Add some data
    working.set_goal("Test goal")
    episodic.create_event(EventType.CONVERSATION, "Test conversation")
    semantic.create_fact(
        KnowledgeCategory.SKILL,
        "user",
        "has_skill",
        "test",
        0.8,
        []
    )
    procedural.initialize_default_procedures()
    strategic.initialize_default_learnings()
    
    # Get summaries
    working_summary = working.get_summary()
    episodic_summary = episodic.get_summary()
    semantic_summary = semantic.get_summary()
    procedural_summary = procedural.get_summary()
    strategic_summary = strategic.get_summary()
    
    assert working_summary["goal"] == "Test goal"
    assert episodic_summary["total_events"] == 1
    assert semantic_summary["total_facts"] == 1
    assert procedural_summary["total_procedures"] > 0
    assert strategic_summary["total_learnings"] > 0
    
    print("  Memory Summaries: PASS")
    return True


def main():
    print("=" * 70)
    print("    AURELIA COGNITIVE OS V3 - PHASE 4 MEMORY TESTS")
    print("=" * 70)
    print()
    
    tests = [
        test_working_memory,
        test_episodic_memory,
        test_semantic_memory,
        test_procedural_memory,
        test_strategic_memory,
        test_memory_integration,
        test_memory_summaries
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
        print("SUCCESS: All Phase 4 memory tests passed!")
        print()
        print("Memory systems ready:")
        print("  - Working Memory (short-term cognitive workspace)")
        print("  - Episodic Memory (event records and patterns)")
        print("  - Semantic Memory (stable learned facts)")
        print("  - Procedural Memory (how to perform tasks)")
        print("  - Strategic Memory (meta-learnings about user)")
        print()
        print("PHASE 4 COMPLETE!")
        print()
        print("Next: Phase 5 - Goals & Planning (Goal engine, Task graphs, Dependencies, Constraint solver, Progress tracking)")
    else:
        print()
        print("FAILURE: Some tests failed. Please fix the issues.")
    
    print("=" * 70)


if __name__ == "__main__":
    main()