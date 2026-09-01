"""Regression tests for truthful Aurelia runtime stabilization."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from aurelia.llm.ollama_cortex import LocalOllamaCortex
from aurelia.runtime.cognitive_runtime import AureliaCognitiveRuntime
from aurelia.runtime.health import HealthSupervisor


class TestRuntimeStabilization(unittest.TestCase):
    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_trace_reports_actual_retrieval_and_no_fake_hypotheses(self, _mock_llm) -> None:
        runtime = AureliaCognitiveRuntime()
        result = runtime.process_query(
            user_text="How should I prepare for a Director of Engineering promotion?",
            user_role="Senior Engineering Manager",
            target_role="Director of Engineering",
            chat_history=[
                {"role": "user", "content": "I currently lead an engineering team."},
                {"role": "assistant", "content": "We should quantify your leadership scope."},
                {
                    "role": "user",
                    "content": "How should I prepare for a Director of Engineering promotion?",
                },
            ],
        )

        self.assertGreater(result.trace.memories_retrieved_count, 0)
        self.assertGreater(result.trace.graph_facts_count, 0)
        self.assertEqual(result.trace.alternatives_evaluated, ())
        self.assertEqual(result.decision_receipt.hypotheses_considered, ())
        self.assertIsNone(result.decision_receipt.selected_hypothesis_id)
        self.assertEqual(result.decision_receipt.critic_scores, {})
        self.assertEqual(
            result.decision_receipt.capabilities_invoked,
            (
                "specialist.evaluate",
                "response.render.aurelia",
                "verification.firewall.verify",
            ),
        )
        self.assertEqual(
            result.trace.specialists_invoked,
            result.decision_receipt.capabilities_invoked,
        )

    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_empty_history_and_unknown_roles_do_not_fabricate_counts(self, _mock_llm) -> None:
        runtime = AureliaCognitiveRuntime()
        result = runtime.process_query(
            user_text="Give me general guidance.",
            user_role="Unknown Role A",
            target_role="Unknown Role B",
            chat_history=[],
        )

        self.assertEqual(result.trace.memories_retrieved_count, 0)
        self.assertEqual(result.trace.graph_facts_count, 0)

    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_response_replay_hash_is_process_stable(self, _mock_llm) -> None:
        first = AureliaCognitiveRuntime().process_query("hello")
        second = AureliaCognitiveRuntime().process_query("hello")
        self.assertEqual(
            first.decision_receipt.deterministic_replay_hash,
            second.decision_receipt.deterministic_replay_hash,
        )
        self.assertEqual(len(first.decision_receipt.deterministic_replay_hash), 64)

    @patch.object(LocalOllamaCortex, "is_ollama_online", return_value=False)
    def test_health_reports_offline_optional_llm_as_degraded(self, _mock_online) -> None:
        report = HealthSupervisor.run_doctor()
        self.assertEqual(report["overall_status"], "DEGRADED")
        ollama = next(
            subsystem
            for subsystem in report["subsystems"]
            if subsystem["name"] == "Local Ollama Cortex"
        )
        self.assertEqual(ollama["status"], "DEGRADED")
        self.assertFalse(ollama["critical"])
        self.assertTrue(ollama["details"]["deterministic_fallback_available"])


if __name__ == "__main__":
    unittest.main()
