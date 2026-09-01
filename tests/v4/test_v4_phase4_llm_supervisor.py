"""
Aurelia Cognitive OS V4 - Phase 4 LLM Supervisor Test Suite
============================================================
Tests Schema-bound model outputs, Hardware awareness, and Ollama Supervisor.
"""

import unittest
from aurelia.llm.schemas import HypothesisProposal, ReasoningResult, CritiqueResult
from aurelia.llm.hardware import HardwareProfile
from aurelia.llm.supervisor import OllamaSupervisor, SupervisorState


class TestPhase4LLMSupervisor(unittest.TestCase):
    """Test suite for Phase 4 LLM Supervisor and Schemas."""

    def test_schema_bound_reasoning_result(self):
        """Test structured output validation."""
        hyp = HypothesisProposal(
            id="hyp_01",
            strategy_type="aggressive_counter_offer",
            headline="Counter with 75th percentile market data",
            assumptions=("Company has budget flexibility",),
            proposed_actions=("Present compensation dossier", "Request 6-month performance review"),
            expected_upside="+$25k base and accelerated vesting",
            expected_downside="Offer rescinded if framed entitled",
            time_to_value_months=6.0,
            confidence=0.82
        )
        
        result = ReasoningResult(
            interpretation="User negotiating senior package with leverage.",
            hypotheses=(hyp,),
            identified_assumptions=("Flexibility exists",),
            uncertainties=("Company burn rate",),
            recommended_hypothesis_id="hyp_01",
            confidence=0.82
        )
        
        self.assertEqual(result.recommended_hypothesis_id, "hyp_01")
        self.assertEqual(len(result.hypotheses), 1)

    def test_hardware_profile_resource_limits(self):
        """Test hardware profiling and memory pressure guard."""
        normal_hw = HardwareProfile(cpu_cores=8, ram_total_gb=16.0, ram_available_gb=6.5)
        self.assertFalse(normal_hw.is_memory_pressured())
        self.assertEqual(normal_hw.get_max_safe_context_tokens(), 8192)

        pressured_hw = HardwareProfile(cpu_cores=4, ram_total_gb=8.0, ram_available_gb=1.1)
        self.assertTrue(pressured_hw.is_memory_pressured())
        self.assertEqual(pressured_hw.get_max_safe_context_tokens(), 2048)

    def test_ollama_supervisor_circuit_breaker_and_ledger(self):
        """Test inference recording and circuit breaker threshold."""
        supervisor = OllamaSupervisor(default_model="llama3.2")
        self.assertEqual(supervisor.state, SupervisorState.READY)
        self.assertTrue(supervisor.is_available())
        
        # Record successful inference
        rec1 = supervisor.record_inference(
            inference_id="inf_01",
            cognitive_role="strategic_reasoning",
            snapshot_id="snap_101",
            prompt_version="v4.0",
            latency_ms=145.2,
            parse_success=True
        )
        self.assertEqual(len(supervisor.inference_ledger), 1)
        self.assertEqual(supervisor.consecutive_failures, 0)
        
        # Simulate 3 consecutive parse/model failures
        supervisor.record_inference("inf_02", "reasoning", "snap_101", "v4.0", 50.0, False)
        supervisor.record_inference("inf_03", "reasoning", "snap_101", "v4.0", 50.0, False)
        supervisor.record_inference("inf_04", "reasoning", "snap_101", "v4.0", 50.0, False)
        
        self.assertEqual(supervisor.state, SupervisorState.DEGRADED)
        self.assertFalse(supervisor.is_available())


if __name__ == "__main__":
    unittest.main()
