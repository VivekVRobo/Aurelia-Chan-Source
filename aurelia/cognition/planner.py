"""Compile bounded cognitive execution DAGs for Aurelia."""

from __future__ import annotations

from dataclasses import dataclass, field

from aurelia.cognition.router import CognitiveBudget, CognitiveComplexityMode
from aurelia.contracts.meaning_frame import MeaningFrame
from aurelia.contracts.snapshot import CognitiveSnapshot


@dataclass(frozen=True)
class PlanNode:
    """One executable node in a cognitive DAG."""

    node_id: str
    capability_id: str
    dependencies: tuple[str, ...] = field(default_factory=tuple)
    is_deterministic: bool = True
    requires_llm: bool = False


@dataclass(frozen=True)
class CognitivePlan:
    """A compiled, dependency-explicit cognitive execution plan."""

    plan_id: str
    budget: CognitiveBudget
    nodes: tuple[PlanNode, ...]
    entry_node_id: str
    exit_node_id: str


class CognitivePlanner:
    """Compile the minimal execution graph allowed by the cognitive budget."""

    @classmethod
    def compile(
        cls,
        meaning: MeaningFrame,
        budget: CognitiveBudget,
        snapshot: CognitiveSnapshot | None = None,
    ) -> CognitivePlan:
        del snapshot  # Reserved for state-dependent planning extensions.
        mode = budget.mode

        if mode == CognitiveComplexityMode.REFLEX:
            mem_lookup = PlanNode(
                node_id="mem_lookup",
                capability_id="memory.lookup.fast",
            )
            response = PlanNode(
                node_id="resp_format",
                capability_id="response.format.direct",
                dependencies=("mem_lookup",),
            )
            verifier = PlanNode(
                node_id="verify_output",
                capability_id="verification.firewall.verify",
                dependencies=("resp_format",),
            )
            return CognitivePlan(
                plan_id=f"plan_reflex_{meaning.frame_id}",
                budget=budget,
                nodes=(mem_lookup, response, verifier),
                entry_node_id="mem_lookup",
                exit_node_id="resp_format",
            )

        if mode in {CognitiveComplexityMode.DEEP, CognitiveComplexityMode.VERIFIED}:
            parse_offer = PlanNode(
                node_id="parse_offer",
                capability_id="comp.parse.offer",
            )
            retrieve_history = PlanNode(
                node_id="retrieve_history",
                capability_id="memory.retrieve.hybrid",
            )
            comp_model = PlanNode(
                node_id="comp_model",
                capability_id="comp.calc.total_target",
                dependencies=("parse_offer",),
            )
            monte_carlo = PlanNode(
                node_id="monte_carlo",
                capability_id="sim.monte_carlo.equity",
                dependencies=("parse_offer", "comp_model"),
            )
            hypotheses = PlanNode(
                node_id="gen_hypotheses",
                capability_id="cognition.search.hypotheses",
                dependencies=("comp_model", "retrieve_history"),
            )
            critics = PlanNode(
                node_id="critics",
                capability_id="cognition.critics.evaluate",
                dependencies=("gen_hypotheses", "monte_carlo"),
            )
            renderer = PlanNode(
                node_id="renderer",
                capability_id="response.render.aurelia",
                dependencies=("critics", "comp_model", "retrieve_history"),
                is_deterministic=False,
                requires_llm=True,
            )
            firewall = PlanNode(
                node_id="firewall",
                capability_id="verification.firewall.verify",
                dependencies=("renderer", "comp_model"),
            )
            artifact = PlanNode(
                node_id="artifact_gen",
                capability_id="artifact.workspace.create",
                dependencies=("firewall", "critics"),
            )
            return CognitivePlan(
                plan_id=f"plan_deep_{meaning.frame_id}",
                budget=budget,
                nodes=(
                    parse_offer,
                    retrieve_history,
                    comp_model,
                    monte_carlo,
                    hypotheses,
                    critics,
                    renderer,
                    firewall,
                    artifact,
                ),
                entry_node_id="parse_offer",
                exit_node_id="renderer",
            )

        specialist = PlanNode(
            node_id="evaluate_specialist",
            capability_id="specialist.evaluate",
        )
        renderer = PlanNode(
            node_id="render_response",
            capability_id="response.render.aurelia",
            dependencies=("evaluate_specialist",),
            is_deterministic=False,
            requires_llm=True,
        )
        verifier = PlanNode(
            node_id="verify_output",
            capability_id="verification.firewall.verify",
            dependencies=("render_response",),
        )
        return CognitivePlan(
            plan_id=f"plan_std_{meaning.frame_id}",
            budget=budget,
            nodes=(specialist, renderer, verifier),
            entry_node_id="evaluate_specialist",
            exit_node_id="render_response",
        )
