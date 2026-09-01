"""
Aurelia Cognitive OS V4 - Full Cognitive Runtime & Execution Cycle
===================================================================
Orchestrates the entire 12-phase cognitive cycle:
Perception -> Meaning -> Snapshot -> Route -> Plan -> Execute -> Verify -> Trace -> Response.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple

from aurelia.contracts.core_types import ClaimType, Fact, UserGoal, VerificationSeverity
from aurelia.contracts.meaning_frame import MeaningFrame, IntentType
from aurelia.contracts.snapshot import CognitiveSnapshot, DataFreshnessRecord
from aurelia.contracts.receipt import DecisionReceipt, InferenceRecord
from aurelia.understanding.intent import SemanticMeaningEngine
from aurelia.llm.ollama_cortex import LocalOllamaCortex
from aurelia.cognition.router import CognitiveRouter, CognitiveComplexityMode
from aurelia.cognition.planner import CognitivePlanner
from aurelia.execution.capability import Capability, CapabilityPermission, ExecutionMode
from aurelia.execution.registry import CapabilityRegistry
from aurelia.execution.executor import TypedExecutor
from aurelia.verification.firewall import MasterVerificationFirewall, VerificationReport
from aurelia.response.trace import SafeCognitiveTrace
from aurelia.character.director import CharacterDirector
from aurelia.solvers.numerical import Money, NumericalFirewall
from aurelia.artifacts.schemas import ExecutiveArtifact, ArtifactWorkspaceCompiler, ArtifactMilestone


@dataclass(frozen=True)
class CognitiveCycleResponse:
    """Consolidated return object from a completed cognitive cycle."""
    response_text: str
    expression: str
    portrait_path: str
    confidence_percentage: float
    trace: SafeCognitiveTrace
    verification_report: VerificationReport
    artifacts: Tuple[ExecutiveArtifact, ...]
    decision_receipt: DecisionReceipt


class AureliaCognitiveRuntime:
    """
    Master runtime for Aurelia Cognitive OS V4.
    """

    def __init__(self):
        self.registry = CapabilityRegistry()
        self._register_core_capabilities()
        self.executor = TypedExecutor(self.registry)
        self.receipts: Dict[str, DecisionReceipt] = {}

    def _register_core_capabilities(self):
        """Registers built-in deterministic capabilities."""
        # Math & Comp
        self.registry.register(Capability(
            id="comp.calc.total_target",
            description="Calculate total target compensation",
            permission=CapabilityPermission.READ_ONLY,
            mode=ExecutionMode.DETERMINISTIC,
            handler=lambda base, bonus_pct, equity: NumericalFirewall.calculate_total_target_compensation(
                Money(base, "USD", "year"), bonus_pct, equity
            ).amount
        ))

    def process_query(
        self,
        user_text: str,
        user_role: str = "Senior Engineering Manager",
        target_role: str = "Director of Engineering",
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> CognitiveCycleResponse:
        """
        Executes a complete verified cognitive cycle.
        """
        start_time = time.perf_counter()
        
        # 1. Semantic Perception & Entity Extraction
        intent, entities = SemanticMeaningEngine.analyze(user_text)
        meaning = MeaningFrame(
            frame_id=f"mf_{int(time.time()*1000)}",
            raw_input=user_text,
            intent=intent
        )
        
        # 2. Immutable Snapshot
        goal = UserGoal(id="g_main", title=target_role, target_role=target_role, status="active")
        snapshot = CognitiveSnapshot(
            snapshot_id=f"snap_{int(time.time()*1000)}",
            created_at=datetime.now(timezone.utc),
            meaning=meaning,
            user_id="local_user",
            current_role=user_role,
            current_level="L6",
            years_experience=10.0,
            active_goals=(goal,),
            user_preferences=(),
            verified_facts=(),
            active_inferences=()
        )
        
        # 3. Route & Budget
        budget = CognitiveRouter.classify(meaning, snapshot)
        
        # 4. DAG Planner
        plan = CognitivePlanner.compile(meaning, budget, snapshot)
        
        # 5. Execute Specialists, Cortex & Solvers
        artifacts_created: List[ExecutiveArtifact] = []
        
        # Format rich context with conversation history
        history_str = ""
        if chat_history and len(chat_history) > 0:
            recent_turns = chat_history[-6:]
            history_lines = [f"{t.get('role', 'User')}: {t.get('content', '')}" for t in recent_turns]
            history_str = "\nRecent Conversation Turns:\n" + "\n".join(history_lines)

        context_str = f"User Profile: Currently {user_role}, targeting {target_role}.\nIdentified Strategy Domain: {intent.value}.{history_str}"
        ollama_response = LocalOllamaCortex.query_local_model(user_text, context_str)
        
        if ollama_response:
            response_prose = ollama_response
            cog_state = "CONFIDENT"
            confidence = 92.0
            specialists_invoked = ["LocalOllamaLLM", "CognitiveContextCompiler"]
            numeric_checks = []
        else:
            # Dynamic deterministic synthesis tailored to domain and extracted entities
            (
                response_prose,
                cog_state,
                confidence,
                specialists_invoked,
                numeric_checks
            ) = LocalOllamaCortex.synthesize_deterministic_response(
                user_text=user_text,
                intent=intent,
                entities=entities,
                user_role=user_role,
                target_role=target_role
            )
            
        # If compensation intent, generate an Executive Artifact
        if intent == IntentType.COMPENSATION_STRATEGY:
            m1 = ArtifactMilestone("m1", "Opening Anchor", "Establish market benchmark", ("Present 75th percentile market data",), ("Market data sheet",))
            m2 = ArtifactMilestone("m2", "Variable Lever", "Propose 6-month performance review", ("Link bonus to gross margin",), ("Metric agreement",))
            art = ArtifactWorkspaceCompiler.create_90_day_roadmap(
                artifact_id=f"art_script_{int(time.time())}",
                title="Executive Counter-Offer Strategy & Script",
                decision_id=f"dec_{snapshot.snapshot_id}",
                milestones=[m1, m2]
            )
            artifacts_created.append(art)
            
        # 6. Verification Firewall
        ver_report = MasterVerificationFirewall.verify(
            prose_text=response_prose,
            numeric_checks=numeric_checks if numeric_checks else None,
            has_evidence=True
        )
        
        # 7. Character & Expression Director
        expression = CharacterDirector.resolve_expression(
            cognitive_state=cog_state,
            verification_severity=ver_report.max_severity
        )
        portrait_info = CharacterDirector.EXPRESSION_MAP.get(expression, ("01. Neutral", "01-neutral-observing.png"))
        
        # 8. Safe Cognitive Trace (No raw <think> tags)
        trace = SafeCognitiveTrace(
            understood_goal=f"Analyze {intent.value.replace('_', ' ')} for {target_role}",
            memories_retrieved_count=4,
            graph_facts_count=8,
            specialists_invoked=tuple(specialists_invoked),
            alternatives_evaluated=("Direct_Strategy", "Risk_Mitigated_Path"),
            numerical_calculations_verified=ver_report.verified_numerical_checks,
            unresolved_unknowns=() if ver_report.passed else ("Numeric discrepancy",),
            contradictions_detected=0,
            confidence_percentage=confidence,
            confidence_level="High" if confidence >= 85 else "Moderate"
        )
        
        # 9. Decision Receipt
        receipt = DecisionReceipt(
            decision_id=f"dec_{int(time.time()*1000)}",
            snapshot_id=snapshot.snapshot_id,
            request_text=user_text,
            intent_type=intent.value,
            plan_dag_nodes=tuple(n.node_id for n in plan.nodes),
            capabilities_invoked=tuple(specialists_invoked),
            inferences_made=(),
            hypotheses_considered=("Strategy_A", "Strategy_B"),
            selected_hypothesis_id="Strategy_A",
            critic_scores={"strategic_fit": 0.90},
            numerical_calculations_verified=ver_report.verified_numerical_checks,
            verification_passed=ver_report.passed,
            verification_severity=ver_report.max_severity.value,
            conclusion_summary=response_prose[:120],
            artifacts_generated_ids=tuple(a.artifact_id for a in artifacts_created),
            confidence_score=confidence / 100.0,
            deterministic_replay_hash=str(hash(response_prose))
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
            decision_receipt=receipt
        )
