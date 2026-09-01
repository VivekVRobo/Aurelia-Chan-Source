"""
Aurelia Cognitive OS V4 - Phase 0 Contract Invariant Tests
===========================================================
Strict automated verification that all core contracts, immutable snapshots,
cognitive primitives, and capability execution boundaries are uncompromised.
"""

import unittest
from datetime import datetime, timezone
from dataclasses import FrozenInstanceError

from aurelia.contracts.core_types import (
    ClaimType,
    EvidenceReliability,
    VerificationSeverity,
    EvidenceRef,
    ConfidenceScore,
    VerifiedValue,
    Fact,
    Observation,
    Inference,
    Hypothesis,
    Prediction,
    Recommendation,
    UserPreference,
    UserGoal,
)
from aurelia.contracts.meaning_frame import (
    IntentType,
    EntityRecord,
    TemporalConstraint,
    MeaningFrame,
)
from aurelia.contracts.snapshot import (
    DataFreshnessRecord,
    CognitiveSnapshot,
)
from aurelia.contracts.receipt import (
    InferenceRecord,
    DecisionReceipt,
)
from aurelia.execution.capability import (
    Capability,
    CapabilityResult,
    CapabilityPermission,
    ExecutionMode,
)
from aurelia.execution.registry import CapabilityRegistry
from aurelia.execution.executor import TypedExecutor


