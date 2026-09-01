"""
Aurelia Cognitive OS V4 - Ablation & No-LLM Benchmark Harness
=============================================================
Measures the percentage of requests solved deterministically (model_calls = 0)
and evaluates performance degradation when subsystems are ablated.
"""

from typing import List, Dict, Tuple, Any


class BenchmarkHarness:
    """
    Evaluates system intelligence efficiency and subsystem value.
    """

    @staticmethod
    def calculate_no_llm_rate(session_records: List[Dict[str, Any]]) -> float:
        """
        Calculates the percentage of user interactions resolved with zero LLM calls.
        """
        if not session_records:
            return 0.0
            
        no_llm_count = sum(1 for r in session_records if r.get("llm_calls_made", 0) == 0)
        return (no_llm_count / len(session_records)) * 100.0

    @staticmethod
    def run_ablation_comparison(
        baseline_score: float,
        ablated_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculates accuracy drop when subsystems are removed.
        Returns degradation percentage per ablated component.
        """
        impacts: Dict[str, float] = {}
        for component, score in ablated_scores.items():
            drop = max(0.0, baseline_score - score)
            impacts[component] = drop
        return impacts
