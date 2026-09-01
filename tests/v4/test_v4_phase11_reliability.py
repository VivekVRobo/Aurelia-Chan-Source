"""
Aurelia Cognitive OS V4 - Phase 11 Production Reliability Test Suite
=====================================================================
Tests SQLite ACID transactions, rollback integrity, and PrivacyGuard redaction.
"""

import unittest
from aurelia.persistence.database import CognitiveDatabase
from aurelia.persistence.security import PrivacyGuard


class TestPhase11Reliability(unittest.TestCase):
    """Test suite for Phase 11 Reliability & Security."""

    def test_database_acid_transaction_commit_and_lookup(self):
        """Test atomic commit of decision receipt and executive artifacts."""
        db = CognitiveDatabase(":memory:")
        
        art = {
            "id": "art_101",
            "type": "roadmap_90_day",
            "title": "90-Day Plan",
            "version": 1,
            "payload": {"milestones": []}
        }
        
        success = db.save_cognitive_cycle_transaction(
            decision_id="dec_01",
            snapshot_id="snap_01",
            request_text="How do I prepare for VP interviews?",
            intent_type="career_roadmap",
            conclusion="Focus on executive P&L accountability.",
            confidence=0.90,
            artifacts=[art]
        )
        
        self.assertTrue(success)
        receipt = db.get_decision_receipt("dec_01")
        self.assertIsNotNone(receipt)
        self.assertEqual(receipt["conclusion_summary"], "Focus on executive P&L accountability.")

    def test_database_rollback_on_duplicate_key(self):
        """Test transaction rollback on duplicate primary key collision."""
        db = CognitiveDatabase(":memory:")
        
        art = {"id": "art_01", "type": "script", "title": "Script", "version": 1, "payload": {}}
        
        # First commit succeeds
        db.save_cognitive_cycle_transaction("dec_dup", "s1", "text", "intent", "conclusion", 0.8, [art])
        
        # Second commit with duplicate decision_id fails and rolls back
        fail_success = db.save_cognitive_cycle_transaction("dec_dup", "s1", "text", "intent", "conclusion", 0.8, [art])
        self.assertFalse(fail_success)

    def test_privacy_guard_redaction(self):
        """Test sensitive email and phone number redaction in logs."""
        raw_log = "Candidate contact: alex.mercer@enterprise.com, phone 415-555-2671."
        redacted = PrivacyGuard.redact_sensitive_text(raw_log)
        self.assertNotIn("alex.mercer@enterprise.com", redacted)
        self.assertNotIn("415-555-2671", redacted)
        self.assertIn("[EMAIL REDACTED]", redacted)
        self.assertIn("[PHONE REDACTED]", redacted)


if __name__ == "__main__":
    unittest.main()
