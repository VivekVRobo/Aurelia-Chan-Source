"""Regression tests for executable cognitive DAG orchestration."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from aurelia.cognition.planner import CognitivePlan, PlanNode
from aurelia.cognition.router import CognitiveBudget, CognitiveComplexityMode
from aurelia.execution.capability import Capability, CapabilityPermission, ExecutionMode
from aurelia.execution.dag_executor import CognitiveDAGExecutor, NodeExecutionStatus
from aurelia.execution.registry import CapabilityRegistry
from aurelia.llm.ollama_cortex import LocalOllamaCortex
from aurelia.runtime.cognitive_runtime import AureliaCognitiveRuntime


class TestDAGExecution(unittest.TestCase):
    def test_runtime_registers_every_planner_capability(self) -> None:
        runtime = AureliaCognitiveRuntime()
        registered = {capability.id for capability in runtime.registry.list_all()}
        expected = {
            "memory.lookup.fast",
            "response.format.direct",
            "comp.parse.offer",
            "memory.retrieve.hybrid",
            "comp.calc.total_target",
            "sim.monte_carlo.equity",
            "cognition.search.hypotheses",
            "cognition.critics.evaluate",
            "specialist.evaluate",
            "response.render.aurelia",
            "verification.firewall.verify",
            "artifact.workspace.create",
        }
        self.assertEqual(registered, expected)

    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_deep_compensation_cycle_executes_real_plan(self, _mock_llm) -> None:
        runtime = AureliaCognitiveRuntime()
        result = runtime.process_query(
            "I received a Director offer with base $220k, 20% bonus, and $60k equity."
        )

        self.assertIn("$324,000", result.response_text)
        self.assertTrue(result.verification_report.is_safe_to_publish)
        self.assertEqual(len(result.artifacts), 1)
        self.assertEqual(
            result.decision_receipt.capabilities_invoked,
            (
                "comp.parse.offer",
                "memory.retrieve.hybrid",
                "comp.calc.total_target",
                "sim.monte_carlo.equity",
                "cognition.search.hypotheses",
                "cognition.critics.evaluate",
                "response.render.aurelia",
                "verification.firewall.verify",
                "artifact.workspace.create",
            ),
        )
        self.assertTrue(result.decision_receipt.hypotheses_considered)
        self.assertIsNotNone(result.decision_receipt.selected_hypothesis_id)
        self.assertTrue(result.decision_receipt.critic_scores)

    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_standard_cycle_executes_specialist_render_verify(self, _mock_llm) -> None:
        result = AureliaCognitiveRuntime().process_query("Give me leadership guidance.")
        self.assertEqual(
            result.decision_receipt.capabilities_invoked,
            (
                "specialist.evaluate",
                "response.render.aurelia",
                "verification.firewall.verify",
            ),
        )
        self.assertTrue(result.verification_report.is_safe_to_publish)

    @patch.object(LocalOllamaCortex, "query_local_model", return_value=None)
    def test_reflex_cycle_is_verified_and_grounded(self, _mock_llm) -> None:
        result = AureliaCognitiveRuntime().process_query("What was my last score?")
        self.assertEqual(
            result.decision_receipt.capabilities_invoked,
            (
                "memory.lookup.fast",
                "response.format.direct",
                "verification.firewall.verify",
            ),
        )
        self.assertIn("do not have a grounded stored value", result.response_text)

    def test_failed_dependency_blocks_downstream_node(self) -> None:
        registry = CapabilityRegistry()

        def fail(*, context, dependencies):
            del context, dependencies
            raise RuntimeError("expected failure")

        def should_not_run(*, context, dependencies):
            del context, dependencies
            raise AssertionError("blocked node executed")

        registry.register(
            Capability(
                id="test.fail",
                description="failure",
                permission=CapabilityPermission.READ_ONLY,
                mode=ExecutionMode.DETERMINISTIC,
                handler=fail,
            )
        )
        registry.register(
            Capability(
                id="test.downstream",
                description="downstream",
                permission=CapabilityPermission.READ_ONLY,
                mode=ExecutionMode.DETERMINISTIC,
                handler=should_not_run,
            )
        )
        plan = CognitivePlan(
            plan_id="test_plan",
            budget=CognitiveBudget(mode=CognitiveComplexityMode.STANDARD),
            nodes=(
                PlanNode("first", "test.fail"),
                PlanNode("second", "test.downstream", dependencies=("first",)),
            ),
            entry_node_id="first",
            exit_node_id="second",
        )
        execution = CognitiveDAGExecutor(registry).execute(plan, context=object())
        self.assertFalse(execution.success)
        self.assertEqual(execution.records[0].status, NodeExecutionStatus.FAILED)
        self.assertEqual(execution.records[1].status, NodeExecutionStatus.BLOCKED)

    def test_unregistered_capability_is_rejected_before_execution(self) -> None:
        plan = CognitivePlan(
            plan_id="invalid",
            budget=CognitiveBudget(mode=CognitiveComplexityMode.STANDARD),
            nodes=(PlanNode("missing", "does.not.exist"),),
            entry_node_id="missing",
            exit_node_id="missing",
        )
        with self.assertRaisesRegex(ValueError, "unregistered capability"):
            CognitiveDAGExecutor(CapabilityRegistry()).validate_plan(plan)


if __name__ == "__main__":
    unittest.main()