class TestPhase0Contracts(unittest.TestCase):
    """Test suite for Phase 0 Cognitive Invariants."""

    def test_invariant_1_facts_are_immutable(self):
        """Invariant: Facts cannot be modified once created."""
        evidence = EvidenceRef(
            id="ev_01",
            source_type="resume_doc",
            content_snippet="Led team of 12 engineers",
            reliability=EvidenceReliability.HISTORICAL_FACT
        )
        fact = Fact(
            id="fact_01",
            subject="user",
            predicate="manages_team_size",
            object_value=12,
            evidence=(evidence,)
        )
        
        self.assertEqual(fact.claim_type, ClaimType.FACT)
        self.assertEqual(fact.object_value, 12)
        
        # Verify immutability
        with self.assertRaises(FrozenInstanceError):
            fact.object_value = 20  # type: ignore

    def test_invariant_2_distinct_cognitive_primitive_classes(self):
        """Invariant: Fact, Inference, Prediction, and Recommendation have distinct types."""
        obs = Observation(
            id="obs_01",
            source="chat_input",
            raw_content="I completed the Q3 planning presentation."
        )
        inf = Inference(
            id="inf_01",
            claim="User demonstrates strategic planning experience",
            derived_from_ids=("obs_01",),
            confidence=ConfidenceScore(score=0.85, evidence_weight=0.8),
            reasoning_method="competency_evaluator"
        )
        pred = Prediction(
            id="pred_01",
            target_milestone="Director Interview Readiness",
            estimated_time_months=3.5,
            probability_range=(0.70, 0.85),
            critical_dependencies=("budget_ownership_evidence",)
        )
        rec = Recommendation(
            id="rec_01",
            action_statement="Seek direct budget accountability for Q4",
            rationale="Budget ownership is current remaining gap for Director role",
            expected_impact="Elevates readiness from 74% to 88%",
            prerequisites=("presentation_delivered",),
            priority_level=1
        )
        
        self.assertEqual(obs.claim_type, ClaimType.OBSERVATION)
        self.assertEqual(inf.claim_type, ClaimType.INFERENCE)
        self.assertEqual(pred.claim_type, ClaimType.PREDICTION)
        self.assertEqual(rec.claim_type, ClaimType.RECOMMENDATION)
        self.assertNotEqual(inf.claim_type, pred.claim_type)

    def test_invariant_3_confidence_score_bounds(self):
        """Invariant: Confidence scores must be strictly between 0.0 and 1.0."""
        valid_conf = ConfidenceScore(score=0.75, evidence_weight=0.7)
        self.assertEqual(valid_conf.score, 0.75)
        
        with self.assertRaises(ValueError):
            ConfidenceScore(score=1.2, evidence_weight=0.5)
            
        with self.assertRaises(ValueError):
            ConfidenceScore(score=-0.1, evidence_weight=0.5)

    def test_invariant_4_cognitive_snapshot_immutability(self):
        """Invariant: CognitiveSnapshot is frozen and cannot be mutated during cycle."""
        meaning = MeaningFrame(
            frame_id="mf_01",
            raw_input="Should I accept the startup offer?",
            intent=IntentType.DECISION_EVALUATION,
            complexity_level="deep"
        )
        goal = UserGoal(
            id="g_01",
            title="Director of Engineering",
            target_role="Director of Engineering"
        )
        pref = UserPreference(
            id="p_01",
            preference_key="location",
            value="remote_only",
            is_hard_constraint=True
        )
        
        snapshot = CognitiveSnapshot(
            snapshot_id="snap_101",
            created_at=datetime.now(timezone.utc),
            meaning=meaning,
            user_id="user_test_01",
            current_role="Senior Engineering Manager",
            current_level="L6",
            years_experience=11.5,
            active_goals=(goal,),
            user_preferences=(pref,),
            verified_facts=(),
            active_inferences=(),
            deterministic_seed=42
        )
        
        self.assertEqual(snapshot.snapshot_id, "snap_101")
        self.assertEqual(snapshot.current_role, "Senior Engineering Manager")
        
        with self.assertRaises(FrozenInstanceError):
            snapshot.current_role = "Director"  # type: ignore

    def test_invariant_5_capability_registry_and_executor(self):
        """Invariant: Capabilities are strictly typed, permissioned, and timed."""
        registry = CapabilityRegistry()
        
        def calculate_compensation_delta(base: float, bonus_pct: float) -> float:
            return base * (1.0 + (bonus_pct / 100.0))
        
        calc_cap = Capability(
            id="comp.calc.total_target",
            description="Computes total target compensation",
            permission=CapabilityPermission.READ_ONLY,
            mode=ExecutionMode.DETERMINISTIC,
            deterministic=True,
            handler=calculate_compensation_delta
        )
        
        registry.register(calc_cap)
        self.assertIsNotNone(registry.get("comp.calc.total_target"))
        
        # Test Duplicate Registration Prevention
        with self.assertRaises(ValueError):
            registry.register(calc_cap)
            
        executor = TypedExecutor(registry)
        
        # Test Successful Execution
        res = executor.execute(
            capability_id="comp.calc.total_target",
            input_args={"base": 200000.0, "bonus_pct": 20.0},
            caller_permission=CapabilityPermission.READ_ONLY
        )
        
        self.assertTrue(res.success)
        self.assertEqual(res.output_data, 240000.0)
        self.assertTrue(res.execution_time_ms >= 0.0)
        self.assertTrue(res.deterministic)
        
        # Test Missing Capability Isolation
        bad_res = executor.execute(
            capability_id="non_existent_capability",
            input_args={}
        )
        self.assertFalse(bad_res.success)
        self.assertIn("not found", bad_res.error_message)

    def test_invariant_6_permission_enforcement(self):
        """Invariant: Mutating state capabilities require explicit permission."""
        registry = CapabilityRegistry()
        
        def mutate_memory(key: str, val: str) -> bool:
            return True
            
        mutate_cap = Capability(
            id="memory.write.commit",
            description="Commits memory item to storage",
            permission=CapabilityPermission.MUTATE_LOCAL_STATE,
            mode=ExecutionMode.DETERMINISTIC,
            handler=mutate_memory
        )
        registry.register(mutate_cap)
        
        executor = TypedExecutor(registry)
        
        # Caller with READ_ONLY must be rejected
        unauth_res = executor.execute(
            capability_id="memory.write.commit",
            input_args={"key": "target_role", "val": "VP"},
            caller_permission=CapabilityPermission.READ_ONLY
        )
        self.assertFalse(unauth_res.success)
        self.assertIn("Permission denied", unauth_res.error_message)
        
        # Caller with MUTATE_LOCAL_STATE must succeed
        auth_res = executor.execute(
            capability_id="memory.write.commit",
            input_args={"key": "target_role", "val": "VP"},
            caller_permission=CapabilityPermission.MUTATE_LOCAL_STATE
        )
        self.assertTrue(auth_res.success)

    def test_invariant_7_decision_receipt_completeness(self):
        """Invariant: DecisionReceipt captures complete execution trace."""
        inf_rec = InferenceRecord(
            inference_id="inf_rec_01",
            model_name="deterministic_evaluator",
            cognitive_role="strategic_reasoning",
            snapshot_id="snap_101",
            prompt_template_version="v4.0",
            temperature=0.0,
            input_tokens_est=120,
            output_tokens_est=80,
            latency_ms=12.4,
            parse_success=True
        )
        
        receipt = DecisionReceipt(
            decision_id="dec_001",
            snapshot_id="snap_101",
            request_text="Should I accept the startup offer?",
            intent_type="decision_evaluation",
            plan_dag_nodes=("parse_offer", "compare_comp", "risk_model", "verifier"),
            capabilities_invoked=("comp.calc.total_target", "risk.evaluate"),
            inferences_made=(inf_rec,),
            hypotheses_considered=("startup_accept", "faang_remain", "negotiate_equity"),
            selected_hypothesis_id="negotiate_equity",
            critic_scores={"strategic_fit": 0.88, "risk_tolerance": 0.72},
            numerical_calculations_verified=("equity_monte_carlo_p50", "tax_bracket_normalizer"),
            verification_passed=True,
            verification_severity=VerificationSeverity.INFO.value,
            conclusion_summary="Negotiate 0.75% equity with accelerated vesting before accepting.",
            artifacts_generated_ids=("art_negotiation_script_v1",),
            confidence_score=0.82,
            deterministic_replay_hash="a1b2c3d4e5f6"
        )
        
        self.assertEqual(receipt.decision_id, "dec_001")
        self.assertEqual(receipt.selected_hypothesis_id, "negotiate_equity")
        self.assertTrue(receipt.verification_passed)
        self.assertEqual(len(receipt.capabilities_invoked), 2)


if __name__ == "__main__":
    unittest.main()
