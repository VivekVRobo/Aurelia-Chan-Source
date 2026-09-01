"""Dependency-aware executor for compiled Aurelia cognitive plans."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from aurelia.cognition.planner import CognitivePlan, PlanNode
from aurelia.execution.capability import CapabilityPermission, CapabilityResult
from aurelia.execution.executor import TypedExecutor
from aurelia.execution.registry import CapabilityRegistry


class NodeExecutionStatus(Enum):
    """Outcome of one DAG node."""

    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class NodeExecutionRecord:
    """Observed execution data for one plan node."""

    node_id: str
    capability_id: str
    status: NodeExecutionStatus
    dependencies: tuple[str, ...]
    result: CapabilityResult | None = None
    reason: str | None = None


@dataclass(frozen=True)
class PlanExecutionResult:
    """Immutable result of executing a complete cognitive DAG."""

    plan_id: str
    success: bool
    records: tuple[NodeExecutionRecord, ...]
    outputs: dict[str, Any]

    @property
    def executed_capabilities(self) -> tuple[str, ...]:
        """Return capability IDs that genuinely completed."""
        return tuple(
            record.capability_id
            for record in self.records
            if record.status == NodeExecutionStatus.COMPLETED
        )

    @property
    def failed_nodes(self) -> tuple[str, ...]:
        """Return nodes that failed or were blocked."""
        return tuple(
            record.node_id
            for record in self.records
            if record.status != NodeExecutionStatus.COMPLETED
        )


class CognitiveDAGExecutor:
    """Execute planner nodes in dependency order with fail-closed blocking."""

    def __init__(self, registry: CapabilityRegistry) -> None:
        self._registry = registry
        self._executor = TypedExecutor(registry)

    def validate_plan(self, plan: CognitivePlan) -> None:
        """Reject malformed plans before any capability is invoked."""
        node_ids = [node.node_id for node in plan.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("Cognitive plan contains duplicate node IDs.")

        known_nodes = set(node_ids)
        for node in plan.nodes:
            unknown_dependencies = set(node.dependencies) - known_nodes
            if unknown_dependencies:
                missing = ", ".join(sorted(unknown_dependencies))
                raise ValueError(f"Node '{node.node_id}' references unknown dependencies: {missing}")
            if self._registry.get(node.capability_id) is None:
                raise ValueError(
                    f"Node '{node.node_id}' references unregistered capability "
                    f"'{node.capability_id}'."
                )

        if plan.entry_node_id not in known_nodes:
            raise ValueError(f"Unknown entry node '{plan.entry_node_id}'.")
        if plan.exit_node_id not in known_nodes:
            raise ValueError(f"Unknown exit node '{plan.exit_node_id}'.")

        self._assert_acyclic(plan)

    def execute(
        self,
        plan: CognitivePlan,
        *,
        context: Any,
        caller_permission: CapabilityPermission = CapabilityPermission.READ_ONLY,
    ) -> PlanExecutionResult:
        """Execute every plan node whose dependencies complete successfully."""
        self.validate_plan(plan)

        pending = {node.node_id: node for node in plan.nodes}
        records: list[NodeExecutionRecord] = []
        outputs: dict[str, Any] = {}
        statuses: dict[str, NodeExecutionStatus] = {}

        while pending:
            progressed = False
            for node_id in list(pending):
                node = pending[node_id]
                if not all(dependency in statuses for dependency in node.dependencies):
                    continue

                progressed = True
                del pending[node_id]

                failed_dependencies = tuple(
                    dependency
                    for dependency in node.dependencies
                    if statuses[dependency] != NodeExecutionStatus.COMPLETED
                )
                if failed_dependencies:
                    statuses[node_id] = NodeExecutionStatus.BLOCKED
                    records.append(
                        NodeExecutionRecord(
                            node_id=node.node_id,
                            capability_id=node.capability_id,
                            status=NodeExecutionStatus.BLOCKED,
                            dependencies=node.dependencies,
                            reason=(
                                "Blocked by failed dependencies: "
                                + ", ".join(failed_dependencies)
                            ),
                        )
                    )
                    continue

                dependency_outputs = {
                    dependency: outputs[dependency] for dependency in node.dependencies
                }
                result = self._executor.execute(
                    node.capability_id,
                    {
                        "context": context,
                        "dependencies": dependency_outputs,
                    },
                    caller_permission=caller_permission,
                )
                if result.success:
                    statuses[node_id] = NodeExecutionStatus.COMPLETED
                    outputs[node_id] = result.output_data
                    status = NodeExecutionStatus.COMPLETED
                    reason = None
                else:
                    statuses[node_id] = NodeExecutionStatus.FAILED
                    status = NodeExecutionStatus.FAILED
                    reason = result.error_message

                records.append(
                    NodeExecutionRecord(
                        node_id=node.node_id,
                        capability_id=node.capability_id,
                        status=status,
                        dependencies=node.dependencies,
                        result=result,
                        reason=reason,
                    )
                )

            if not progressed:
                raise RuntimeError("Cognitive DAG execution stalled despite prior validation.")

        success = all(
            record.status == NodeExecutionStatus.COMPLETED for record in records
        )
        return PlanExecutionResult(
            plan_id=plan.plan_id,
            success=success,
            records=tuple(records),
            outputs=outputs,
        )

    @staticmethod
    def _assert_acyclic(plan: CognitivePlan) -> None:
        nodes = {node.node_id: node for node in plan.nodes}
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: PlanNode) -> None:
            if node.node_id in visited:
                return
            if node.node_id in visiting:
                raise ValueError(f"Cognitive plan contains a cycle at '{node.node_id}'.")
            visiting.add(node.node_id)
            for dependency in node.dependencies:
                visit(nodes[dependency])
            visiting.remove(node.node_id)
            visited.add(node.node_id)

        for node in plan.nodes:
            visit(node)
