"""
Aurelia Cognitive OS V4 - Phase 1 Domain Brain & Solvers Test Suite
====================================================================
Tests Numerical Firewall V2, Monte Carlo Simulation, Competency Engine,
and Temporal Career Knowledge Graph.
"""

import unittest
from datetime import datetime, timezone, timedelta
from aurelia.solvers.numerical import Money, EquityGrant, TimelineMonths, NumericalFirewall
from aurelia.solvers.simulation import MonteCarloSimulator, SimulationDistribution
from aurelia.knowledge.evidence import CompetencyRequirement, CompetencyAssessment, CompetencyEvidenceEngine
from aurelia.knowledge.graph import TemporalCareerGraph, KnowledgeNode, TemporalEdge, NodeType, EdgeType
from aurelia.contracts.core_types import EvidenceRef, EvidenceReliability


class TestPhase1DomainBrain(unittest.TestCase):
    """Test suite for Phase 1 Domain Brain and Solvers."""

    def test_numerical_firewall_money_normalization(self):
        """Test currency and period normalization."""
        usd_year = Money(amount=200000.0, currency="USD", period="year")
        self.assertEqual(usd_year.to_annual_usd(), 200000.0)

        usd_month = Money(amount=15000.0, currency="USD", period="month")
        self.assertEqual(usd_month.to_annual_usd(), 180000.0)

        eur_year = Money(amount=100000.0, currency="EUR", period="year")
        self.assertEqual(eur_year.to_annual_usd(), 108000.0)

    def test_total_target_compensation_calculation(self):
        """Test exact deterministic compensation calculation."""
        base = Money(amount=220000.0, currency="USD", period="year")
        total = NumericalFirewall.calculate_total_target_compensation(
            base_salary=base,
            target_bonus_pct=20.0,      # $44,000
            annual_equity_value=60000.0,# $60,000
            signing_bonus_first_year=25000.0 # $25,000
        )
        # 220,000 + 44,000 + 60,000 + 25,000 = 349,000
        self.assertEqual(total.amount, 349000.0)

    def test_arithmetic_verification(self):
        """Test numerical firewall arithmetic validator."""
        passed, err = NumericalFirewall.verify_arithmetic_claim(
            claim_description="Revenue increase",
            expected_value=1200000.0,
            actual_value=1205000.0,
            tolerance_pct=1.0
        )
        self.assertTrue(passed)
        self.assertIsNone(err)

        failed, err2 = NumericalFirewall.verify_arithmetic_claim(
            claim_description="Revenue discrepancy",
            expected_value=1000000.0,
            actual_value=1200000.0,
            tolerance_pct=1.0
        )
        self.assertFalse(failed)
        self.assertIn("Numerical discrepancy", err2)

    def test_monte_carlo_budget_aware_simulation(self):
        """Test budget-aware Monte Carlo distribution simulation."""
        equity = EquityGrant(
            ownership_percentage=0.005,  # 0.5%
            vesting_years=4.0
        )
        
        # Test Fast Budget (250 runs)
        dist_fast = MonteCarloSimulator.simulate_startup_equity_outcomes(
            equity=equity,
            base_valuation_usd=50000000.0, # $50M Series A
            budget_mode="fast"
        )
        self.assertEqual(dist_fast.runs_executed, 250)
        self.assertTrue(0.0 <= dist_fast.probability_of_zero <= 1.0)
        self.assertTrue(dist_fast.p10_downside <= dist_fast.p50_median <= dist_fast.p90_upside)

        # Test Standard Budget (1000 runs)
        dist_std = MonteCarloSimulator.simulate_startup_equity_outcomes(
            equity=equity,
            base_valuation_usd=50000000.0,
            budget_mode="standard"
        )
        self.assertEqual(dist_std.runs_executed, 1000)

    def test_competency_readiness_calculation(self):
        """Test deterministic readiness scoring and bottleneck discovery."""
        reqs = [
            CompetencyRequirement(competency_id="comp_lead", name="People Leadership", required_level=4.0, weight=1.0),
            CompetencyRequirement(competency_id="comp_budget", name="Budget Ownership", required_level=3.0, weight=1.0),
            CompetencyRequirement(competency_id="comp_comm", name="Exec Communication", required_level=4.0, weight=1.0),
        ]
        
        ev_item = EvidenceRef(id="ev_01", source_type="resume", content_snippet="Led 12 engineers", reliability=EvidenceReliability.HISTORICAL_FACT)
        
        assessments = [
            CompetencyAssessment(
                competency_id="comp_lead",
                name="People Leadership",
                observed_score=4.2,     # Met (4.2 >= 4.0)
                required_score=4.0,
                gap=0.0,
                evidence_items=(ev_item,),
                is_satisfied=True,
                confidence=0.90
            ),
            CompetencyAssessment(
                competency_id="comp_budget",
                name="Budget Ownership",
                observed_score=1.8,     # Gap (1.8 < 3.0)
                required_score=3.0,
                gap=1.2,
                evidence_items=(),
                is_satisfied=False,
                confidence=0.75
            ),
            CompetencyAssessment(
                competency_id="comp_comm",
                name="Exec Communication",
                observed_score=3.2,     # Gap (3.2 < 4.0)
                required_score=4.0,
                gap=0.8,
                evidence_items=(),
                is_satisfied=False,
                confidence=0.80
            ),
        ]
        
        readiness_pct, met_list, gap_list = CompetencyEvidenceEngine.calculate_readiness_score(reqs, assessments)
        
        # Lead: 1.0 (capped), Budget: 1.8/3.0 = 0.6, Comm: 3.2/4.0 = 0.8 => (1.0 + 0.6 + 0.8)/3 = 2.4/3 = 80.0%
        self.assertAlmostEqual(readiness_pct, 80.0, places=1)
        self.assertEqual(len(met_list), 1)
        self.assertIn("People Leadership", met_list[0])
        self.assertEqual(len(gap_list), 2)
        self.assertIn("Budget Ownership gap", gap_list[0])

    def test_temporal_career_graph_pathfinding_and_validity(self):
        """Test temporal graph search and time-bounded validity."""
        graph = TemporalCareerGraph()
        
        # Test BFS pathfinding from Senior EM to CTO
        path = graph.find_progression_path("role_senior_em", "role_cto")
        self.assertIsNotNone(path)
        self.assertEqual(path, ["role_senior_em", "role_director", "role_vp_eng", "role_cto"])

        # Test Temporal Edge Validity Bounds
        now = datetime.now(timezone.utc)
        past_edge = TemporalEdge(
            source_id="person_01",
            target_id="role_swe",
            edge_type=EdgeType.DEMONSTRATES,
            valid_from=now - timedelta(days=700),
            valid_to=now - timedelta(days=365) # Expired 1 year ago
        )
        self.assertFalse(past_edge.is_active_at(now))
        self.assertTrue(past_edge.is_active_at(now - timedelta(days=500)))


if __name__ == "__main__":
    unittest.main()
