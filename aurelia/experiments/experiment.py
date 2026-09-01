"""
Aurelia Cognitive OS V5 - Empirical Strategy Experiment Engine
==============================================================
Enables empirical hypothesis testing across interview framing and negotiation tactics,
with strict causal inference guards to prevent learning spurious correlations.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from aurelia.contracts.v5_contracts import ExperimentStatus


@dataclass
class StrategyExperiment:
    """Empirical strategy experiment record."""
    experiment_id: str
    hypothesis: str
    baseline_metric_name: str
    baseline_value: float
    intervention_tag: str
    minimum_samples: int
    samples_collected: List[float] = field(default_factory=list)
    status: ExperimentStatus = ExperimentStatus.RUNNING
    is_causally_supported: bool = False
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ExperimentEngine:
    """
    Manages empirical strategy testing and evaluates causality guards.
    """

    def __init__(self):
        self.experiments: Dict[str, StrategyExperiment] = {}

    def create_experiment(
        self,
        experiment_id: str,
        hypothesis: str,
        baseline_metric_name: str,
        baseline_value: float,
        intervention_tag: str,
        minimum_samples: int = 3
    ) -> StrategyExperiment:
        """Registers a new empirical strategy experiment."""
        exp = StrategyExperiment(
            experiment_id=experiment_id,
            hypothesis=hypothesis,
            baseline_metric_name=baseline_metric_name,
            baseline_value=baseline_value,
            intervention_tag=intervention_tag,
            minimum_samples=minimum_samples,
            samples_collected=[]
        )
        self.experiments[experiment_id] = exp
        return exp

    def record_observation(
        self,
        experiment_id: str,
        observed_value: float
    ) -> StrategyExperiment:
        """
        Records an empirical data point and updates experiment status.
        """
        if experiment_id not in self.experiments:
            raise KeyError(f"Experiment {experiment_id} not found.")

        exp = self.experiments[experiment_id]
        exp.samples_collected.append(observed_value)

        # Evaluate status once minimum samples reached
        if len(exp.samples_collected) >= exp.minimum_samples:
            avg_observed = sum(exp.samples_collected) / len(exp.samples_collected)
            delta = avg_observed - exp.baseline_value

            if delta >= 3.0: # Meaningful positive uplift (e.g. +3 points on 100 scale)
                exp.status = ExperimentStatus.SUPPORTED
                exp.is_causally_supported = True
            elif delta <= -3.0: # Meaningful negative decline
                exp.status = ExperimentStatus.UNSUPPORTED
                exp.is_causally_supported = False
            else:
                exp.status = ExperimentStatus.INCONCLUSIVE
                exp.is_causally_supported = False
        else:
            exp.status = ExperimentStatus.RUNNING

        return exp
