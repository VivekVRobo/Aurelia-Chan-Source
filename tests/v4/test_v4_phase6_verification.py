"""
Aurelia Cognitive OS V4 - Phase 6 Verification Firewall Test Suite
===================================================================
Tests Master Verification Firewall, SycophancyGuard, and Issue Severity.
"""

import unittest
from aurelia.contracts.core_types import VerificationSeverity
from aurelia.verification.sycophancy import SycophancyGuard
from aurelia.verification.firewall import MasterVerificationFirewall, VerificationReport


class TestPhase6Verification(unittest.TestCase):
    """Test suite for Phase 6 Verification Firewall."""

    def test_sycophancy_guard_strips_unearned_flattery(self):
        """Test unearned flattery detection without supporting evidence."""
        flattery_text = "Don't worry you are a genius and you will get it easily."
        res = SycophancyGuard.audit_prose(flattery_text, has_corroborating_evidence=False)
        self.assertFalse(res.is_acceptable)
        self.assertTrue(res.flagged_flattery)

    def test_sycophancy_guard_preserves_evidence_backed_positive_feedback(self):
        """Test legitimate positive feedback with quantitative metrics is preserved."""
        metric_text = "Your interview performance improved from 68 to 74 to 82 across 3 mock sessions."
        res = SycophancyGuard.audit_prose(metric_text, has_corroborating_evidence=True)
        self.assertTrue(res.is_acceptable)
        self.assertFalse(res.flagged_flattery)
        self.assertEqual(res.sanitized_text, metric_text)

    def test_verification_firewall_blocks_arithmetic_errors(self):
        """Invariant: Blockers prevent response publication."""
        report = MasterVerificationFirewall.verify(
            prose_text="Your total compensation will be $350k.",
            numeric_checks=[("Base + Equity Sum", 350000.0, 420000.0)], # Discrepancy
            has_evidence=True
        )
        self.assertFalse(report.passed)
        self.assertFalse(report.is_safe_to_publish)
        self.assertEqual(report.max_severity, VerificationSeverity.BLOCKER)
        self.assertEqual(len(report.issues), 1)
        self.assertEqual(report.issues[0].issue_type, "NUMERIC_MISMATCH")

    def test_verification_firewall_approves_verified_output(self):
        """Test verified output passes with INFO severity."""
        report = MasterVerificationFirewall.verify(
            prose_text="Your verified total compensation is $349,000 annualized.",
            numeric_checks=[("Base + Bonus + Equity Sum", 349000.0, 349000.0)], # Exact match
            has_evidence=True
        )
        self.assertTrue(report.passed)
        self.assertTrue(report.is_safe_to_publish)
        self.assertEqual(len(report.verified_numerical_checks), 1)
        self.assertIn("349000.0", report.verified_numerical_checks[0])


if __name__ == "__main__":
    unittest.main()
