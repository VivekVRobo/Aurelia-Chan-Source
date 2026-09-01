"""Regression tests for Aurelia's canonical durable Flask integration boundary."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from aurelia.llm.ollama_cortex import LocalOllamaCortex
from aurelia.runtime.app_bootstrap import configure_integrated_backend
from aurelia.runtime.cognitive_runtime import CognitiveExecutionError


class TestIntegrationHardening(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tempdir.name) / "aurelia-integration.db"
        self.env = patch.dict(os.environ, {"AURELIA_DB_PATH": str(self.db_path)})
        self.env.start()
        self.app, self.runtime = configure_integrated_backend()
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        database = getattr(self.runtime, "database", None)
        if database is not None:
            try:
                database.close()
            except Exception:
                pass
        self.env.stop()
        self.tempdir.cleanup()

    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_cognitive_api_exposes_persona_and_durable_persistence(self, _mock_llm) -> None:
        response = self.client.post(
            "/api/cognitive-cycle",
            json={
                "message": "I received an offer with base $220k, 20% bonus, and $60k equity.",
                "user_role": "Senior Engineering Manager",
                "target_role": "Director of Engineering",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["expression"], data["persona"]["expression"])
        self.assertEqual(data["portrait"], data["persona"]["portrait"])
        self.assertEqual(data["persona"]["emotion"], "confident")
        self.assertTrue(data["persona"]["traits"])
        self.assertTrue(data["verification"]["safe_to_publish"])
        self.assertTrue(data["persistence"]["committed"])
        self.assertTrue(data["persistence"]["durable"])
        self.assertTrue(data["decision_id"])

    def test_runtime_status_reports_durable_character_aware_server(self) -> None:
        response = self.client.get("/api/runtime-status")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["runtime_configured"])
        self.assertTrue(data["persona_renderer"])
        self.assertTrue(data["persistence"]["durable"])
        self.assertEqual(data["registered_capabilities"], 12)
        self.assertNotIn("db_path", str(data))

    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_file_backed_decision_survives_canonical_runtime_restart(self, _mock_llm) -> None:
        response = self.client.post(
            "/api/cognitive-cycle",
            json={"message": "Give me general career guidance."},
        )
        self.assertEqual(response.status_code, 200)
        decision_id = response.get_json()["decision_id"]

        _app, restarted = configure_integrated_backend()
        self.runtime = restarted
        stored = restarted.database.get_decision_receipt(decision_id)

        self.assertIsNotNone(stored)
        self.assertEqual(stored["decision_id"], decision_id)

    def test_missing_runtime_fails_closed_instead_of_using_legacy_chat(self) -> None:
        import integrated_backend as backend

        previous = backend.v4_runtime
        backend.v4_runtime = None
        try:
            response = self.client.post(
                "/api/cognitive-cycle",
                json={"message": "Give me guidance."},
            )
        finally:
            backend.v4_runtime = previous

        self.assertEqual(response.status_code, 503)
        data = response.get_json()
        self.assertFalse(data["safe_to_publish"])
        self.assertIn("unavailable", data["error"].lower())
        self.assertNotIn("response", data)

    def test_cognitive_failure_returns_non_publishable_error_and_writes_nothing(self) -> None:
        before = self.runtime.database.count_rows("decision_receipts")
        with patch.object(
            self.runtime,
            "process_query",
            side_effect=CognitiveExecutionError("verification blocked output"),
        ):
            response = self.client.post(
                "/api/cognitive-cycle",
                json={"message": "Give me a guaranteed outcome."},
            )

        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertFalse(data["safe_to_publish"])
        self.assertEqual(data["error_type"], "CognitiveExecutionError")
        self.assertNotIn("response", data)
        self.assertEqual(self.runtime.database.count_rows("decision_receipts"), before)


if __name__ == "__main__":
    unittest.main()
