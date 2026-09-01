"""
Aurelia Cognitive OS V4 - Phase 2 Memory & Write Firewall Test Suite
=====================================================================
Tests UserDossier V2, MemoryWritePolicy Firewall, MemoryConflictEngine,
and HybridMemoryRetriever.
"""

import unittest
from datetime import datetime, timezone, timedelta
from aurelia.contracts.core_types import ClaimType, EvidenceRef, EvidenceReliability, Fact, UserGoal
from aurelia.memory.user_dossier import UserDossier, CareerTimelineEvent, CompensationRecord
from aurelia.memory.write_policy import MemoryWritePolicy, MemoryCandidate
from aurelia.memory.conflicts import MemoryConflictEngine, GoalSupersessionEvent
from aurelia.memory.retrieval import HybridMemoryRetriever, RetrievedMemoryItem


class TestPhase2Memory(unittest.TestCase):
    """Test suite for Phase 2 Memory & Firewall."""

    def test_user_dossier_and_active_goal_retrieval(self):
        """Test UserDossier structure and goal resolution."""
        goal1 = UserGoal(id="g_01", title="Director of Engineering", target_role="Director of Engineering", status="active")
        dossier = UserDossier(
            user_id="usr_01",
            full_name="Alex Mercer",
            current_role="Senior Engineering Manager",
            current_level="L6",
            target_role="Director of Engineering",
            years_experience=12.0,
            active_goals=[goal1]
        )
        self.assertEqual(dossier.get_active_goal(), goal1)

    def test_memory_write_firewall_rejection_no_evidence(self):
        """Invariant: Proposed Facts without evidence MUST be rejected."""
        candidate = MemoryCandidate(
            candidate_id="cand_01",
            claim_type=ClaimType.FACT,
            key="managed_budget_amount",
            value=3000000.0,
            evidence=(),  # Empty evidence
            proposed_by="unverified_llm_inference",
            confidence=0.85
        )
        result = MemoryWritePolicy.evaluate_candidate(candidate, existing_facts=[])
        self.assertFalse(result.approved)
        self.assertIn("require non-empty verifiable evidence", result.rejection_reason)

    def test_memory_write_firewall_rejection_low_confidence(self):
        """Invariant: Facts with low confidence MUST be rejected."""
        ev = EvidenceRef(id="ev_01", source_type="unclear_note", content_snippet="maybe led team")
        candidate = MemoryCandidate(
            candidate_id="cand_02",
            claim_type=ClaimType.FACT,
            key="team_size",
            value=10,
            evidence=(ev,),
            proposed_by="llm_guess",
            confidence=0.55 # Below 0.70 threshold
        )
        result = MemoryWritePolicy.evaluate_candidate(candidate, existing_facts=[])
        self.assertFalse(result.approved)
        self.assertIn("below required threshold", result.rejection_reason)

    def test_memory_write_firewall_approves_verified_candidate(self):
        """Verified candidates are committed to canonical Fact."""
        ev = EvidenceRef(id="ev_02", source_type="w2_tax_doc", content_snippet="2025 base salary $215k", reliability=EvidenceReliability.VERIFIED_DOCUMENT)
        candidate = MemoryCandidate(
            candidate_id="cand_03",
            claim_type=ClaimType.FACT,
            key="base_salary",
            value=215000.0,
            evidence=(ev,),
            proposed_by="resume_parser_v4",
            confidence=0.95
        )
        result = MemoryWritePolicy.evaluate_candidate(candidate, existing_facts=[])
        self.assertTrue(result.approved)
        self.assertIsNotNone(result.committed_fact)
        self.assertEqual(result.committed_fact.object_value, 215000.0)

    def test_goal_supersession_engine(self):
        """Test clean goal transition without historical data loss."""
        g_old = UserGoal(id="g_01", title="Director of Engineering", target_role="Director of Engineering", status="active")
        g_new = UserGoal(id="g_02", title="Staff Engineer Track", target_role="Staff Engineer", status="active")
        
        updated_goals, super_event = MemoryConflictEngine.resolve_goal_update(
            existing_goals=[g_old],
            new_goal=g_new,
            reason="User decided to pursue individual contributor technical leadership"
        )
        
        self.assertEqual(len(updated_goals), 2)
        # Check old goal is superseded
        self.assertEqual(updated_goals[0].status, "superseded")
        # Check new goal is active
        self.assertEqual(updated_goals[1].status, "active")
        self.assertIsNotNone(super_event)
        self.assertEqual(super_event.old_goal_title, "Director of Engineering")
        self.assertEqual(super_event.new_goal_title, "Staff Engineer Track")

    def test_hybrid_memory_retriever(self):
        """Test multi-signal hybrid ranking."""
        now = datetime.now(timezone.utc)
        items = [
            {
                "id": "mem_01",
                "content": "Led Q3 budgeting and reduced cloud infrastructure expenses by $450k.",
                "timestamp": now - timedelta(days=5),
                "reliability_weight": 0.90,
                "source_type": "quarterly_review"
            },
            {
                "id": "mem_02",
                "content": "Discussed interest in basketball and casual hobbies.",
                "timestamp": now - timedelta(days=2),
                "reliability_weight": 0.40,
                "source_type": "chat"
            },
            {
                "id": "mem_03",
                "content": "Completed Director leadership transition course covering organizational P&L.",
                "timestamp": now - timedelta(days=10),
                "reliability_weight": 0.85,
                "source_type": "training_record"
            }
        ]
        
        goal = UserGoal(id="g_01", title="Director", target_role="Director", success_conditions=("P&L accountability",), status="active")
        
        results = HybridMemoryRetriever.retrieve(
            query_text="What evidence do we have regarding budget ownership for Director role?",
            query_entities=["budget", "Director"],
            active_goal=goal,
            candidate_items=items,
            now=now,
            top_k=2
        )
        
        self.assertEqual(len(results), 2)
        # Top result should be budget or director relevant item
        self.assertIn("mem_01", [results[0].item_id, results[1].item_id])
        self.assertIn("mem_03", [results[0].item_id, results[1].item_id])
        self.assertNotIn("mem_02", [r.item_id for r in results])


if __name__ == "__main__":
    unittest.main()
