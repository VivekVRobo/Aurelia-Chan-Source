"""
Aurelia Cognitive OS V6 - Phase 5 Vision Router Test Suite
==========================================================
Tests tiered perception complexity routing and zero-vision optimization.
"""

import unittest
from aurelia.screen.vision_router import (
    VisionComplexityTier,
    LocalVisionRouter
)


class TestV6Phase5VisionRouter(unittest.TestCase):
    """Test suite for Phase 5 Vision Router."""

    def test_structured_doc_zero_vision(self):
        """Test structured document routes to Tier 2 with no vision models."""
        decision = LocalVisionRouter.route_perception(
            has_accessibility_tree=False,
            is_structured_text=True,
            requires_diagram_interpretation=False,
            has_unstructured_pixels_only=False
        )
        self.assertEqual(decision.selected_tier, VisionComplexityTier.TIER_2_STRUCTURED_DOC)
        self.assertIsNone(decision.recommended_model)
        self.assertLess(decision.estimated_latency_ms, 10.0)

    def test_accessibility_tree_zero_vision(self):
        """Test accessibility tree routes to Tier 1 with zero vision models."""
        decision = LocalVisionRouter.route_perception(
            has_accessibility_tree=True,
            is_structured_text=False,
            requires_diagram_interpretation=False,
            has_unstructured_pixels_only=False
        )
        self.assertEqual(decision.selected_tier, VisionComplexityTier.TIER_1_ACCESSIBILITY_TREE)
        self.assertIsNone(decision.recommended_model)

    def test_diagram_routes_to_deep_vision(self):
        """Test complex diagram routes to Tier 4 deep vision."""
        decision = LocalVisionRouter.route_perception(
            has_accessibility_tree=False,
            is_structured_text=False,
            requires_diagram_interpretation=True,
            has_unstructured_pixels_only=True
        )
        self.assertEqual(decision.selected_tier, VisionComplexityTier.TIER_4_DEEP_VISION)
        self.assertIsNotNone(decision.recommended_model)


if __name__ == "__main__":
    unittest.main()
