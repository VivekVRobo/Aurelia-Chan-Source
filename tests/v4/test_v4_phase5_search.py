"""
Aurelia Cognitive OS V4 - Phase 5 Search & Solvers Test Suite
==============================================================
Tests StrategicHypothesis utility, Beam Search with constraint pruning,
Independent Critics, and Counterfactual Sensitivity.
"""

import unittest
from aurelia.cognition.hypotheses import StrategicHypothesis, CognitiveSearchEngine
from aurelia.cognition.critic import StrategicCritic, RiskCritic, EvidenceCritic
from aurelia.cognition.counterfactual import CounterfactualEngine, SensitivityFactor
from aurelia.contracts.core_types import EvidenceRef, EvidenceReliability


class TestPhase5SearchAndSolvers(unittest.TestCase):
    """Test suite for Phase 5 Cognitive Search & Solvers."""

    def test_strategic_hypothesis_utility_and_pruning(self):
        """Test utility formula and hard constraint penalty."""
        valid_hyp = StrategicHypothesis(
            id="hyp_01",
            strategy_type="Internal_Promotion",
            title="Internal Director Transition",
            assumptions=("Reorg creates VP spot",),
            actions=("Acquire budget scope", "Deliver QBR"),
            expected_value_usd=320000.0,
            strategic_value_score=0.85,
            reversibility_score=0.75,
            risk_penalty=0.20,
            time_to_value_months=6.0,
            effort_cost=0.50,
            uncertainty_penalty=0.15
        )
        self.assertTrue(valid_hyp.calculate_utility() > 0.0)

        invalid_hyp = StrategicHypothesis(
            id="hyp_02",
            strategy_type="Relocation_Required",
            title="Move to SF Headquarters",
            assumptions=(),
            actions=("Relocate to SF",),
            expected_value_usd=400000.0,
            strategic_value_score=0.90,
            reversibility_score=0.20,
            risk_penalty=0.70,
            time_to_value_months=12.0,
            effort_cost=0.90,
            uncertainty_penalty=0.30,
            violates_hard_constraints=True
        )
        self.assertEqual(invalid_hyp.calculate_utility(), -999.0)

    def test_beam_search_with_constraint_pruning(self):
        """Test beam search filtering against user hard constraints and skills."""
        h1 = StrategicHypothesis(
            id="h_remote",
            strategy_type="Remote_Leadership",
            title="Remote VP of Engineering",
            assumptions=(),
            actions=("Manage global remote org",),
            expected_value_usd=350000.0,
            strategic_value_score=0.90,
            reversibility_score=0.80,
            risk_penalty=0.20,
            time_to_value_months=6.0,
            effort_cost=0.40,
            uncertainty_penalty=0.10,
            required_prerequisites=("distributed_leadership",)
        )
        h2 = StrategicHypothesis(
            id="h_relocate",
            strategy_type="In_Office_Relocation",
            title="Onsite New York Director",
            assumptions=(),
            actions=("Relocate to New York Office",),
            expected_value_usd=420000.0,
            strategic_value_score=0.95,
            reversibility_score=0.30,
            risk_penalty=0.50,
            time_to_value_months=4.0,
            effort_cost=0.80,
            uncertainty_penalty=0.20
        )
        
        # User constraint: "relocate", user skill: "distributed_leadership"
        ranked = CognitiveSearchEngine.evaluate_and_rank(
            hypotheses=[h1, h2],
            user_hard_constraints=["relocate"],
            user_known_skills=["distributed_leadership"],
            beam_width=2
        )
        
        self.assertEqual(len(ranked), 1)
        self.assertEqual(ranked[0].id, "h_remote")

    def test_independent_critics(self):
        """Test independent critic evaluations."""
        ev = EvidenceRef(id="ev_01", source_type="dossier", content_snippet="Verified $4M P&L ownership")
        hyp = StrategicHypothesis(
            id="h_test",
            strategy_type="Internal_Director",
            title="Internal Director",
            assumptions=(),
            actions=("Lead QBR",),
            expected_value_usd=320000.0,
            strategic_value_score=0.88,
            reversibility_score=0.70,
            risk_penalty=0.15,
            time_to_value_months=6.0,
            effort_cost=0.40,
            uncertainty_penalty=0.10,
            evidence=(ev,),
            confidence=0.88
        )
        
        crit_strat = StrategicCritic.critique(hyp, target_role="Director")
        self.assertTrue(crit_strat.passed)
        self.assertEqual(crit_strat.critic_role, "strategic_fit")

        crit_risk = RiskCritic.critique(hyp)
        self.assertTrue(crit_risk.passed)
        self.assertEqual(crit_risk.critic_role, "risk_assessor")

        crit_ev = EvidenceCritic.critique(hyp)
        self.assertTrue(crit_ev.passed)
        self.assertEqual(crit_ev.critic_role, "evidence_auditor")

    def test_counterfactual_engine_sensitivity(self):
        """Test sensitivity factor calculation."""
        factors = CounterfactualEngine.calculate_decision_sensitivity(
            current_readiness=68.0,
            target_threshold=80.0,
            competency_gaps={"Budget Ownership": 1.2, "Exec Presentation": 0.8}
        )
        self.assertEqual(len(factors), 2)
        self.assertEqual(factors[0].variable_name, "Budget Ownership")
        self.assertTrue(factors[0].sensitivity_percentage > factors[1].sensitivity_percentage)


if __name__ == "__main__":
    unittest.main()
