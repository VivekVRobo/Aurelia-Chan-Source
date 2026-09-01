"""
Aurelia Cognitive OS V4 - Phase 10 Integration Test Suite
==========================================================
Tests the full end-to-end Cognitive Runtime, Health Doctor, and Flask API.
"""

import unittest
from aurelia.runtime.cognitive_runtime import AureliaCognitiveRuntime, CognitiveCycleResponse
from aurelia.runtime.health import HealthSupervisor
from integrated_backend import app


class TestPhase10Integration(unittest.TestCase):
    """Test suite for Phase 10 Integration."""

    def setUp(self):
        self.runtime = AureliaCognitiveRuntime()
        self.client = app.test_client()

    def test_full_cognitive_cycle_compensation_and_artifact(self):
        """Test complete 12-phase cognitive cycle with math and artifact."""
        res: CognitiveCycleResponse = self.runtime.process_query(
            user_text="I received an offer for Director of Engineering. Base $220k, 20% bonus, and $60k equity. How should I evaluate this?",
            user_role="Senior Engineering Manager",
            target_role="Director of Engineering"
        )
        
        self.assertIsNotNone(res.response_text)
        self.assertIn("$324,000", res.response_text) # Verified total comp
        self.assertEqual(res.expression, "confident")
        self.assertTrue(res.verification_report.passed)
        self.assertTrue(len(res.artifacts) >= 1)
        self.assertEqual(res.artifacts[0].title, "Executive Counter-Offer Strategy & Script")
        self.assertEqual(res.trace.confidence_level, "High")
        self.assertIsNotNone(res.decision_receipt.decision_id)

    def test_health_supervisor_doctor(self):
        """Test health supervisor diagnostics."""
        doctor_report = HealthSupervisor.run_doctor()
        self.assertEqual(doctor_report["overall_status"], "HEALTHY")
        self.assertEqual(len(doctor_report["subsystems"]), 4)

    def test_flask_api_cognitive_cycle_endpoint(self):
        """Test Flask /api/cognitive-cycle endpoint."""
        response = self.client.post('/api/cognitive-cycle', json={
            'message': 'How do I negotiate my executive compensation package?',
            'user_role': 'Senior EM',
            'target_role': 'Director'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('response', data)
        self.assertIn('trace', data)
        self.assertIn('verification', data)
        self.assertIn('artifacts', data)
        self.assertTrue(data['verification']['passed'])

    def test_flask_api_health_doctor_endpoint(self):
        """Test Flask /api/health-doctor endpoint."""
        response = self.client.get('/api/health-doctor')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['overall_status'], 'HEALTHY')


if __name__ == "__main__":
    unittest.main()
