"""
Aurelia Cognitive OS V6 - Phase 9 Attention & Purpose Test Suite
================================================================
Tests purpose-bound perception requests and attention threshold filtering.
"""

import unittest
from aurelia.routing.attention import (
    PerceptionRequest,
    AttentionEngine,
    AttentionScore
)
from aurelia.contracts.v6_contracts import Modality


class TestV6Phase9AttentionAndPurpose(unittest.TestCase):
    """Test suite for Phase 9 Attention & Purpose Limitation."""

    def test_perception_request_purpose_binding(self):
        """Test explicit purpose declaration and region scoping."""
        req = PerceptionRequest(
            request_id="req_001",
            modality=Modality.SCREEN,
            purpose="resolve_user_reference",
            requested_regions=("header_region", "compensation_table")
        )
        self.assertEqual(req.purpose, "resolve_user_reference")
        self.assertEqual(len(req.requested_regions), 2)

    def test_attention_score_gating(self):
        """Test high-interaction active element passes while background noise is filtered."""
        # High active focus (active window, clicked, relevant to query)
        score_active = AttentionEngine.calculate_attention(
            recency=0.95,
            user_interaction=1.0,
            semantic_relevance=0.85,
            threshold=0.65
        )
        self.assertTrue(score_active.passes_threshold)
        self.assertGreater(score_active.composite_score, 0.85)

        # Background noise (old notification, 0 interaction, low relevance)
        score_noise = AttentionEngine.calculate_attention(
            recency=0.20,
            user_interaction=0.0,
            semantic_relevance=0.10,
            threshold=0.65
        )
        self.assertFalse(score_noise.passes_threshold)
        self.assertLess(score_noise.composite_score, 0.20)


if __name__ == "__main__":
    unittest.main()
