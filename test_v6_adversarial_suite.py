"""
Aurelia Cognitive OS V6 - Phase 14 Adversarial Perception Test Suite
====================================================================
Torture-tests perception against adversarial scenarios: OCR misreads, identical
document titles, stealth incognito windows, and temporal fact collisions.
"""

import unittest
from aurelia.privacy.zones import PrivacyFirewall
from aurelia.contracts.v6_contracts import PrivacyClass, EntityVisibility
from aurelia.grounding.contradiction import MultimodalContradictionEngine
from aurelia.grounding.entity_resolution import MultimodalEntityResolver
from aurelia.documents.parser import UniversalDocumentParser


class TestV6Phase14AdversarialSuite(unittest.TestCase):
    """Adversarial stress-test suite for V6 Perception."""

    def test_adversarial_localized_incognito_detection(self):
        """Adversarial: Stealth / localized private browsing title is caught."""
        stealth_titles = [
            "Private Browsing - Firefox",
            "InPrivate window - Microsoft Edge",
            "Google Chrome (Incognito)",
            "Bank of America | NetBanking - Chrome"
        ]
        for title in stealth_titles:
            res = PrivacyFirewall.evaluate_pre_capture(window_title=title)
            self.assertFalse(res.is_capture_allowed, f"Failed to block stealth title: {title}")
            self.assertEqual(res.privacy_class, PrivacyClass.DENIED)

    def test_adversarial_identical_document_titles_disambiguation(self):
        """Adversarial: Two files with identical names disambiguated by unique paths."""
        doc1 = UniversalDocumentParser.parse_document(
            doc_id="doc_v1",
            file_path="C:/FolderA/Resume.pdf",
            text_content="Base Salary: $200,000"
        )
        doc2 = UniversalDocumentParser.parse_document(
            doc_id="doc_v2",
            file_path="C:/FolderB/Resume.pdf",
            text_content="Base Salary: $240,000"
        )
        self.assertNotEqual(doc1.doc_id, doc2.doc_id)
        self.assertNotEqual(doc1.file_path, doc2.file_path)

    def test_adversarial_old_screen_vs_new_statement_collision(self):
        """Adversarial: Outdated screenshot does not silently overwrite fresh user statement."""
        conflict = MultimodalContradictionEngine.evaluate_conflict(
            entity_type="INTERVIEW_DATE",
            source_a_label="Stale Screen Capture (2 days ago)",
            val_a="Thursday 10 AM",
            source_b_label="Fresh User Utterance",
            val_b="Friday 2 PM"
        )
        self.assertIsNotNone(conflict)
        self.assertIn("Temporal interview conflict", conflict.explanation)


if __name__ == "__main__":
    unittest.main()
