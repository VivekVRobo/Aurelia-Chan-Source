"""
Aurelia Cognitive OS V6 - Phase 0 Contracts Test Suite
======================================================
Tests V6 contracts, immutability, quality fields, and epistemic invariants.
"""

import unittest
from datetime import datetime, timezone, timedelta
from aurelia.contracts.v6_contracts import (
    Modality,
    ObservationSource,
    PrivacyClass,
    ObservationPromotionStage,
    ConflictSeverity,
    SessionMode,
    EntityVisibility,
    EntityExistence,
    Provenance,
    ObservationQuality,
    ObservedEntity,
    ObservedEntityState,
    ObservationPayload,
    Observation,
    ObservationSession,
    SourceDependencyRecord,
    PerceptionReceipt,
    ContextCandidate,
    ContextCandidateSet
)


class TestV6Phase0Contracts(unittest.TestCase):
    """Test suite for Phase 0 V6 Contracts."""

    def test_observation_contract_immutability(self):
        """Test Observation frozen dataclass immutability and provenance."""
        now = datetime.now(timezone.utc)
        provenance = Provenance(
            root_source_id="screen_snap_001",
            source_type=ObservationSource.ACCESSIBILITY_TREE,
            file_path="C:/Users/test/Resume.pdf",
            page_or_region="Page 1 Header"
        )
        quality = ObservationQuality(
            confidence=0.92,
            completeness=0.88,
            ambiguity=0.05,
            source_reliability=0.95,
            freshness=1.0
        )
        entity = ObservedEntity(
            entity_id="ent_comp_01",
            entity_type="COMPENSATION_AMOUNT",
            raw_text="$220,000",
            normalized_value=220000.0,
            confidence=0.95
        )
        payload = ObservationPayload(
            structured_data={"base_salary": 220000.0},
            summary_text="Base salary extracted from header.",
            raw_token_count=12
        )
        obs = Observation(
            observation_id="obs_001",
            session_id="sess_100",
            modality=Modality.SCREEN,
            source=ObservationSource.ACCESSIBILITY_TREE,
            observed_at=now,
            expires_at=now + timedelta(minutes=5),
            entities=(entity,),
            content=payload,
            quality=quality,
            provenance=provenance,
            privacy_class=PrivacyClass.PUBLIC,
            stage=ObservationPromotionStage.RAW_OBSERVATION
        )

        self.assertEqual(obs.observation_id, "obs_001")
        self.assertEqual(obs.entities[0].normalized_value, 220000.0)
        self.assertEqual(obs.quality.confidence, 0.92)

        # Verify frozen immutability
        with self.assertRaises(AttributeError):
            obs.stage = ObservationPromotionStage.WORLD_STATE_MEMORY

    def test_visibility_vs_existence_separation(self):
        """Test invariant: NOT_CURRENTLY_VISIBLE does not mean NO_LONGER_EXISTS."""
        now = datetime.now(timezone.utc)
        entity_state = ObservedEntityState(
            entity_id="ent_resume_doc",
            visibility=EntityVisibility.NOT_CURRENTLY_VISIBLE,
            existence=EntityExistence.PERSISTENT,
            last_observed_at=now - timedelta(minutes=10)
        )
        self.assertEqual(entity_state.visibility, EntityVisibility.NOT_CURRENTLY_VISIBLE)
        self.assertEqual(entity_state.existence, EntityExistence.PERSISTENT)

    def test_context_candidate_set_separation(self):
        """Test ContextCandidateSet high separation vs ambiguity."""
        c1 = ContextCandidate("vscode_python_debug", "Traceback visible in editor", 0.92, ("ev_01",))
        c2 = ContextCandidate("terminal_output", "Terminal log output", 0.45, ("ev_02",))
        
        # High separation: (0.92 - 0.45) / 0.92 = 0.51 >= 0.30 -> Decisive
        cset = ContextCandidateSet(
            candidates=(c1, c2),
            separation_ratio=round((0.92 - 0.45) / 0.92, 2),
            selected_context="vscode_python_debug",
            is_ambiguous=False
        )
        self.assertFalse(cset.is_ambiguous)
        self.assertEqual(cset.selected_context, "vscode_python_debug")

    def test_perception_receipt_contract(self):
        """Test PerceptionReceipt audit trail fields."""
        receipt = PerceptionReceipt(
            receipt_id="rec_percept_01",
            session_id="sess_100",
            modality=Modality.SCREEN,
            root_source_id="snap_123",
            raw_retained=False,
            observations_created=("obs_01", "obs_02"),
            evidence_promoted=("ev_comp_01",),
            world_state_changes=("facts.target_role_updated",)
        )
        self.assertFalse(receipt.raw_retained)
        self.assertEqual(len(receipt.evidence_promoted), 1)


if __name__ == "__main__":
    unittest.main()
