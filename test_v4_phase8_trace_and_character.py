"""
Aurelia Cognitive OS V4 - Phase 8 Trace & Character Test Suite
===============================================================
Tests Safe Structured Cognitive Trace formatting and CharacterDirector expression mapping.
"""

import unittest
from aurelia.response.trace import SafeCognitiveTrace
from aurelia.character.director import CharacterDirector
from aurelia.contracts.core_types import VerificationSeverity


class TestPhase8TraceAndCharacter(unittest.TestCase):
    """Test suite for Phase 8 Safe Trace & Character Director."""

    def test_safe_cognitive_trace_formatting(self):
        """Invariant: Cognitive trace must not contain raw <think> tags."""
        trace = SafeCognitiveTrace(
            understood_goal="Compare Series B startup equity vs Big Tech Director offer",
            memories_retrieved_count=6,
            graph_facts_count=12,
            specialists_invoked=("CompensationNormalizer", "MonteCarloSimulator", "RiskCritic"),
            alternatives_evaluated=("Startup_Accept", "FAANG_Remain", "Negotiate_Equity"),
            numerical_calculations_verified=("Equity P50 ($84k)", "Total Comp ($349k)"),
            unresolved_unknowns=("Startup exit timeline",),
            contradictions_detected=0,
            confidence_percentage=78.0,
            confidence_level="Moderate-High"
        )
        
        summary = trace.to_formatted_summary()
        self.assertIn("### 🧠 Aurelia's Analysis", summary)
        self.assertIn("✓ Understood: Compare Series B startup", summary)
        self.assertIn("✓ Verified 2 numerical calculations", summary)
        self.assertNotIn("<think>", summary)
        self.assertNotIn("</think>", summary)

    def test_character_director_expression_resolution(self):
        """Test expression mapping across cognitive states and severities."""
        # Blocker severity forces warning
        exp_blocker = CharacterDirector.resolve_expression(
            cognitive_state="ANALYZING",
            verification_severity=VerificationSeverity.BLOCKER
        )
        self.assertEqual(exp_blocker, "warning")

        # Entitlement triggers warning
        exp_warn = CharacterDirector.resolve_expression("ENTITLEMENT_WARNING")
        self.assertEqual(exp_warn, "warning")

        # Verified plan triggers confident
        exp_conf = CharacterDirector.resolve_expression("VERIFIED_PLAN")
        self.assertEqual(exp_conf, "confident")

        # Audit triggers analyzing
        exp_audit = CharacterDirector.resolve_expression("ANALYZING_METRICS")
        self.assertEqual(exp_audit, "analyzing")


if __name__ == "__main__":
    unittest.main()
