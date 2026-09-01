"""
Aurelia Cognitive OS V6 - Phase 7 Entity Resolution Test Suite
==============================================================
Tests multimodal pronoun grounding and contextual entity linking.
"""

import unittest
from aurelia.grounding.entity_resolution import (
    MultimodalEntityResolver,
    GroundedReference
)


class TestV6Phase7EntityResolution(unittest.TestCase):
    """Test suite for Phase 7 Entity Resolution."""

    def test_pronoun_grounding_dual_offers(self):
        """Test Test A: 'Compare this with the other one' resolves to active & background docs."""
        active_doc = {"id": "doc_startup_a", "title": "Startup_Offer_A.pdf"}
        dossier = [
            {"id": "doc_startup_a", "title": "Startup_Offer_A.pdf"},
            {"id": "doc_faang_b", "title": "FAANG_Offer_B.pdf"}
        ]
        
        query = "Compare this with the other one."
        resolved = MultimodalEntityResolver.resolve_references(
            user_query=query,
            active_foreground_doc=active_doc,
            dossier_documents=dossier
        )
        
        self.assertEqual(len(resolved), 2)
        ref_map = {r.pronoun_or_phrase: r for r in resolved}
        
        # 'this' resolves to Startup_Offer_A
        self.assertIn("this", ref_map)
        self.assertEqual(ref_map["this"].target_entity_id, "doc_startup_a")
        self.assertEqual(ref_map["this"].resolution_source, "ACTIVE_FOREGROUND_DOC")
        
        # 'other' resolves to FAANG_Offer_B
        self.assertIn("other", ref_map)
        self.assertEqual(ref_map["other"].target_entity_id, "doc_faang_b")
        self.assertEqual(ref_map["other"].resolution_source, "DOSSIER_BACKGROUND_DOC")

    def test_active_code_grounding(self):
        """Test grounding 'Why did this error happen in this code?' to active editor."""
        query = "Why did this error happen in this code?"
        resolved = MultimodalEntityResolver.resolve_references(
            user_query=query,
            active_editor_code="def execute_plan():\n    raise ValueError('Missing budget')"
        )
        
        self.assertEqual(len(resolved), 1)
        self.assertEqual(resolved[0].resolution_source, "ACTIVE_EDITOR_CODE")


if __name__ == "__main__":
    unittest.main()
