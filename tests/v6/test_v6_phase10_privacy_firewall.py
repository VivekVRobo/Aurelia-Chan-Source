"""
Aurelia Cognitive OS V6 - Phase 10 Privacy Firewall Test Suite
==============================================================
Tests pre-capture denial of password managers, banking apps, and incognito windows.
"""

import unittest
from aurelia.privacy.zones import PrivacyFirewall
from aurelia.contracts.v6_contracts import PrivacyClass


class TestV6Phase10PrivacyFirewall(unittest.TestCase):
    """Test suite for Phase 10 Privacy Firewall."""

    def test_password_manager_blocked_before_capture(self):
        """Invariant: Test C - Password manager process must block 100% of capture."""
        res = PrivacyFirewall.evaluate_pre_capture(process_name="bitwarden.exe")
        self.assertFalse(res.is_capture_allowed)
        self.assertEqual(res.privacy_class, PrivacyClass.DENIED)
        self.assertIn("bitwarden.exe", res.matched_denial_rule)

    def test_incognito_window_blocked_before_capture(self):
        """Test incognito browsing window is blocked before capture."""
        res = PrivacyFirewall.evaluate_pre_capture(window_title="Google Chrome - [Incognito]")
        self.assertFalse(res.is_capture_allowed)
        self.assertEqual(res.privacy_class, PrivacyClass.DENIED)
        self.assertIn("incognito", res.matched_denial_rule)

    def test_restricted_file_path_blocked(self):
        """Test restricted SSH or tax path is blocked."""
        res = PrivacyFirewall.evaluate_pre_capture(file_path="C:/Users/test/.ssh/id_rsa")
        self.assertFalse(res.is_capture_allowed)
        self.assertEqual(res.privacy_class, PrivacyClass.DENIED)

    def test_legitimate_work_window_allowed(self):
        """Test standard coding and document windows pass pre-capture checks."""
        res = PrivacyFirewall.evaluate_pre_capture(
            process_name="Code.exe",
            window_title="Aurelia - Visual Studio Code",
            file_path="C:/Users/test/Offer_Letter.pdf"
        )
        self.assertTrue(res.is_capture_allowed)
        self.assertEqual(res.privacy_class, PrivacyClass.PUBLIC)
        self.assertIsNone(res.matched_denial_rule)


if __name__ == "__main__":
    unittest.main()
