"""
Aurelia Cognitive OS V6 - Phase 13 Transactional Promotion Test Suite
======================================================================
Tests atomic promotion lifecycle, rollback on verification failure, and receipts.
"""

import unittest
from datetime import datetime, timezone
from aurelia.grounding.transactional_promotion import TransactionalObservationPromoter
from aurelia.contracts.v6_contracts import (
    Observation,
    ObservationPromotionStage,
    Modality,
    ObservationSource,
    PrivacyClass,
    Provenance,
    ObservationQuality,
    ObservedEntity,
    ObservationPayload
)


class TestV6Phase13TransactionalReceipts(unittest.TestCase):
    """Test suite for Phase 13 Transactional Promotion & Receipts."""

    def _create_sample_obs(self) -> Observation:
        now = datetime.now(timezone.utc)
        return Observation(
            observation_id="obs_test_99",
            session_id="sess_v6",
            modality=Modality.DOCUMENT,
            source=ObservationSource.STRUCTURED_DOCUMENT,
            observed_at=now,
            expires_at=None,
            entities=(ObservedEntity("ent_role", "TARGET_ROLE", "Director", "Director"),),
            content=ObservationPayload({}, "Director role detected"),
            quality=ObservationQuality(0.95, 0.95, 0.0, 0.95, 1.0),
            provenance=Provenance("doc_jd_01", ObservationSource.STRUCTURED_DOCUMENT),
            privacy_class=PrivacyClass.PUBLIC
        )

    def test_successful_transaction_and_receipt(self):
        """Test successful promotion commits fact and emits PerceptionReceipt."""
        promoter = TransactionalObservationPromoter()
        obs = self._create_sample_obs()
        
        res = promoter.execute_promotion_transaction(
            observation=obs,
            fact_key="target_role",
            fact_value="Director of Engineering",
            verification_passed=True
        )
        
        self.assertTrue(res.success)
        self.assertEqual(res.final_stage, ObservationPromotionStage.WORLD_STATE_MEMORY)
        self.assertIsNotNone(res.receipt)
        self.assertEqual(promoter.world_state_facts["target_role"], "Director of Engineering")
        self.assertEqual(len(promoter.committed_receipts), 1)

    def test_failed_verification_rollback(self):
        """Test verification failure triggers complete rollback."""
        promoter = TransactionalObservationPromoter()
        promoter.world_state_facts["existing_verified_fact"] = "UNCHANGED"
        obs = self._create_sample_obs()
        
        res = promoter.execute_promotion_transaction(
            observation=obs,
            fact_key="target_role",
            fact_value="Contradictory Role",
            verification_passed=False # Fails verification!
        )
        
        self.assertFalse(res.success)
        self.assertIsNone(res.receipt)
        self.assertIn("Verification failure", res.rollback_reason)
        # World state must NOT contain unverified fact
        self.assertNotIn("target_role", promoter.world_state_facts)
        self.assertEqual(promoter.world_state_facts["existing_verified_fact"], "UNCHANGED")


if __name__ == "__main__":
    unittest.main()
