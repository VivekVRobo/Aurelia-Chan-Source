"""
Aurelia Cognitive OS V6 - Local Vision Model Router
====================================================
Routes visual perception queries through the cheapest authoritative tier:
Tier 0 (OS Metadata) -> Tier 1 (Accessibility) -> Tier 2 (Document) ->
Tier 3 (Light Vision) -> Tier 4 (Deep Multimodal Vision).
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional


class VisionComplexityTier(str, Enum):
    """Hierarchy of perception tiers from cheapest to deepest."""
    TIER_0_OS_METADATA = "TIER_0_OS_METADATA"                 # Cost: 0 ms / 0 tokens
    TIER_1_ACCESSIBILITY_TREE = "TIER_1_ACCESSIBILITY_TREE"   # Cost: ~1 ms / 0 tokens
    TIER_2_STRUCTURED_DOC = "TIER_2_STRUCTURED_DOC"           # Cost: ~5 ms / 0 tokens
    TIER_3_LIGHT_VISION = "TIER_3_LIGHT_VISION"               # Cost: ~200 ms / local small vision
    TIER_4_DEEP_VISION = "TIER_4_DEEP_VISION"                 # Cost: ~1200 ms / local deep vision


@dataclass(frozen=True)
class VisionRoutingDecision:
    """Routing decision for perceptual analysis."""
    selected_tier: VisionComplexityTier
    recommended_model: Optional[str]
    rationale: str
    estimated_latency_ms: float


class LocalVisionRouter:
    """
    Selects the lowest-cost tier capable of resolving the user's perception need.
    """

    @classmethod
    def route_perception(
        cls,
        has_accessibility_tree: bool,
        is_structured_text: bool,
        requires_diagram_interpretation: bool,
        has_unstructured_pixels_only: bool
    ) -> VisionRoutingDecision:
        """Determines the cheapest sufficient vision tier."""
        # Case 1: Pure structured document text available
        if is_structured_text:
            return VisionRoutingDecision(
                selected_tier=VisionComplexityTier.TIER_2_STRUCTURED_DOC,
                recommended_model=None,
                rationale="Document possesses structured text; zero vision inference needed.",
                estimated_latency_ms=5.0
            )

        # Case 2: Rich native OS Accessibility Tree available
        if has_accessibility_tree and not requires_diagram_interpretation:
            return VisionRoutingDecision(
                selected_tier=VisionComplexityTier.TIER_1_ACCESSIBILITY_TREE,
                recommended_model=None,
                rationale="Native accessibility tree provides full UI controls; zero vision inference needed.",
                estimated_latency_ms=1.0
            )

        # Case 3: Dense chart, graph, or architectural diagram
        if requires_diagram_interpretation:
            return VisionRoutingDecision(
                selected_tier=VisionComplexityTier.TIER_4_DEEP_VISION,
                recommended_model="llava:13b",
                rationale="Complex diagram requires deep multimodal spatial and relational reasoning.",
                estimated_latency_ms=1200.0
            )

        # Case 4: Unstructured pixel bitmap without accessibility
        if has_unstructured_pixels_only:
            return VisionRoutingDecision(
                selected_tier=VisionComplexityTier.TIER_3_LIGHT_VISION,
                recommended_model="minicpm-v:latest",
                rationale="Unstructured pixel bitmap requires lightweight layout and OCR vision.",
                estimated_latency_ms=250.0
            )

        # Default fallback: Tier 0 OS metadata
        return VisionRoutingDecision(
            selected_tier=VisionComplexityTier.TIER_0_OS_METADATA,
            recommended_model=None,
            rationale="Standard OS process and window metadata is sufficient.",
            estimated_latency_ms=0.5
        )
