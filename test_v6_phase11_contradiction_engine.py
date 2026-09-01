"""
Aurelia Cognitive OS V6 - Phase 11 Contradiction Engine Test Suite
==================================================================
Tests multi-source conflict detection, severity classification, and non-override.
"""

import unittest
from aurelia.grounding.contradiction import (
    MultimodalContradictionEngine,
    PerceptualConflict
)
from aurelia.contracts.v6_contracts import ConflictSeverity


class TestV6Phase11ContradictionEngine(unittest.TestCase):
    """Test suite for Phase 11 Contradiction Engine."""

    def test_temporal_conflict_detection(self):
        """Invariant: Test B - Calendar screenshot vs user speech must detect critical conflict."""
        conflict = MultimodalContradictionEngine.evaluate_conflict(
            entity_type="INTERVIEW_DATE",
            source_a_label="Calendar Screenshot",
            val_a="Tuesday 3 PM",
            source_b_label="User Speech Statement",
            val_b="Wednesday 3 PM"
        )
        
        self.assertIsNotNone(conflict)
        self.assertEqual(conflict.severity, ConflictSeverity.CRITICAL)
        self.assertIn("Temporal interview conflict", conflict.explanation)
        self.assertIn("Tuesday 3 PM", conflict.explanation)
        self.assertIn("Wednesday 3 PM", conflict.explanation)

    def test_material_compensation_mismatch(self):
        """Test compensation mismatch (₹28L vs ₹38L) classified as MATERIAL."""
        conflict = MultimodalContradictionEngine.evaluate_conflict(
            entity_type="COMPENSATION_AMOUNT",
            source_a_label="Offer Letter PDF",
            val_a=2800000.0,
            source_b_label="User Claim",
            val_b=3800000.0
        )
        self.assertIsNotNone(conflict)
        self.assertEqual(conflict.severity, ConflictSeverity.MATERIAL)

    def test_minor_team_size_mismatch(self):
        """Test small team size difference (11 vs 12) classified as MINOR."""
        conflict = MultimodalContradictionEngine.evaluate_conflict(
            entity_type="TEAM_SIZE",
            source_a_label="Resume Bullet",
            val_a=11,
            source_b_label="Interview Transcript",
            val_b=12
        )
        self.assertIsNotNone(conflict)
        self.assertEqual(conflict.severity, ConflictSeverity.MINOR)


if __name__ == "__main__":
    unittest.main()
