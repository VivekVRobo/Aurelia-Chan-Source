"""
Aurelia Cognitive OS V5 - Phase 10 Proactivity Test Suite
=========================================================
Tests event significance scoring, proactivity policy, and cooldown enforcement.
"""

import unittest
from datetime import datetime, timezone, timedelta
from aurelia.proactive.policy import EventSignificanceEngine, ProactivityPolicy


class TestV5Phase10Proactivity(unittest.TestCase):
    """Test suite for Phase 10 Proactive Autonomy."""

    def test_event_significance_scoring(self):
        """Test significance calculation for high-value vs routine events."""
        # High value: Salary offer received
        sig_offer = EventSignificanceEngine.evaluate_event("SALARY_OFFER_RECEIVED")
        self.assertGreaterEqual(sig_offer.significance_score, 0.75)
        self.assertTrue(sig_offer.requires_replan)
        
        # Low value: Routine greeting
        sig_routine = EventSignificanceEngine.evaluate_event("ROUTINE_CHAT_GREETING")
        self.assertLess(sig_routine.significance_score, 0.30)
        self.assertFalse(sig_routine.requires_replan)

    def test_proactivity_policy_approval_and_cooldown(self):
        """Test approval gating, mandatory Reason to Interrupt, and cooldown."""
        policy = ProactivityPolicy(min_significance=0.75, min_confidence=0.70, cooldown_hours=4.0)
        now = datetime.now(timezone.utc)
        sig_offer = EventSignificanceEngine.evaluate_event("SALARY_OFFER_RECEIVED")
        
        # 1. Reject if Reason to Interrupt is missing
        approved_no_reason, err = policy.should_proactively_interrupt(
            significance=sig_offer,
            confidence=0.85,
            reason_to_interrupt="",
            current_time=now
        )
        self.assertFalse(approved_no_reason)
        self.assertIn("Reason to Interrupt", err)
        
        # 2. Approve with full criteria
        valid_reason = "An external $240k offer altered your leverage on the active Director roadmap."
        approved, err = policy.should_proactively_interrupt(
            significance=sig_offer,
            confidence=0.85,
            reason_to_interrupt=valid_reason,
            current_time=now
        )
        self.assertTrue(approved)
        self.assertIsNone(err)
        
        # 3. Reject immediate subsequent attempt due to 4-hour cooldown
        subsequent_time = now + timedelta(hours=1.5)
        approved_cd, err_cd = policy.should_proactively_interrupt(
            significance=sig_offer,
            confidence=0.85,
            reason_to_interrupt=valid_reason,
            current_time=subsequent_time
        )
        self.assertFalse(approved_cd)
        self.assertIn("cooldown", err_cd.lower())


if __name__ == "__main__":
    unittest.main()
