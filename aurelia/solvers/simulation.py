"""
Aurelia Cognitive OS V4 - Budget-Aware Monte Carlo & Scenario Simulator
========================================================================
Runs deterministic mathematical simulations for equity, compensation,
and career transition outcomes without hallucinated LLM guesses.
"""

import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from aurelia.solvers.numerical import Money, EquityGrant


@dataclass(frozen=True)
class SimulationDistribution:
    """
    Quantile outcomes from a Monte Carlo simulation.
    """
    runs_executed: int
    p10_downside: float
    p25_conservative: float
    p50_median: float
    p75_optimistic: float
    p90_upside: float
    expected_mean: float
    probability_of_zero: float          # e.g., startup total failure rate


class MonteCarloSimulator:
    """
    Budget-aware local Monte Carlo simulator for executive compensation and startup risk.
    """

    BUDGET_RUNS = {
        "fast": 250,
        "standard": 1000,
        "deep": 5000,
    }

    @classmethod
    def simulate_startup_equity_outcomes(
        cls,
        equity: EquityGrant,
        base_valuation_usd: float,
        years_to_exit: float = 4.0,
        budget_mode: str = "standard",
        seed: int = 42
    ) -> SimulationDistribution:
        """
        Simulates exit valuation distributions based on venture stage survival rates.
        """
        runs = cls.BUDGET_RUNS.get(budget_mode.lower(), 1000)
        rng = random.Random(seed)
        
        outcomes: List[float] = []
        zero_count = 0
        
        # Scenario weights: Failure (50%), Moderate Exit 1x-3x (30%), Strong Exit 3x-10x (15%), Unicorn 10x-50x (5%)
        for _ in range(runs):
            rand_val = rng.random()
            
            if rand_val < 0.50:
                # Company fails or equity wiped out by liquidation preference
                outcomes.append(0.0)
                zero_count += 1
            elif rand_val < 0.80:
                # Moderate exit: 1.0x to 3.0x valuation
                multiplier = rng.uniform(1.0, 3.0)
                diluted_pct = equity.ownership_percentage * (0.80 ** (years_to_exit / 2.0))
                annual_val = (base_valuation_usd * multiplier * diluted_pct) / years_to_exit
                outcomes.append(annual_val)
            elif rand_val < 0.95:
                # Strong exit: 3.0x to 10.0x valuation
                multiplier = rng.uniform(3.0, 10.0)
                diluted_pct = equity.ownership_percentage * (0.75 ** (years_to_exit / 2.0))
                annual_val = (base_valuation_usd * multiplier * diluted_pct) / years_to_exit
                outcomes.append(annual_val)
            else:
                # Exceptional unicorn exit: 10.0x to 40.0x valuation
                multiplier = rng.uniform(10.0, 40.0)
                diluted_pct = equity.ownership_percentage * (0.70 ** (years_to_exit / 2.0))
                annual_val = (base_valuation_usd * multiplier * diluted_pct) / years_to_exit
                outcomes.append(annual_val)
        
        outcomes.sort()
        n = len(outcomes)
        
        return SimulationDistribution(
            runs_executed=runs,
            p10_downside=outcomes[int(n * 0.10)],
            p25_conservative=outcomes[int(n * 0.25)],
            p50_median=outcomes[int(n * 0.50)],
            p75_optimistic=outcomes[int(n * 0.75)],
            p90_upside=outcomes[int(n * 0.90)],
            expected_mean=sum(outcomes) / n,
            probability_of_zero=zero_count / n
        )
