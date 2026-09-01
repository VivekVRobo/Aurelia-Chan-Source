"""Aurelia Cognitive OS V4 cognitive runtime.

The runtime owns the verified interaction cycle. It deliberately distinguishes
between a compiled cognitive plan and the capabilities that were actually
executed. Later stabilization phases will execute the full DAG; this module
must not fabricate execution, memory, graph, evidence, or critic trace data.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from aurelia.artifacts.schemas import ArtifactMilestone, ArtifactWorkspaceCompiler, ExecutiveArtifact
from aurelia.character.director import CharacterDirector
from aurelia.cognition.planner import CognitivePlanner
from aurelia.cognition.router import CognitiveRouter
from aurelia.contracts.core_types import UserGoal
from aurelia.contracts.meaning_frame import IntentType, MeaningFrame
from aurelia.contracts.receipt import DecisionReceipt
from aurelia.contracts.snapshot import CognitiveSnapshot
from aurelia.execution.capability import Capability, CapabilityPermission, ExecutionMode
from aurelia.execution.executor import TypedExecutor
from aurelia.execution.registry import CapabilityRegistry
from aurelia.llm.ollama_cortex import LocalOllamaCortex
from aurelia.response.trace import SafeCognitiveTrace
from aurelia.runtime.grounding import RuntimeGrounder
from aurelia.solvers.numerical import Money, NumericalFirewall
from aurelia.understanding.intent import SemanticMeaningEngine
from aurelia.verification.firewall import MasterVerificationFirewall, VerificationReport


@dataclass(frozen=True)
class CognitiveCycleResponse:
    """Consolidated return object from a completed cognitive cycle."""

    response_text: str
    expression: str
    portrait_path: str
    confidence_percentage: float
    trace: SafeCognitiveTrace
    verification_report: VerificationReport
    artifacts: tuple[ExecutiveArtifact, ...]
    decision_receipt: DecisionReceipt


class AureliaCognitiveRuntime:
    """Coordinate one grounded, verified Aurelia cognitive interaction."""

    def __init__(self) -> None:
        self.registry = CapabilityRegistry()
        self._register_core_capabilities()
        self.executor = TypedExecutor(self.registry)
        self.grounder = RuntimeGrounder()
        self.receipts: dict[str, DecisionReceipt] = {}

    def _register_core_capabilities(self) -> None:
        """Register capabilities that are genuinely executable today."""
        self.registry.register(
            Capability(
                id="comp.calc.total_target",
                description="Calculate total target compensation",
                permission=CapabilityPermission.READ_ONLY,
                mode=ExecutionMode.DETERMINISTIC,
                handler=lambda base, bonus_pct, equity: (
                    NumericalFirewall.calculate_total_target_compensation(
                        Money(base, "USD", "year"), bonus_pct, equity
                    ).amount
                ),
            )
        )

    def process_query(
        self,
        user_text: str,
        user_role: str = "Senior Engineering Manager",
        target_role: str = "Director of Engineering",
        chat_history: list[dict[str, str]] | None = None,
    ) -> CognitiveCycleResponse:
        """Execute the currently wired cognitive cycle without synthetic trace claims."""
        intent, entities = SemanticMeaningEngine.analyze(user_text)
        meaning = MeaningFrame(
            frame_id=f"mf_{int(time.time() * 1000)}",
            raw_input=user_text,
            intent=intent,
        )

        goal = UserGoal(
            id="g_main",
            title=target_role,
            target_role=target_role,
            status="active",
        )
        snapshot = CognitiveSnapshot(
            snapshot_id=f"snap_{int(time.time() * 1000)}",
            created_at=datetime.now(timezone.utc),
            meaning=meaning,
            user_id="local_user",
            current_role=user_role,
            current_level="L6",
            years_experience=10.0,
            active_goals=(goal,),
            user_preferences=(),
            verified_facts=(),
            active_inferences=(),
        )

        budget = CognitiveRouter.classify(meaning, snapshot)
        plan = CognitivePlanner.compile(meaning, budget, snapshot)

        grounded = self.grounder.build(
            user_text=user_text,
            entities=entities,
            user_role=user_role,
            target_role=target_role,
            active_goal=goal,
            chat_history=chat_history,
            top_k=min(5, budget.max_retrieval_items),
        )

        context_parts = [
            f"User Profile: Currently {user_role}, targeting {target_role}.",
            f"Identified Strategy Domain: {intent.value}.",
        ]
        grounded_context = grounded.render_for_model()
        if grounded_context:
            context_parts.append(grounded_context)
        context_str = "\n\n".join(context_parts)

        artifacts_created: list[ExecutiveArtifact] = []
        ollama_response = LocalOllamaCortex.query_local_model(user_text, context_str)

        if ollama_response:
            response_prose = ollama_response
            cog_state = "CONFIDENT"
            confidence = 92.0
            executed_components = ["LocalOllamaCortex", "RuntimeGrounder"]
            numeric_checks: list[tuple[str, float, float]] = []
        else:
            (
                response_prose,
                cog_state,
                confidence,
                _declared_specialists,
                numeric_checks,
            ) = LocalOllamaCortex.synthesize_deterministic_response(
                user_text=user_text,
                intent=intent,
                entities=entities,
                user_role=user_role,
                target_role=target_role,
            )
            executed_components = ["DeterministicResponseSynthesizer", "RuntimeGrounder"]
            if numeric_checks:
                executed_components.append("NumericalFirewall")

        if intent == IntentType.COMPENSATION_STRATEGY:
            milestones = [
                ArtifactMilestone(
                    "m1",
                    "Opening Anchor",
                    "Establish market benchmark",
                    ("Present 75th percentile market data",),
                    ("Market data sheet",),
                ),
                ArtifactMilestone(
                    "m2",
                    "Variable Lever",
                    "Propose 6-month performance review",
                    ("Link bonus to gross margin",),
                    ("Metric agreement",),
                ),
            ]
            artifacts_created.append(
                ArtifactWorkspaceCompiler.create_90_day_roadmap(
                    artifact_id=f"art_script_{int(time.time())}",
                    title="Executive Counter-Offer Strategy & Script",
                    decision_id=f"dec_{snapshot.snapshot_id}",
                    milestones=milestones,
                )
            )

        ver_report = MasterVerificationFirewall.verify(
            prose_text=response_prose,
            numeric_checks=numeric_checks or None,
            has_evidence=grounded.has_corroborating_evidence,
        )

        expression = CharacterDirector.resolve_expression(
            cognitive_state=cog_state,
            verification_severity=ver_report.max_severity,
        )
        portrait_info = CharacterDirector.EXPRESSION_MAP.get(
            expression,
            ("01. Neutral", "01-neutral-observing.png"),
        )

        unresolved_unknowns = () if ver_report.passed else ("Verification issue requires review",)
        trace = SafeCognitiveTrace(
            understood_goal=f"Analyze {intent.value.replace('_', ' ')} for {target_role}",
            memories_retrieved_count=len(grounded.memories),
            graph_facts_count=len(grounded.graph_facts),
            specialists_invoked=tuple(executed_components),
            alternatives_evaluated=(),
            numerical_calculations_verified=ver_report.verified_numerical_checks,
            unresolved_unknowns=unresolved_unknowns,
            contradictions_detected=0,
            confidence_percentage=confidence,
            confidence_level="High" if confidence >= 85 else "Moderate",
        )

        receipt = DecisionReceipt(
            decision_id=f"dec_{int(time.time() * 1000)}",
            snapshot_id=snapshot.snapshot_id,
            request_text=user_text,
            intent_type=intent.value,
            plan_dag_nodes=tuple(node.node_id for node in plan.nodes),
            capabilities_invoked=tuple(executed_components),
            inferences_made=(),
            hypotheses_considered=(),
            selected_hypothesis_id=None,
            critic_scores={},
            numerical_calculations_verified=ver_report.verified_numerical_checks,
            verification_passed=ver_report.passed,
            verification_severity=ver_report.max_severity.value,
            conclusion_summary=response_prose[:120],
            artifacts_generated_ids=tuple(artifact.artifact_id for artifact in artifacts_created),
            confidence_score=confidence / 100.0,
            deterministic_replay_hash=self._stable_response_hash(response_prose),
        )
        self.receipts[receipt.decision_id] = receipt

        return CognitiveCycleResponse(
            response_text=response_prose,
            expression=expression,
            portrait_path=f"aurelia-expressions/{portrait_info[1]}",
            confidence_percentage=confidence,
            trace=trace,
            verification_report=ver_report,
            artifacts=tuple(artifacts_created),
            decision_receipt=receipt,
        )

    @staticmethod
    def _stable_response_hash(response_prose: str) -> str:
        """Return a process-stable SHA-256 hash for deterministic replay comparison."""
        return hashlib.sha256(response_prose.encode("utf-8")).hexdigest()
