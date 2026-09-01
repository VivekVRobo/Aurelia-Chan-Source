"""
Aurelia Cognitive OS V6 - Phase 2 Document Intelligence Test Suite
===================================================================
Tests document parsing, structural segmentation, entity extraction, and cross-document comparison.
"""

import unittest
from aurelia.documents.parser import UniversalDocumentParser
from aurelia.documents.cross_document import CrossDocumentGraph


class TestV6Phase2DocumentIntelligence(unittest.TestCase):
    """Test suite for Phase 2 Document Intelligence."""

    def test_document_parsing_and_provenance(self):
        """Test structural segmentation and entity extraction from an offer letter."""
        sample_offer = (
            "# Offer Letter\n"
            "We are pleased to offer you the position of Director of Engineering.\n\n"
            "# Compensation\n"
            "Base Salary: $240,000 per annum with standard executive benefits.\n"
            "You will lead an engineering team of 18 engineers.\n"
        )
        
        parsed = UniversalDocumentParser.parse_document(
            doc_id="offer_startup_a",
            file_path="C:/docs/Offer_Startup_A.pdf",
            text_content=sample_offer,
            doc_type="OFFER_LETTER"
        )
        
        self.assertEqual(parsed.doc_id, "offer_startup_a")
        self.assertGreaterEqual(len(parsed.sections), 2)
        
        # Verify extracted entities
        entity_types = {e.entity_type: e.normalized_value for e in parsed.extracted_entities}
        self.assertEqual(entity_types.get("COMPENSATION_AMOUNT"), 240000.0)
        self.assertEqual(entity_types.get("TARGET_ROLE"), "Director")
        self.assertEqual(entity_types.get("TEAM_SIZE"), 18)

    def test_cross_document_graph_comparison(self):
        """Test cross-document entity comparison between two competing offers."""
        graph = CrossDocumentGraph()
        
        doc_a = UniversalDocumentParser.parse_document(
            doc_id="offer_a",
            file_path="C:/docs/Offer_A.pdf",
            text_content="Base Salary: $240,000 for Senior Engineering Manager",
            doc_type="OFFER_LETTER"
        )
        doc_b = UniversalDocumentParser.parse_document(
            doc_id="offer_b",
            file_path="C:/docs/Offer_B.pdf",
            text_content="Base Salary: $280,000 for Director of Engineering",
            doc_type="OFFER_LETTER"
        )
        
        graph.add_document(doc_a)
        graph.add_document(doc_b)
        
        comp_map = graph.compare_compensation_across_documents()
        self.assertEqual(comp_map.get("offer_a"), 240000.0)
        self.assertEqual(comp_map.get("offer_b"), 280000.0)
        self.assertGreater(comp_map["offer_b"], comp_map["offer_a"])


if __name__ == "__main__":
    unittest.main()
