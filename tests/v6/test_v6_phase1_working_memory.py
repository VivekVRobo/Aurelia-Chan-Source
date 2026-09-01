"""
Aurelia Cognitive OS V6 - Phase 1 Working Memory & Deduplication Test Suite
============================================================================
Tests TTL purging, visibility state transitions, deduplication, and session gating.
"""

import unittest
from datetime import datetime, timezone, timedelta
from aurelia.grounding.working_memory import PerceptualWorkingMemory
from aurelia.grounding.deduplicator import ObservationSessionManager, ObservationDeduplicator
from aurelia.contracts.v6_contracts import (
    Modality,
    ObservationSource,
    PrivacyClass,
    ObservationPromotionStage,
    SessionMode,
    EntityVisibility,
    EntityExistence,
    Provenance,
    ObservationQuality,
    ObservedEntity,
    ObservationPayload,
    Observation
)


class TestV6Phase1WorkingMemory(unittest.TestCase):
    """Test suite for Phase 1 Working Memory & Deduplication."""

    def test_ephemeral_ttl_and_entity_visibility_transition(self):
        """Test observation expiry purges record but marks entity NOT_CURRENTLY_VISIBLE."""
        pwm = PerceptualWorkingMemory()
        now = datetime.now(timezone.utc)
        
        entity = ObservedEntity("ent_dialog", "ACTIVE_DIALOG", "Confirm Save?", "CONFIRM_SAVE")
        obs = Observation(
            observation_id="obs_dlg_01",
            session_id="sess_1",
            modality=Modality.SCREEN,
            source=ObservationSource.ACCESSIBILITY_TREE,
            observed_at=now - timedelta(seconds=25),
            expires_at=now - timedelta(seconds=5), # Expired 5 seconds ago
            entities=(entity,),
            content=ObservationPayload({}, "Save dialog open"),
            quality=ObservationQuality(0.9, 0.9, 0.0, 0.9, 1.0),
            provenance=Provenance("screen_01", ObservationSource.ACCESSIBILITY_TREE),
            privacy_class=PrivacyClass.PUBLIC
        )
        pwm.add_observation(obs)
        self.assertEqual(pwm.entity_states["ent_dialog"].visibility, EntityVisibility.CURRENTLY_VISIBLE)
        
        expired = pwm.sweep_expired(current_time=now)
        self.assertIn("obs_dlg_01", expired)
        self.assertIsNone(pwm.get_observation("obs_dlg_01"))
        
        # Entity state must be NOT_CURRENTLY_VISIBLE but still PERSISTENT
        ent_state = pwm.entity_states["ent_dialog"]
        self.assertEqual(ent_state.visibility, EntityVisibility.NOT_CURRENTLY_VISIBLE)
        self.assertEqual(ent_state.existence, EntityExistence.PERSISTENT)

    def test_observation_deduplicator(self):
        """Test duplicate filtering within sliding time window."""
        dedup = ObservationDeduplicator(window_seconds=60.0)
        now = datetime.now(timezone.utc)
        
        # Observation 1: Allowed
        first = dedup.should_record("screen_ocr", "SALARY_OFFER", 240000.0, now)
        self.assertTrue(first)
        
        # Observation 2 at +15s (identical): Blocked
        dup = dedup.should_record("screen_ocr", "SALARY_OFFER", 240000.0, now + timedelta(seconds=15))
        self.assertFalse(dup)
        
        # Observation 3 at +75s (after 60s window): Allowed
        later = dedup.should_record("screen_ocr", "SALARY_OFFER", 240000.0, now + timedelta(seconds=75))
        self.assertTrue(later)

    def test_session_manager_modality_gating(self):
        """Test session start/end and modality gating."""
        sm = ObservationSessionManager()
        
        # No session active -> modality disallowed
        self.assertFalse(sm.is_modality_allowed(Modality.SCREEN))
        
        # Start PUSH_TO_TALK session with only AUDIO allowed
        sm.start_session("sess_audio", SessionMode.PUSH_TO_TALK, {Modality.AUDIO})
        self.assertTrue(sm.is_modality_allowed(Modality.AUDIO))
        self.assertFalse(sm.is_modality_allowed(Modality.SCREEN))
        
        # End session
        sm.end_session()
        self.assertFalse(sm.is_modality_allowed(Modality.AUDIO))


if __name__ == "__main__":
    unittest.main()
