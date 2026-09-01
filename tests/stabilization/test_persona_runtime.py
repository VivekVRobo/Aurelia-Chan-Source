"""Regression tests for live Aurelia persona integration."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from aurelia.character.affect_engine import Emotion
from aurelia.llm.ollama_cortex import LocalOllamaCortex
from aurelia.runtime.cognitive_runtime import AureliaCognitiveRuntime, CognitiveExecutionError


class TestPersonaRuntime(unittest.TestCase):
    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_compensation_cycle_exposes_confident_typed_persona(self, _mock_llm) -> None:
        result = AureliaCognitiveRuntime().process_query(
            "I received an offer with base $220k, 20% bonus, and $60k equity."
        )

        self.assertEqual(result.persona.emotion, Emotion.CONFIDENT)
        self.assertEqual(result.persona.expression, "confident")
        self.assertEqual(result.expression, result.persona.expression)
        self.assertEqual(result.portrait_path, result.persona.portrait_path)
        self.assertIn("I can give you a structured assessment.", result.response_text)
        self.assertTrue(result.persona.traits)
        self.assertTrue(result.verification_report.is_safe_to_publish)

    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_user_distress_overrides_confident_cognitive_delivery(self, _mock_llm) -> None:
        result = AureliaCognitiveRuntime().process_query(
            "I'm struggling with my promotion to Director of Engineering. What should I do?"
        )

        self.assertEqual(result.persona.emotion, Emotion.SUPPORTIVE)
        self.assertEqual(result.persona.expression, "empathetic")
        self.assertTrue(result.response_text.startswith("I understand this is challenging."))
        self.assertTrue(result.verification_report.is_safe_to_publish)

    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_reflex_memory_path_still_runs_through_persona(self, _mock_llm) -> None:
        result = AureliaCognitiveRuntime().process_query("What was my last score?")

        self.assertEqual(result.persona.expression, "focused")
        self.assertEqual(result.expression, "focused")
        self.assertIn("do not have a grounded stored value", result.response_text)
        self.assertIn("response.format.direct", result.decision_receipt.capabilities_invoked)
        self.assertTrue(result.verification_report.is_safe_to_publish)

    @patch.object(
        LocalOllamaCortex,
        "query_local_model",
        return_value="I guarantee this will work perfectly for you.",
    )
    def test_publish_blocking_persona_policy_prevents_persistence(self, _mock_llm) -> None:
        runtime = AureliaCognitiveRuntime()

        with self.assertRaisesRegex(CognitiveExecutionError, "Verification firewall rejected"):
            runtime.process_query("Give me leadership guidance.")

        self.assertEqual(runtime.database.count_rows("decision_receipts"), 0)
        self.assertEqual(runtime.database.count_rows("executive_artifacts"), 0)


if __name__ == "__main__":
    unittest.main()
