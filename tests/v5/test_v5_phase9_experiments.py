"""
Aurelia Cognitive OS V5 - Phase 9 Experiments Test Suite
=========================================================
Tests empirical strategy experiments and causal learning guards.
"""

import unittest
from aurelia.experiments.experiment import ExperimentEngine
from aurelia.contracts.v5_contracts import ExperimentStatus


class TestV5Phase9Experiments(unittest.TestCase):
    """Test suite for Phase 9 Experiments."""

    def test_experiment_supported_after_minimum_samples(self):
        """Test hypothesis supported when observed uplift exceeds threshold."""
        engine = ExperimentEngine()
        
        # Baseline score = 70.0, hypothesis: shorter answers increase score
        exp = engine.create_experiment(
            experiment_id="exp_star_length",
            hypothesis="Shorter concise STAR answers increase interview score.",
            baseline_metric_name="interview_score",
            baseline_value=70.0,
            intervention_tag="concise_star",
            minimum_samples=3
        )
        self.assertEqual(exp.status, ExperimentStatus.RUNNING)
        
        # Sample 1: 85.0 (still RUNNING, N=1 < 3)
        engine.record_observation("exp_star_length", 85.0)
        self.assertEqual(exp.status, ExperimentStatus.RUNNING)
        
        # Sample 2: 90.0 (still RUNNING, N=2 < 3)
        engine.record_observation("exp_star_length", 90.0)
        self.assertEqual(exp.status, ExperimentStatus.RUNNING)
        
        # Sample 3: 88.0 (N=3 == min_samples, mean=87.67 vs 70.0 baseline -> SUPPORTED)
        engine.record_observation("exp_star_length", 88.0)
        self.assertEqual(exp.status, ExperimentStatus.SUPPORTED)
        self.assertTrue(exp.is_causally_supported)

    def test_experiment_inconclusive(self):
        """Test hypothesis inconclusive when delta is within noise threshold."""
        engine = ExperimentEngine()
        
        exp = engine.create_experiment(
            experiment_id="exp_passive_study",
            hypothesis="Passive reading increases interview score.",
            baseline_metric_name="interview_score",
            baseline_value=70.0,
            intervention_tag="passive_reading",
            minimum_samples=3
        )
        
        engine.record_observation("exp_passive_study", 70.0)
        engine.record_observation("exp_passive_study", 70.5)
        engine.record_observation("exp_passive_study", 69.8)
        
        self.assertEqual(exp.status, ExperimentStatus.INCONCLUSIVE)
        self.assertFalse(exp.is_causally_supported)


if __name__ == "__main__":
    unittest.main()
