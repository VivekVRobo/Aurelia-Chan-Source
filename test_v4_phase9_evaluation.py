"""
Aurelia Cognitive OS V4 - Phase 9 Evaluation & Calibration Test Suite
======================================================================
Tests Calibration Engine, Ablation Harness, No-LLM rates, and Decision Replay.
"""

import unittest
from aurelia.evaluation.calibration import CalibrationEngine, DecisionReplayer
from aurelia.evaluation.benchmarks import BenchmarkHarness
from aurelia.contracts.receipt import DecisionReceipt, InferenceRecord
from aurelia.contracts.core_types import VerificationSeverity


class TestPhase9Evaluation(unittest.TestCase):
    """Test suite for Phase 9 Evaluation and Calibration."""

    def test_calibration_engine_buckets(self):
        """Test confidence calibration evaluation."""
        predictions = [
            (0.85, True),
            (0.80, True),
            (0.75, True),
            (0.70, False),
            (0.60, True),
            (0.55, False)
        ]
        buckets = CalibrationEngine.evaluate_calibration(predictions)
        self.assertTrue(len(buckets) >= 2)
        # Check that calibration errors are computed
        for b in buckets:
            self.assertTrue(0.0 <= b.calibration_error <= 1.0)

    def test_no_llm_benchmark_calculation(self):
        """Test calculation of deterministic zero-LLM rate."""
        records = [
            {"request_id": "r1", "llm_calls_made": 0}, # Status inquiry
            {"request_id": "r2", "llm_calls_made": 0}, # Resume formula audit
            {"request_id": "r3", "llm_calls_made": 1}, # Chat response
            {"request_id": "r4", "llm_calls_made": 0}, # Last score lookup
        ]
        rate = BenchmarkHarness.calculate_no_llm_rate(records)
        self.assertEqual(rate, 75.0) # 3 out of 4 = 75%

    def test_ablation_comparison(self):
        """Test ablation impact evaluation."""
        baseline = 92.0
        ablated = {
            "minus_numerical_firewall": 64.0, # -28% accuracy drop
            "minus_career_graph": 72.0,       # -20% accuracy drop
            "minus_memory": 80.0             # -12% accuracy drop
        }
        impacts = BenchmarkHarness.run_ablation_comparison(baseline, ablated)
        self.assertEqual(impacts["minus_numerical_firewall"], 28.0)
        self.assertEqual(impacts["minus_career_graph"], 20.0)

    def test_decision_replayer_receipt_integrity(self):
        """Test decision receipt integrity verification."""
        inf = InferenceRecord("inf_1", "llama3.2", "reasoning", "s1", "v4", 0.0, 10, 10, 50.0, True)
        receipt = DecisionReceipt(
            decision_id="dec_42",
            snapshot_id="snap_1",
            request_text="Compare packages",
            intent_type="compensation_strategy",
            plan_dag_nodes=("n1", "n2"),
            capabilities_invoked=("comp.calc",),
            inferences_made=(inf,),
            hypotheses_considered=("h1",),
            selected_hypothesis_id="h1",
            critic_scores={"fit": 0.8},
            numerical_calculations_verified=("total_comp",),
            verification_passed=True,
            verification_severity=VerificationSeverity.INFO.value,
            conclusion_summary="Accept with counter",
            artifacts_generated_ids=("art_1",),
            confidence_score=0.85
        )
        self.assertTrue(DecisionReplayer.verify_receipt_integrity(receipt))


if __name__ == "__main__":
    unittest.main()
