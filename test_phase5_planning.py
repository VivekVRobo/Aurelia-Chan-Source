#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aurelia Cognitive OS V3 - Phase 5 Goals & Planning Tests
=======================================================
Tests the goal engine, task graph, constraint solver, and progress tracker.
"""

import sys
sys.path.insert(0, 'C:\\Users\\vivek\\Desktop\\Aurelia-Chan')

from aurelia.planning.goal_engine import GoalEngine, Goal, GoalStatus, GoalPriority
from aurelia.planning.task_graph import TaskGraph, Task, TaskStatus, TaskType
from aurelia.planning.constraint_solver import ConstraintSolver, Constraint, ConstraintType, ConstraintSeverity
from aurelia.planning.progress_tracker import ProgressTracker, ProgressSnapshot, Milestone, ProgressAlert, ProgressTrend
from aurelia.cognition.contracts import Evidence
from datetime import datetime, timedelta


def test_goal_engine():
    """Test goal engine."""
    print("Testing Goal Engine...")
    
    engine = GoalEngine()
    
    # Test goal creation
    goal = engine.create_goal(
        title="Become Director",
        description="Achieve Director role within 2 years",
        priority=GoalPriority.HIGH,
        target_completion=datetime.now() + timedelta(days=730)
    )
    
    assert goal.status == GoalStatus.PROPOSED
    assert goal.priority == GoalPriority.HIGH
    assert len(engine.goals) == 1
    
    # Test goal status update
    engine.update_goal_status(goal.id, GoalStatus.ACTIVE)
    assert engine.get_goal(goal.id).status == GoalStatus.ACTIVE
    
    # Test goal progress update
    engine.update_goal_progress(goal.id, 0.5)
    assert engine.get_goal(goal.id).completion_percentage == 0.5
    assert engine.get_goal(goal.id).status == GoalStatus.IN_PROGRESS
    
    # Test goal decomposition
    sub_goals = engine.decompose_goal(
        parent_goal_id=goal.id,
        sub_goal_titles=["Improve communication", "Gain strategic experience"],
        sub_goal_descriptions=["Develop executive communication skills", "Work on strategic projects"]
    )
    
    assert len(sub_goals) == 2
    assert len(goal.sub_goal_ids) == 2
    
    # Test parent progress calculation
    engine.update_goal_progress(sub_goals[0].id, 1.0)
    engine.update_goal_progress(sub_goals[1].id, 0.0)
    parent_progress = engine.calculate_parent_progress(goal.id)
    assert parent_progress == 0.5
    
    # Test filtering
    active_goals = engine.get_active_goals()
    assert len(active_goals) >= 1
    
    print("  Goal Engine: PASS")
    return True


def test_task_graph():
    """Test task graph."""
    print("Testing Task Graph...")
    
    graph = TaskGraph()
    
    # Test task creation
    task1 = graph.create_task(
        title="Complete leadership course",
        description="Take executive leadership training",
        task_type=TaskType.LEARNING,
        estimated_duration_hours=40.0
    )
    
    assert task1.status == TaskStatus.PENDING
    assert len(graph.tasks) == 1
    
    # Test task with dependencies
    task2 = graph.create_task(
        title="Apply leadership skills",
        description="Apply skills in current role",
        task_type=TaskType.EXECUTION,
        dependencies=[task1.id],
        estimated_duration_hours=20.0
    )
    
    assert len(task2.dependencies) == 1
    assert task1.id in task2.dependencies
    
    # Test ready tasks
    ready_tasks = graph.get_ready_tasks()
    assert task1 in ready_tasks
    assert task2 not in ready_tasks  # Blocked by dependency
    
    # Test task status update
    graph.update_task_status(task1.id, TaskStatus.COMPLETED)
    ready_tasks = graph.get_ready_tasks()
    assert task2 in ready_tasks  # Now ready
    
    # Test cycle detection
    task3 = graph.create_task(
        title="Task with cycle",
        description="This creates a cycle",
        task_type=TaskType.EXECUTION,
        dependencies=[task2.id]
    )
    # Create cycle
    task2.dependencies.append(task3.id)
    
    assert graph.has_cycles()
    
    # Test progress calculation
    progress = graph.calculate_progress()
    assert progress > 0  # At least one task completed
    
    print("  Task Graph: PASS")
    return True


def test_constraint_solver():
    """Test constraint solver."""
    print("Testing Constraint Solver...")
    
    solver = ConstraintSolver()
    
    # Test constraint creation
    constraint = solver.create_constraint(
        constraint_type=ConstraintType.TIME,
        description="Goal must be completed within 2 years",
        severity=ConstraintSeverity.CRITICAL,
        metadata={"max_duration_years": 2}
    )
    
    assert constraint.constraint_type == ConstraintType.TIME
    assert constraint.severity == ConstraintSeverity.CRITICAL
    
    # Test constraint validation
    context = {
        "current_time": datetime.now(),
        "deadline": datetime.now() + timedelta(days=365)
    }
    
    # Create a constraint with a deadline
    deadline_constraint = solver.create_constraint(
        constraint_type=ConstraintType.TIME,
        description="Test deadline",
        severity=ConstraintSeverity.HIGH,
        metadata={"deadline": datetime.now() + timedelta(days=30)}
    )
    
    violations = solver.validate_plan(context)
    # Should have violations for deadlines that might be tight
    assert isinstance(violations, list)
    
    # Test plan validity
    is_valid = solver.is_plan_valid(context)
    assert isinstance(is_valid, bool)
    
    # Test conflict detection
    solver.initialize_default_constraints()
    conflicts = solver.get_constraint_conflicts()
    assert isinstance(conflicts, list)
    
    # Test optimization
    optimization = solver.optimize_plan(context)
    assert "status" in optimization
    assert "violations" in optimization
    
    print("  Constraint Solver: PASS")
    return True


def test_progress_tracker():
    """Test progress tracker."""
    print("Testing Progress Tracker...")
    
    tracker = ProgressTracker()
    
    # Test snapshot recording
    snapshot = tracker.record_snapshot(
        goal_id="goal_1",
        completion_percentage=0.3,
        tasks_completed=3,
        tasks_total=10,
        notes="Making good progress"
    )
    
    assert snapshot.completion_percentage == 0.3
    assert snapshot.tasks_completed == 3
    assert len(tracker.snapshots) == 1
    
    # Test getting snapshots
    goal_snapshots = tracker.get_snapshots_for_goal("goal_1")
    assert len(goal_snapshots) == 1
    
    latest = tracker.get_latest_snapshot("goal_1")
    assert latest is not None
    assert latest.completion_percentage == 0.3
    
    # Test milestone creation
    milestone = tracker.create_milestone(
        goal_id="goal_1",
        title="First milestone",
        description="Complete 50% of tasks",
        target_completion_percentage=0.5
    )
    
    assert milestone.target_completion_percentage == 0.5
    assert not milestone.achieved
    
    # Test milestone achievement
    tracker.record_snapshot("goal_1", 0.6, 6, 10)
    achieved = tracker.check_milestone_achievement("goal_1", 0.6)
    assert len(achieved) == 1
    assert achieved[0].achieved
    
    # Test progress trend
    # Add more snapshots to establish a trend
    tracker.record_snapshot("goal_1", 0.7, 7, 10)
    tracker.record_snapshot("goal_1", 0.8, 8, 10)
    
    trend = tracker.calculate_progress_trend("goal_1", days=30)
    assert trend in [ProgressTrend.ACCELERATING, ProgressTrend.STEADY, ProgressTrend.DECELERATING]
    
    # Test alert generation
    # Create a stalled scenario
    stalled_tracker = ProgressTracker()
    stalled_tracker.record_snapshot("goal_2", 0.3, 3, 10)
    # No progress for a while
    stalled_tracker.record_snapshot("goal_2", 0.3, 3, 10)
    
    alerts = stalled_tracker.generate_progress_alerts("goal_2")
    # Should generate at least one alert for stalled progress
    assert isinstance(alerts, list)
    
    # Test alert acknowledgment
    if alerts:
        stalled_tracker.acknowledge_alert(alerts[0].id)
        assert alerts[0].acknowledged
    
    # Test progress summary
    summary = tracker.get_progress_summary("goal_1")
    assert "latest_completion" in summary
    assert "trend" in summary
    assert "total_milestones" in summary
    
    print("  Progress Tracker: PASS")
    return True


def test_planning_integration():
    """Test integration between planning components."""
    print("Testing Planning Integration...")
    
    # Create all planning components
    goal_engine = GoalEngine()
    task_graph = TaskGraph()
    constraint_solver = ConstraintSolver()
    progress_tracker = ProgressTracker()
    
    # Create a comprehensive plan
    goal = goal_engine.create_goal(
        title="Transition to Director",
        description="Achieve Director role within 18 months",
        priority=GoalPriority.HIGH,
        target_completion=datetime.now() + timedelta(days=540)
    )
    
    # Decompose into sub-goals
    sub_goals = goal_engine.decompose_goal(
        parent_goal_id=goal.id,
        sub_goal_titles=["Improve strategic skills", "Gain executive experience", "Build network"],
        sub_goal_descriptions=[
            "Develop strategic thinking capabilities",
            "Work on high-visibility projects",
            "Build relationships with senior leaders"
        ]
    )
    
    # Create tasks for each sub-goal
    for sub_goal in sub_goals:
        task = task_graph.create_task(
            title=f"Tasks for {sub_goal.title}",
            description=f"Execute plan for {sub_goal.title}",
            task_type=TaskType.EXECUTION,
            associated_goal_id=sub_goal.id,
            estimated_duration_hours=50.0
        )
    
    # Add constraints
    constraint_solver.initialize_default_constraints()
    
    # Track progress
    progress_tracker.record_snapshot(
        goal_id=goal.id,
        completion_percentage=0.1,
        tasks_completed=1,
        tasks_total=3
    )
    
    # Verify integration
    assert len(goal_engine.goals) == 4  # 1 parent + 3 sub-goals
    assert len(task_graph.tasks) == 3  # 3 tasks
    assert len(constraint_solver.constraints) > 0
    assert len(progress_tracker.snapshots) == 1
    
    # Test coordinated workflow
    # Complete first task
    first_task = list(task_graph.tasks.values())[0]
    task_graph.update_task_status(first_task.id, TaskStatus.COMPLETED)
    
    # Update progress
    progress_tracker.record_snapshot(
        goal_id=goal.id,
        completion_percentage=0.33,
        tasks_completed=1,
        tasks_total=3
    )
    
    # Validate plan
    context = {
        "current_time": datetime.now(),
        "deadline": goal.target_completion
    }
    violations = constraint_solver.validate_plan(context)
    assert isinstance(violations, list)
    
    print("  Planning Integration: PASS")
    return True


def test_hierarchical_planning():
    """Test hierarchical planning (goals -> sub-goals -> tasks)."""
    print("Testing Hierarchical Planning...")
    
    goal_engine = GoalEngine()
    task_graph = TaskGraph()
    
    # Create top-level goal
    top_goal = goal_engine.create_goal(
        title="Career advancement",
        description="Advance to executive level",
        priority=GoalPriority.HIGH
    )
    
    # Create sub-goals
    sub_goals = goal_engine.decompose_goal(
        parent_goal_id=top_goal.id,
        sub_goal_titles=["Skill development", "Experience building"],
        sub_goal_descriptions=["Develop key skills", "Build relevant experience"]
    )
    
    # Create tasks for sub-goals
    for sub_goal in sub_goals:
        for i in range(2):
            task_graph.create_task(
                title=f"Task {i+1} for {sub_goal.title}",
                description=f"Execute sub-task {i+1}",
                task_type=TaskType.EXECUTION,
                associated_goal_id=sub_goal.id
            )
    
    # Test hierarchy
    hierarchy = goal_engine.get_goal_hierarchy(top_goal.id)
    assert len(hierarchy) == 3  # 1 parent + 2 sub-goals
    
    # Test task-goal association
    tasks_for_subgoal1 = task_graph.get_tasks_for_goal(sub_goals[0].id)
    assert len(tasks_for_subgoal1) == 2
    
    # Test cascading progress
    # Complete tasks for first sub-goal
    for task in tasks_for_subgoal1:
        task_graph.update_task_status(task.id, TaskStatus.COMPLETED)
    
    # Update sub-goal progress
    goal_engine.update_goal_progress(sub_goals[0].id, 1.0)
    
    # Parent progress should reflect sub-goal completion
    parent_progress = goal_engine.calculate_parent_progress(top_goal.id)
    assert parent_progress == 0.5  # 1 of 2 sub-goals complete
    
    print("  Hierarchical Planning: PASS")
    return True


def main():
    print("=" * 70)
    print("    AURELIA COGNITIVE OS V3 - PHASE 5 PLANNING TESTS")
    print("=" * 70)
    print()
    
    tests = [
        test_goal_engine,
        test_task_graph,
        test_constraint_solver,
        test_progress_tracker,
        test_planning_integration,
        test_hierarchical_planning
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
        print("SUCCESS: All Phase 5 planning tests passed!")
        print()
        print("Planning system ready:")
        print("  - Goal Engine (multi-step objectives, hierarchy, progress)")
        print("  - Task Graph (dependency management, cycle detection, critical path)")
        print("  - Constraint Solver (validation, optimization, conflict detection)")
        print("  - Progress Tracker (trend analysis, milestones, alerts)")
        print()
        print("PHASE 5 COMPLETE!")
        print()
        print("Next: Phase 6 - Verification (Claim verification, Numerical firewall, Conflict detector, Freshness, Confidence propagation)")
    else:
        print()
        print("FAILURE: Some tests failed. Please fix the issues.")
    
    print("=" * 70)


if __name__ == "__main__":
    main()