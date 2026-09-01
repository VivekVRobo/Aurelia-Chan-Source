"""
Aurelia Cognitive OS V4 - Cognitive DAG Planner
================================================
Compiles structured task graphs (DAGs) representing the execution sequence,
data dependencies, and capability requirements for a cognitive cycle.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from aurelia.cognition.router import CognitiveBudget, CognitiveComplexityMode
from aurelia.contracts.meaning_frame import MeaningFrame, IntentType
from aurelia.contracts.snapshot import CognitiveSnapshot


@dataclass(frozen=True)
class PlanNode:
    """A node in the cognitive execution DAG."""
    node_id: str
    capability_id: str
    dependencies: Tuple[str, ...] = field(default_factory=tuple)
    is_deterministic: bool = True
    requires_llm: bool = False


@dataclass(frozen=True)
class CognitivePlan:
    """A compiled cognitive plan ready for the TypedExecutor."""
    plan_id: str
    budget: CognitiveBudget
    nodes: Tuple[PlanNode, ...]
    entry_node_id: str
    exit_node_id: str


class CognitivePlanner:
    """
    Compiles cognitive execution DAGs based on routing and snapshot state.
    """

    @classmethod
    def compile(
        cls,
        meaning: MeaningFrame,
        budget: CognitiveBudget,
        snapshot: Optional[CognitiveSnapshot] = None
    ) -> CognitivePlan:
        """
        Compiles the DAG nodes for the given complexity mode.
        """
        mode = budget.mode
        
        if mode == CognitiveComplexityMode.REFLEX:
            n1 = PlanNode(node_id="mem_lookup", capability_id="memory.lookup.fast", dependencies=(), is_deterministic=True)
            n2 = PlanNode(node_id="resp_format", capability_id="response.format.direct", dependencies=("mem_lookup",), is_deterministic=True)
            return CognitivePlan(
                plan_id=f"plan_reflex_{meaning.frame_id}",
                budget=budget,
                nodes=(n1, n2),
                entry_node_id="mem_lookup",
                exit_node_id="resp_format"
            )
            
        elif mode == CognitiveComplexityMode.DEEP or mode == CognitiveComplexityMode.VERIFIED:
            n1 = PlanNode(node_id="parse_offer", capability_id="comp.parse.offer", dependencies=(), is_deterministic=True)
            n2 = PlanNode(node_id="retrieve_history", capability_id="memory.retrieve.hybrid", dependencies=(), is_deterministic=True)
            n3 = PlanNode(node_id="comp_model", capability_id="comp.calc.total_target", dependencies=("parse_offer",), is_deterministic=True)
            n4 = PlanNode(node_id="monte_carlo", capability_id="sim.monte_carlo.equity", dependencies=("comp_model",), is_deterministic=True)
            n5 = PlanNode(node_id="gen_hypotheses", capability_id="cognition.search.hypotheses", dependencies=("comp_model", "retrieve_history"), is_deterministic=False, requires_llm=True)
            n6 = PlanNode(node_id="critics", capability_id="cognition.critics.evaluate", dependencies=("gen_hypotheses", "monte_carlo"), is_deterministic=False, requires_llm=True)
            n7 = PlanNode(node_id="firewall", capability_id="verification.firewall.verify", dependencies=("critics", "monte_carlo"), is_deterministic=True)
            n8 = PlanNode(node_id="artifact_gen", capability_id="artifact.workspace.create", dependencies=("firewall",), is_deterministic=True)
            n9 = PlanNode(node_id="renderer", capability_id="response.render.aurelia", dependencies=("firewall", "artifact_gen"), is_deterministic=False, requires_llm=True)
            
            return CognitivePlan(
                plan_id=f"plan_deep_{meaning.frame_id}",
                budget=budget,
                nodes=(n1, n2, n3, n4, n5, n6, n7, n8, n9),
                entry_node_id="parse_offer",
                exit_node_id="renderer"
            )
            
        else: # Standard Mode
            n1 = PlanNode(node_id="evaluate_specialist", capability_id="specialist.evaluate", dependencies=(), is_deterministic=True)
            n2 = PlanNode(node_id="verify_output", capability_id="verification.firewall.verify", dependencies=("evaluate_specialist",), is_deterministic=True)
            n3 = PlanNode(node_id="render_response", capability_id="response.render.aurelia", dependencies=("verify_output",), is_deterministic=False, requires_llm=True)
            
            return CognitivePlan(
                plan_id=f"plan_std_{meaning.frame_id}",
                budget=budget,
                nodes=(n1, n2, n3),
                entry_node_id="evaluate_specialist",
                exit_node_id="render_response"
            )
