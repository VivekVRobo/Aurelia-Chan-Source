"""Regression tests for the actuator-free Aurelia to RCI embodiment boundary."""

from __future__ import annotations

import json
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from aurelia.embodiment.adapter import (
    AureliaEmbodimentAdapter,
    EmbodimentContractError,
)
from aurelia.embodiment.contracts import (
    SCHEMA_VERSION,
    MotionCue,
    MotionDisposition,
    MotionStyle,
)
from aurelia.llm.ollama_cortex import LocalOllamaCortex
from aurelia.runtime.api_contract import serialize_cognitive_cycle
from aurelia.runtime.cognitive_runtime import AureliaCognitiveRuntime

FORBIDDEN_ACTUATOR_KEYS = {
    "actuator",
    "actuators",
    "angle",
    "angles",
    "duty_cycle",
    "joint",
    "joints",
    "motor",
    "motors",
    "pulse_width",
    "pwm",
    "servo",
    "servos",
    "target_position",
    "target_velocity",
    "trajectory",
}


class TestEmbodimentContract(unittest.TestCase):
    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_verified_cycle_adapts_to_semantic_character_response(self, _mock_llm) -> None:
        cycle = AureliaCognitiveRuntime().process_query(
            "I received an offer with base $220k, 20% bonus, and $60k equity."
        )
        response = AureliaEmbodimentAdapter.adapt(cycle)

        self.assertEqual(response.schema_version, SCHEMA_VERSION)
        self.assertEqual(response.decision_id, cycle.decision_receipt.decision_id)
        self.assertTrue(response.interaction_id.startswith("interaction_"))
        self.assertEqual(response.speech.text, cycle.response_text)
        self.assertEqual(response.expression.expression, cycle.persona.expression)
        self.assertEqual(response.motion.cue, MotionCue.PRESENT)
        self.assertEqual(response.motion.style, MotionStyle.RESTRAINED)
        self.assertEqual(response.motion.disposition, MotionDisposition.OPTIONAL)
        self.assertTrue(response.verified)
        self.assertTrue(response.persistence_committed)
        self.assertFalse(response.persistence_durable)

    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_canonical_api_contains_same_versioned_character_response(self, _mock_llm) -> None:
        cycle = AureliaCognitiveRuntime().process_query("Give me leadership guidance.")
        payload = serialize_cognitive_cycle(cycle)
        character = payload["character_response"]

        self.assertEqual(character["schema_version"], SCHEMA_VERSION)
        self.assertEqual(character["decision_id"], payload["decision_id"])
        self.assertEqual(character["speech"]["text"], payload["response"])
        self.assertEqual(character["expression"]["expression"], payload["expression"])
        self.assertIn(character["motion"]["disposition"], {"none", "optional"})

    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_unverified_cycle_cannot_cross_embodiment_boundary(self, _mock_llm) -> None:
        cycle = AureliaCognitiveRuntime().process_query("Give me leadership guidance.")
        unsafe_report = replace(
            cycle.verification_report,
            passed=False,
            is_safe_to_publish=False,
        )
        unsafe_cycle = replace(cycle, verification_report=unsafe_report)

        with self.assertRaisesRegex(EmbodimentContractError, "Unverified output"):
            AureliaEmbodimentAdapter.adapt(unsafe_cycle)

    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_uncommitted_cycle_cannot_cross_embodiment_boundary(self, _mock_llm) -> None:
        cycle = AureliaCognitiveRuntime().process_query("Give me leadership guidance.")
        uncommitted = replace(cycle.persistence, committed=False)
        unsafe_cycle = replace(cycle, persistence=uncommitted)

        with self.assertRaisesRegex(EmbodimentContractError, "Uncommitted output"):
            AureliaEmbodimentAdapter.adapt(unsafe_cycle)

    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_presentation_divergence_fails_closed(self, _mock_llm) -> None:
        cycle = AureliaCognitiveRuntime().process_query("Give me leadership guidance.")
        divergent = replace(cycle, expression="warning")

        with self.assertRaisesRegex(EmbodimentContractError, "expressions diverged"):
            AureliaEmbodimentAdapter.adapt(divergent)

    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_contract_contains_no_actuator_level_fields(self, _mock_llm) -> None:
        cycle = AureliaCognitiveRuntime().process_query("Give me leadership guidance.")
        payload = AureliaEmbodimentAdapter.adapt(cycle).to_dict()
        keys = _collect_keys(payload)

        self.assertTrue(FORBIDDEN_ACTUATOR_KEYS.isdisjoint(keys))
        self.assertEqual(
            {member.value for member in MotionDisposition},
            {"none", "optional"},
        )

    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_machine_schema_matches_runtime_envelope_and_forbids_extra_fields(
        self, _mock_llm
    ) -> None:
        cycle = AureliaCognitiveRuntime().process_query("Give me leadership guidance.")
        payload = AureliaEmbodimentAdapter.adapt(cycle).to_dict()
        schema = json.loads(
            Path("schemas/rci-character-response-v1.schema.json").read_text(encoding="utf-8")
        )

        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["properties"]), set(payload))
        self.assertEqual(schema["properties"]["schema_version"]["const"], SCHEMA_VERSION)
        self.assertTrue(FORBIDDEN_ACTUATOR_KEYS.isdisjoint(_collect_schema_property_names(schema)))


def _collect_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key))
            keys.update(_collect_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_collect_keys(child))
    return keys


def _collect_schema_property_names(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        properties = value.get("properties")
        if isinstance(properties, dict):
            keys.update(str(key) for key in properties)
        for child in value.values():
            keys.update(_collect_schema_property_names(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_collect_schema_property_names(child))
    return keys


if __name__ == "__main__":
    unittest.main()
