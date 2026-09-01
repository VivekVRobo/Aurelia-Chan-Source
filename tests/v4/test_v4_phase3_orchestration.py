"""
Aurelia Cognitive OS V4 - Phase 3 Orchestration Test Suite
===========================================================
Tests Active Goal Engine, Cognitive Router, and Cognitive DAG Planner.
"""

import unittest
from datetime import datetime, timezone
from aurelia.goals.model import ActiveGoalTracker, GoalMilestone
from aurelia.contracts.core_types import EvidenceRef, EvidenceReliability
from aurelia.contracts.meaning_frame import MeaningFrame, IntentType
from aurelia.cognition.router import CognitiveRouter, CognitiveComplexityMode, CognitiveBudget
from aurelia.cognition.planner import CognitivePlanner, CognitivePlan, PlanNode


class TestPhase3Orchestration(unittest.TestCase):
    """Test suite for Phase 3 Goal Tracking & Orchestration."""

    def test_active_goal_evidence_resolution_and_progress(self):
        """Test automatic milestone completion upon evidence observation."""
        m1 = GoalMilestone(
            milestone_id="m_01",
            title="Complete Executive Finance & Budgeting Course",
            target_competency_id="comp_budget",
            required_evidence_type="course_completion"
        )
        m2 = GoalMilestone(
            milestone_id="m_02",
            title="Deliver Q3 Multi-Department Planning Review",
            target_competency_id="comp_strategic",
            required_evidence_type="presentation"
        )
        
        tracker = ActiveGoalTracker(
            goal_id="goal_director",
            target_role="Director of Engineering",
            target_compensation_usd=320000.0,
            deadline=None,
            milestones=[m1, m2]
        )
        
        self.assertEqual(tracker.overall_progress_pct, 0.0)
        
        # Ingest incoming evidence
        ev = EvidenceRef(id="ev_01", source_type="cert", content_snippet="Finance & Budgeting course completed", reliability=EvidenceReliability.VERIFIED_DOCUMENT)
        msg = tracker.resolve_incoming_evidence("I finished the Executive Finance & Budgeting Course today.", ev)
        
        self.assertIsNotNone(msg)
        self.assertIn("marked COMPLETED", msg)
        self.assertEqual(tracker.overall_progress_pct, 50.0)
        self.assertTrue(tracker.milestones[0].is_completed)
        self.assertFalse(tracker.milestones[1].is_completed)

    def test_cognitive_router_reflex_mode(self):
        """Test reflex mode routing for lookup inquiries."""
        meaning = MeaningFrame(
            frame_id="mf_01",
            raw_input="What was my last interview score?",
            intent=IntentType.STATUS_INQUIRY
        )
        budget = CognitiveRouter.classify(meaning)
        self.assertEqual(budget.mode, CognitiveComplexityMode.REFLEX)
        self.assertEqual(budget.max_llm_calls, 0) # Zero LLM calls for lookup

    def test_cognitive_router_deep_mode(self):
        """Test deep mode routing for high-stakes decisions."""
        meaning = MeaningFrame(
            frame_id="mf_02",
            raw_input="Should I accept the startup offer or stay at FAANG?",
            intent=IntentType.DECISION_EVALUATION
        )
        budget = CognitiveRouter.classify(meaning)
        self.assertEqual(budget.mode, CognitiveComplexityMode.DEEP)
        self.assertTrue(budget.max_llm_calls >= 2)
        self.assertTrue(budget.max_simulations >= 1000)

    def test_cognitive_planner_dag_compilation(self):
        """Test DAG compilation for deep strategy plan."""
        meaning = MeaningFrame(
            frame_id="mf_03",
            raw_input="Compare compensation packages",
            intent=IntentType.COMPENSATION_STRATEGY
        )
        budget = CognitiveRouter.classify(meaning)
        plan = CognitivePlanner.compile(meaning, budget)
        
        self.assertIsInstance(plan, CognitivePlan)
        self.assertEqual(plan.budget.mode, CognitiveComplexityMode.DEEP)
        self.assertEqual(len(plan.nodes), 9)
        self.assertEqual(plan.entry_node_id, "parse_offer")
        self.assertEqual(plan.exit_node_id, "renderer")


if __name__ == "__main__":
    unittest.main()
