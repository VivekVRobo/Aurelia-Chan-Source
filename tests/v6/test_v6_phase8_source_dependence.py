"""
Aurelia Cognitive OS V6 - Phase 8 Source Dependence Test Suite
==============================================================
Tests source dependence DAG and non-compounding co-dependent evidence guards.
"""

import unittest
from aurelia.grounding.evidence_fusion import (
    SourceDependenceGraph,
    EvidenceFusionEngine,
    FusedEvidence
)
from aurelia.contracts.v6_contracts import ObservationSource


class TestV6Phase8SourceDependence(unittest.TestCase):
    """Test suite for Phase 8 Source Dependence & Fusion."""

    def test_single_root_source_no_confidence_explosion(self):
        """Invariant: Test D - OCR + Vision on same screenshot must count as 1 root source."""
        graph = SourceDependenceGraph()
        
        # Two observations derived from the SAME screenshot (root_snap_100)
        rec1 = graph.register_observation("obs_ocr_01", "root_snap_100", ObservationSource.OCR_EXTRACTOR)
        rec2 = graph.register_observation("obs_vis_02", "root_snap_100", ObservationSource.LIGHT_VISION)
        
        self.assertTrue(rec2.is_composite)
        
        # Fuse evidence from both observations
        obs_data = [
            ("obs_ocr_01", 0.85, "root_snap_100"),
            ("obs_vis_02", 0.88, "root_snap_100")
        ]
        fused = EvidenceFusionEngine.fuse_evidence("Compensation is $230k", obs_data)
        
        # Must count as only 1 independent root source, max confidence = 0.88 (not 0.98)
        self.assertEqual(fused.independent_root_sources_count, 1)
        self.assertEqual(fused.fused_confidence, 0.88)
        self.assertFalse(fused.is_multi_source_verified)

    def test_truly_independent_source_fusion(self):
        """Test fusion of two separate independent root sources compounds confidence."""
        obs_data = [
            ("obs_email_01", 0.85, "root_email_doc_401"),
            ("obs_user_speech", 0.90, "root_mic_audio_702")
        ]
        fused = EvidenceFusionEngine.fuse_evidence("Interview scheduled for Friday", obs_data)
        
        # 1 - (1 - 0.85)(1 - 0.90) = 1 - (0.15 * 0.10) = 1 - 0.015 = 0.985
        self.assertEqual(fused.independent_root_sources_count, 2)
        self.assertGreaterEqual(fused.fused_confidence, 0.98)
        self.assertTrue(fused.is_multi_source_verified)


if __name__ == "__main__":
    unittest.main()
