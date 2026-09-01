"""Aurelia Cognitive OS V4 executable, persistent, character-aware runtime."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from aurelia.artifacts.schemas import ExecutiveArtifact
from aurelia.character.affect_engine import AffectIntensity, Emotion
from aurelia.character.expression_policy import ExpressionStyle
from aurelia.character.persona_renderer import PersonaRenderedResponse, PersonaRenderer
from aurelia.cognition.planner import CognitivePlanner
from aurelia.cognition.router import CognitiveRouter
from aurelia.contracts.core_types import UserGoal
from aurelia.contracts.meaning_frame import MeaningFrame
from aurelia.contracts.receipt import DecisionReceipt
from aurelia.contracts.snapshot import CognitiveSnapshot
from aurelia.execution.dag_executor import CognitiveDAGExecutor
from aurelia.execution.executor import TypedExecutor
from aurelia.execution.registry import CapabilityRegistry
from aurelia.memory.write_policy import MemoryCandidate
from aurelia.persistence.database import CognitiveDatabase
from aurelia.response.trace import SafeCognitiveTrace
from aurelia.runtime.capability_catalog import RuntimeCapabilityCatalog, RuntimeExecutionContext
from aurelia.runtime.grounding import RuntimeGrounder
from aurelia.runtime.persistence import PersistenceCommitResult, RuntimePersistence
from aurelia.understanding.intent import SemanticMeaningEngine
from aurelia.verification.firewall import VerificationReport


class CognitiveExecutionError(RuntimeError):
    """The planned cognitive cycle could not complete safely."""


@dataclass(frozen=True)
class CharacterPresentation:
    """Typed character state attached to one verified user-visible response."""

    emotion: Emotion
    emotion_intensity: AffectIntensity
    expression_style: ExpressionStyle
    mode: str
    traits: tuple[str, ...]
    expression: str
    portrait_path: str


@dataclass(frozen=True)
class CognitiveCycleResponse:
    """Consolidated return object from a completed verified cognitive cycle."""

    response_text: str
    expression: str
    portrait_path: str
    persona: CharacterPresentation
    confidence_percentage: float
    trace: SafeCognitiveTrace
    verification_report: VerificationReport
    artifacts: tuple[ExecutiveArtifact, ...]
    decision_receipt: DecisionReceipt
    persistence: PersistenceCommitResult


class AureliaCognitiveRuntime:
    """Compile, execute, characterize, verify, persist, and record one interaction."""

    def __init__(
        self,
        *,
        database: CognitiveDatabase | None = None,
        db_path: str = ":memory:",
    ) -> None:
        self.registry = CapabilityRegistry()
        RuntimeCapabilityCatalog.register_all(self.registry)
        self.executor = TypedExecutor(self.registry)
        self.dag_executor = CognitiveDAGExecutor(self.registry)
        self.grounder = RuntimeGrounder()
        self.persona_renderer = PersonaRenderer()
        self.database = database or CognitiveDatabase(db_path)
        self.persistence = RuntimePersistence(self.database)
        self.receipts: dict[str, DecisionReceipt] = {}

    def process_query(
        self,
        user_text: str,
        user_role: str = "Senior Engineering Manager",
        target_role: str = "Director of Engineering",
        chat_history: list[dict[str, str]] | None = None,
        memory_candidates: tuple[MemoryCandidate, ...] = (),
    ) -> CognitiveCycleResponse:
        """Execute, characterize, verify, and atomically persist the cognitive DAG."""
        intent, entities = SemanticMeaningEngine.analyze(user_text)
        meaning = MeaningFrame(
            frame_id=f"mf_{uuid4().hex}",
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
            snapshot_id=f"snap_{uuid4().hex}",
            created_at=datetime.now(UTC),
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
            persistent_candidates=self.persistence.retrieval_candidates(),
            top_k=min(5, budget.max_retrieval_items),
        )
        runtime_context = RuntimeExecutionContext(
            user_text=user_text,
            user_role=user_role,
            target_role=target_role,
            intent=intent,
            entities=entities,
            snapshot=snapshot,
            active_goal=goal,
            budget=budget,
            grounded=grounded,
            persona_renderer=self.persona_renderer,
        )
        execution = self.dag_executor.execute(plan, context=runtime_context)
        if not execution.success:
            failed = ", ".join(execution.failed_nodes)
            raise CognitiveExecutionError(f"Cognitive DAG failed or blocked nodes: {failed}")

        rendered = execution.outputs[plan.exit_node_id]
        response_prose = str(rendered["response_text"])
        confidence = float(rendered.get("confidence", 0.0))
        cognitive_state = str(rendered.get("cognitive_state", "FOCUSED"))
        persona_rendered = rendered.get("persona")
        if not isinstance(persona_rendered, PersonaRenderedResponse):
            raise CognitiveExecutionError("User-visible DAG output bypassed Aurelia PersonaRenderer.")

        verification_key = "firewall" if "firewall" in execution.outputs else "verify_output"
        verification_report: VerificationReport = execution.outputs[verification_key]
        if not verification_report.is_safe_to_publish:
            raise CognitiveExecutionError("Verification firewall rejected the rendered response.")

        expression, portrait_path = PersonaRenderer.resolve_expression(
            emotion=persona_rendered.emotion,
            cognitive_state=cognitive_state,
            verification_severity=verification_report.max_severity,
        )
        presentation = CharacterPresentation(
            emotion=persona_rendered.emotion,
            emotion_intensity=persona_rendered.emotion_intensity,
            expression_style=persona_rendered.expression_style,
            mode=persona_rendered.mode,
            traits=tuple(persona_rendered.traits),
            expression=expression,
            portrait_path=portrait_path,
        )

        artifacts = tuple(execution.outputs.get("artifact_gen", ()))
        critics = execution.outputs.get("critics", {})
        evaluations = tuple(critics.get("evaluations", ()))
        selected = critics.get("selected")
        hypotheses = tuple(entry["hypothesis"] for entry in evaluations)
        critic_scores = {
            f"{entry['hypothesis'].id}:{critique.critic_role}": critique.score
            for entry in evaluations
            for critique in entry["critiques"]
        }

        unresolved_unknowns = tuple(
            issue.description
            for issue in verification_report.issues
            if issue.severity.value in {"ERROR", "BLOCKER"}
        )
        trace = SafeCognitiveTrace(
            understood_goal=f"Analyze {intent.value.replace('_', ' ')} for {target_role}",
            memories_retrieved_count=len(grounded.memories),
            graph_facts_count=len(grounded.graph_facts),
            specialists_invoked=execution.executed_capabilities,
            alternatives_evaluated=tuple(hypothesis.id for hypothesis in hypotheses),
            numerical_calculations_verified=verification_report.verified_numerical_checks,
            unresolved_unknowns=unresolved_unknowns,
            contradictions_detected=0,
            confidence_percentage=confidence,
            confidence_level="High" if confidence >= 85 else "Moderate",
        )

        receipt = DecisionReceipt(
            decision_id=f"dec_{uuid4().hex}",
            snapshot_id=snapshot.snapshot_id,
            request_text=user_text,
            intent_type=intent.value,
            plan_dag_nodes=tuple(node.node_id for node in plan.nodes),
            capabilities_invoked=execution.executed_capabilities,
            inferences_made=(),
            hypotheses_considered=tuple(hypothesis.id for hypothesis in hypotheses),
            selected_hypothesis_id=selected.id if selected is not None else None,
            critic_scores=critic_scores,
            numerical_calculations_verified=verification_report.verified_numerical_checks,
            verification_passed=verification_report.passed,
            verification_severity=verification_report.max_severity.value,
            conclusion_summary=response_prose[:120],
            artifacts_generated_ids=tuple(artifact.artifact_id for artifact in artifacts),
            confidence_score=confidence / 100.0,
            deterministic_replay_hash=self._stable_response_hash(response_prose),
        )
        persistence_result = self.persistence.commit_verified_cycle(
            receipt=receipt,
            artifacts=artifacts,
            memory_candidates=memory_candidates,
        )
        self.receipts[receipt.decision_id] = receipt

        return CognitiveCycleResponse(
            response_text=response_prose,
            expression=expression,
            portrait_path=portrait_path,
            persona=presentation,
            confidence_percentage=confidence,
            trace=trace,
            verification_report=verification_report,
            artifacts=artifacts,
            decision_receipt=receipt,
            persistence=persistence_result,
        )

    @staticmethod
    def _stable_response_hash(response_prose: str) -> str:
        """Return a process-stable SHA-256 hash for deterministic replay comparison."""
        return hashlib.sha256(response_prose.encode("utf-8")).hexdigest()
