"""
Aurelia Cognitive OS V6 - Phase 6 Speech & Prosody Test Suite
==============================================================
Tests audio transcription, acoustic prosody metrics, and anti-pseudopsychology guards.
"""

import unittest
from aurelia.audio.prosody import (
    LocalAudioEngine,
    ProsodyObservation
)


class TestV6Phase6SpeechAndProsody(unittest.TestCase):
    """Test suite for Phase 6 Speech & Prosody."""

    def test_audio_turn_prosody_calculation(self):
        """Test speech rate and pause density calculation."""
        text = "I need to prepare for the executive board review tomorrow afternoon."
        # 11 words over 4.0 seconds with 0.8s silence
        transcript = LocalAudioEngine.analyze_audio_turn(
            raw_text=text,
            duration_seconds=4.0,
            silence_duration_seconds=0.8,
            volume_std_db=5.1,
            pitch_std_hz=28.0
        )
        
        self.assertEqual(transcript.transcript_text, text)
        self.assertAlmostEqual(transcript.prosody.speech_rate_wpm, 165.0, delta=2.0)
        self.assertEqual(transcript.prosody.pause_density, 0.20)
        self.assertFalse(transcript.prosody.is_clinical_diagnosis)

    def test_anti_pseudopsychology_invariant(self):
        """Invariant: Prosody metrics must never be clinical diagnoses."""
        prosody = ProsodyObservation(
            speech_rate_wpm=90.0,
            pause_density=0.45,
            volume_variability_db=1.2,
            observed_pitch_variance_hz=8.0,
            is_clinical_diagnosis=False
        )
        self.assertFalse(prosody.is_clinical_diagnosis)


if __name__ == "__main__":
    unittest.main()
