"""Aurelia Cognitive OS V4 phase-10 integration tests."""

import unittest

from integrated_backend import app
from aurelia.runtime.cognitive_runtime import AureliaCognitiveRuntime, CognitiveCycleResponse
from aurelia.runtime.health import HealthSupervisor


class TestPhase10Integration(unittest.TestCase):
    """Test the wired cognitive runtime, health doctor, and Flask API."""

    def setUp(self):
        self.runtime = AureliaCognitiveRuntime()
        self.client = app.test_client()

    def test_full_cognitive_cycle_compensation_and_artifact(self):
        res: CognitiveCycleResponse = self.runtime.process_query(
            user_text=(
                "I received an offer for Director of Engineering. Base $220k, "
                "20% bonus, and $60k equity. How should I evaluate this?"
            ),
            user_role="Senior Engineering Manager",
            target_role="Director of Engineering",
        )

        self.assertIsNotNone(res.response_text)
        self.assertIn("$324,000", res.response_text)
        self.assertEqual(res.expression, "confident")
        self.assertTrue(res.verification_report.passed)
        self.assertGreaterEqual(len(res.artifacts), 1)
        self.assertEqual(res.artifacts[0].title, "Executive Counter-Offer Strategy & Script")
        self.assertEqual(res.trace.confidence_level, "High")
        self.assertIsNotNone(res.decision_receipt.decision_id)

    def test_health_supervisor_doctor(self):
        doctor_report = HealthSupervisor.run_doctor()
        self.assertIn(doctor_report["overall_status"], {"HEALTHY", "DEGRADED"})
        self.assertEqual(len(doctor_report["subsystems"]), 4)
        self.assertTrue(all("critical" in subsystem for subsystem in doctor_report["subsystems"]))

    def test_flask_api_cognitive_cycle_endpoint(self):
        response = self.client.post(
            "/api/cognitive-cycle",
            json={
                "message": "How do I negotiate my executive compensation package?",
                "user_role": "Senior EM",
                "target_role": "Director",
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("response", data)
        self.assertIn("trace", data)
        self.assertIn("verification", data)
        self.assertIn("artifacts", data)
        self.assertTrue(data["verification"]["passed"])

    def test_flask_api_health_doctor_endpoint(self):
        response = self.client.get("/api/health-doctor")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn(data["overall_status"], {"HEALTHY", "DEGRADED"})


if __name__ == "__main__":
    unittest.main()
