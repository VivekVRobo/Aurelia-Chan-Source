"""
Aurelia Cognitive OS V3 - Phase 9: Scenario Simulation
=================================================
Simulates possible scenarios and their outcomes.

Scenario simulation allows Aurelia to explore "what if" scenarios
and their potential consequences before recommending actions.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
import copy


class ScenarioType(Enum):
    """Types of scenarios to simulate."""
    CAREER_PATH = "career_path"
    SKILL_DEVELOPMENT = "skill_development"
    ORGANIZATIONAL_CHANGE = "organizational_change"
    MARKET_CONDITIONS = "market_conditions"
    TIMELINE_VARIATION = "timeline_variation"


class ScenarioStatus(Enum):
    """Status of scenario simulation."""
    PLAUSIBLE = "plausible"
    UNLIKELY = "unlikely"
    UNCERTAIN = "uncertain"
    HIGH_RISK = "high_risk"
    LOW_RISK = "low_risk"


@dataclass
class ScenarioParameter:
    """A parameter that can be varied in scenario simulation."""
    name: str
    current_value: Any
    possible_values: List[Any]
    impact_level: str  # "high", "medium", "low"


@dataclass
class Scenario:
    """
    A scenario to simulate.
    
    Scenarios represent "what if" situations and their parameters.
    """
    id: str
    scenario_type: ScenarioType
    description: str
    parameters: Dict[str, Any]
    assumptions: List[str]
    status: ScenarioStatus = ScenarioStatus.UNCERTAIN
    probability: float = 0.5
    confidence: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SimulationResult:
    """
    Result of running a scenario simulation.
    
    Contains outcomes, probabilities, and recommendations.
    """
    scenario_id: str
    outcomes: List[Dict[str, Any]]
    probability: float
    confidence: float
    risks: List[str]
    benefits: List[str]
    recommendation: str
    alternative_scenarios: List[str] = field(default_factory=list)


class ScenarioSimulator:
    """
    Simulates possible scenarios and their outcomes.
    
    The scenario simulator:
    - Defines scenarios with variable parameters
    - Runs simulations with different parameter values
    - Estimates probabilities and risks
    - Provides recommendations based on simulation results
    """
    
    def __init__(self):
        self.scenarios: Dict[str, Scenario] = {}
        self.scenario_counter = 0
        self.simulation_history: List[SimulationResult] = []
    
    def create_scenario(
        self,
        scenario_type: ScenarioType,
        description: str,
        parameters: Dict[str, Any],
        assumptions: Optional[List[str]] = None
    ) -> Scenario:
        """Create a new scenario."""
        scenario_id = f"scenario_{self.scenario_counter}"
        
        scenario = Scenario(
            id=scenario_id,
            scenario_type=scenario_type,
            description=description,
            parameters=parameters,
            assumptions=assumptions or [],
            status=ScenarioStatus.UNCERTAIN
        )
        
        self.scenarios[scenario_id] = scenario
        self.scenario_counter += 1
        
        return scenario
    
    def simulate_scenario(
        self,
        scenario_id: str,
        parameter_variations: Optional[Dict[str, List[Any]]] = None
    ) -> SimulationResult:
        """
        Simulate a scenario with parameter variations.
        
        Explores different "what if" scenarios and their outcomes.
        """
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")
        
        # Base simulation with current parameters
        base_outcomes = self._calculate_outcomes(scenario.parameters)
        
        # Simulate with parameter variations if provided
        all_outcomes = [base_outcomes]
        
        if parameter_variations:
            for param_name, variations in parameter_variations.items():
                for variation in variations:
                    varied_params = copy.deepcopy(scenario.parameters)
                    varied_params[param_name] = variation
                    varied_outcomes = self._calculate_outcomes(varied_params)
                    all_outcomes.append(varied_outcomes)
        
        # Calculate overall probability and confidence
        probability = self._estimate_probability(all_outcomes)
        confidence = self._estimate_confidence(all_outcomes, scenario.assumptions)
        
        # Determine status
        status = self._determine_status(probability, confidence)
        
        # Extract risks and benefits
        risks = self._extract_risks(all_outcomes)
        benefits = self._extract_benefits(all_outcomes)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(status, risks, benefits)
        
        # Find alternative scenarios
        alternatives = self._find_alternative_scenarios(scenario)
        
        result = SimulationResult(
            scenario_id=scenario_id,
            outcomes=all_outcomes,
            probability=probability,
            confidence=confidence,
            risks=risks,
            benefits=benefits,
            recommendation=recommendation,
            alternative_scenarios=alternatives
        )
        
        self.simulation_history.append(result)
        return result
    
    def _calculate_outcomes(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate outcomes for a given parameter set."""
        # Simplified outcome calculation - in full system would use domain models
        outcomes = {
            "parameters": parameters,
            "success_probability": 0.5,  # Default
            "time_to_complete": "6-12 months",
            "resource_requirements": "moderate",
            "potential_roadblocks": []
        }
        
        # Adjust based on parameters
        if parameters.get("skill_level", 0) > 0.7:
            outcomes["success_probability"] = 0.8
            outcomes["time_to_complete"] = "3-6 months"
        else:
            outcomes["success_probability"] = 0.4
            outcomes["time_to_complete"] = "12-18 months"
            outcomes["potential_roadblocks"].append("Skill gap")
        
        market_conditions = parameters.get("market_conditions", "favorable")
        if market_conditions == "favorable":
            outcomes["success_probability"] += 0.1
        elif market_conditions == "challenging":
            outcomes["success_probability"] -= 0.15
            outcomes["potential_roadblocks"].append("Market constraints")
        
        return outcomes
    
    def _estimate_probability(self, outcomes: List[Dict[str, Any]]) -> float:
        """Estimate overall probability from simulation outcomes."""
        if not outcomes:
            return 0.5
        
        success_probs = [o.get("success_probability", 0.5) for o in outcomes]
        return sum(success_probs) / len(success_probs)
    
    def _estimate_confidence(self, outcomes: List[Dict[str, Any]], assumptions: List[str]) -> float:
        """Estimate confidence in simulation results."""
        # More assumptions = lower confidence
        base_confidence = 0.8
        assumption_penalty = len(assumptions) * 0.05
        return max(0.3, base_confidence - assumption_penalty)
    
    def _determine_status(self, probability: float, confidence: float) -> ScenarioStatus:
        """Determine scenario status based on probability and confidence."""
        if probability < 0.3:
            return ScenarioStatus.UNLIKELY
        elif probability > 0.7 and confidence > 0.7:
            return ScenarioStatus.PLAUSIBLE
        elif probability < 0.5:
            return ScenarioStatus.HIGH_RISK
        else:
            return ScenarioStatus.LOW_RISK
    
    def _extract_risks(self, outcomes: List[Dict[str, Any]]) -> List[str]:
        """Extract risks from simulation outcomes."""
        risks = set()
        
        for outcome in outcomes:
            roadblocks = outcome.get("potential_roadblocks", [])
            risks.update(roadblocks)
        
        # Add common risks
        if any(o.get("success_probability", 0.5) < 0.4 for o in outcomes):
            risks.add("Low success probability")
        
        return list(risks)
    
    def _extract_benefits(self, outcomes: List[Dict[str, Any]]) -> List[str]:
        """Extract benefits from simulation outcomes."""
        benefits = []
        
        if any(o.get("success_probability", 0.5) > 0.7 for o in outcomes):
            benefits.append("High success probability")
        
        if any(o.get("time_to_complete", "") in ["3-6 months", "3-9 months"] for o in outcomes):
            benefits.append("Fast completion possible")
        
        return benefits
    
    def _generate_recommendation(self, status: ScenarioStatus, risks: List[str], benefits: List[str]) -> str:
        """Generate recommendation based on simulation results."""
        if status == ScenarioStatus.PLAUSIBLE:
            return "This scenario appears feasible. Proceed with confidence while monitoring key risks."
        elif status == ScenarioStatus.UNLIKELY:
            return "This scenario has low probability of success. Consider alternative approaches."
        elif status == ScenarioStatus.HIGH_RISK:
            return "This scenario carries significant risk. Implement risk mitigation strategies before proceeding."
        else:
            return "This scenario is moderately feasible. Proceed with caution and monitor progress closely."
    
    def _find_alternative_scenarios(self, scenario: Scenario) -> List[str]:
        """Find alternative scenarios related to the current one."""
        alternatives = []
        
        # Simple alternative finding based on scenario type
        if scenario.scenario_type == ScenarioType.CAREER_PATH:
            alternatives = ["Consider alternative career progression paths", "Explore lateral moves for skill development"]
        elif scenario.scenario_type == ScenarioType.SKILL_DEVELOPMENT:
            alternatives = ["Consider different skill development approaches", "Prioritize high-impact skills"]
        elif scenario.scenario_type == ScenarioType.ORGANIZATIONAL_CHANGE:
            alternatives = ["Consider internal mobility", "Explore external opportunities with similar growth"]
        
        return alternatives
    
    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Get a scenario by ID."""
        return self.scenarios.get(scenario_id)
    
    def get_scenarios_by_type(self, scenario_type: ScenarioType) -> List[Scenario]:
        """Get all scenarios of a specific type."""
        return [s for s in self.scenarios.values() if s.scenario_type == scenario_type]
    
    def get_simulation_history(self, limit: int = 10) -> List[SimulationResult]:
        """Get recent simulation results."""
        return self.simulation_history[-limit:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the scenario simulator state."""
        return {
            "total_scenarios": len(self.scenarios),
            "by_type": {st.value: len(self.get_scenarios_by_type(st)) for st in ScenarioType},
            "total_simulations": len(self.simulation_history),
            "recent_simulations": len(self.get_simulation_history(5))
        }