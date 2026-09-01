"""
Aurelia Cognitive OS V3 - Phase 9: Replanning Engine
=================================================
Handles dynamic replanning when plans fail or circumstances change.

The replanning engine enables Aurelia to adapt when initial plans
are not working or when situations change.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class ReplanningTrigger(Enum):
    """Triggers for replanning."""
    PLAN_FAILURE = "plan_failure"
    OBSTACLE_ENCOUNTERED = "obstacle_encountered"
    CONTEXT_CHANGE = "context_change"
    RESOURCE_CONSTRAINT = "resource_constraint"
    NEW_INFORMATION = "new_information"
    DEADLINE_MISSED = "deadline_missed"


class ReplanningStrategy(Enum):
    """Strategies for replanning."""
    ADJUST_TIMELINE = "adjust_timeline"
    MODIFY_SCOPE = "modify_scope"
    CHANGE_APPROACH = "change_approach"
    SEEK_ALTERNATIVES = "seek_alternatives"
    ABORT_PLAN = "abort_plan"


@dataclass
class ReplanningAction:
    """
    A replanning action to be taken.
    
    Defines what should change in the current plan.
    """
    action_type: ReplanningStrategy
    description: str
    affected_components: List[str]
    priority: float  # 0-1 scale
    estimated_impact: str
    new_parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReplanningResult:
    """
    Result of replanning process.
    
    Contains new plan or recommendation for how to proceed.
    """
    original_plan_id: str
    trigger: ReplanningTrigger
    actions: List[ReplanningAction]
    new_plan_id: Optional[str]
    success: bool
    confidence: float
    rationale: str


class ReplanningEngine:
    """
    Handles dynamic replanning when plans fail or circumstances change.
    
    The replanning engine:
    - Detects when replanning is needed
    - Determines appropriate replanning strategies
    - Generates replanning actions
    - Adjusts plans dynamically
    """
    
    def __init__(self):
        self.replanning_history: List[ReplanningResult] = []
        self.current_plans: Dict[str, Any] = {}
        self.plan_counter = 0
    
    def detect_replanning_need(
        self,
        plan_id: str,
        execution_status: str,
        obstacles: List[str],
        deadline_status: str
    ) -> Optional[ReplanningTrigger]:
        """
        Detect if replanning is needed.
        
        Analyzes execution status and triggers replanning if needed.
        """
        triggers = []
        
        if execution_status == "failed":
            triggers.append(ReplanningTrigger.PLAN_FAILURE)
        
        if obstacles:
            triggers.append(ReplanningTrigger.OBSTACLE_ENCOUNTERED)
        
        if deadline_status == "missed":
            triggers.append(ReplanningTrigger.DEADLINE_MISSED)
        
        # If multiple triggers, return the most urgent
        if not triggers:
            return None
        
        # Priority: PLAN_FAILURE > DEADLINE_MISSED > OBSTACLE_ENCOUNTERED > others
        priority = {
            ReplanningTrigger.PLAN_FAILURE: 4,
            ReplanningTrigger.DEADLINE_MISSED: 3,
            ReplanningTrigger.OBSTACLE_ENCOUNTERED: 2,
            ReplanningTrigger.CONTEXT_CHANGE: 1,
            ReplanningTrigger.RESOURCE_CONSTRAINT: 1,
            ReplanningTrigger.NEW_INFORMATION: 1
        }
        
        return max(triggers, key=lambda t: priority[t])
    
    def determine_replanning_strategy(
        self,
        trigger: ReplanningTrigger,
        context: Dict[str, Any]
    ) -> ReplanningStrategy:
        """
        Determine appropriate replanning strategy.
        
        Selects the best approach given the trigger and context.
        """
        if trigger == ReplanningTrigger.PLAN_FAILURE:
            # Plan failed - need different approach
            return ReplanningStrategy.CHANGE_APPROACH
        
        elif trigger == ReplanningTrigger.DEADLINE_MISSED:
            # Deadline missed - adjust timeline or scope
            if context.get("flexible_deadline", False):
                return ReplanningStrategy.ADJUST_TIMELINE
            else:
                return ReplanningStrategy.MODIFY_SCOPE
        
        elif trigger == ReplanningTrigger.OBSTACLE_ENCOUNTERED:
            # Obstacle - assess impact
            obstacle_severity = context.get("obstacle_severity", "medium")
            if obstacle_severity == "minor":
                return ReplanningStrategy.ADJUST_TIMELINE
            elif obstacle_severity == "major":
                return ReplanningStrategy.CHANGE_APPROACH
            else:
                return ReplanningStrategy.MODIFY_SCOPE
        
        elif trigger == ReplanningTrigger.RESOURCE_CONSTRAINT:
            # Resource constraints - modify scope
            return ReplanningStrategy.MODIFY_SCOPE
        
        else:
            # Default to seeking alternatives
            return ReplanningStrategy.SEEK_ALTERNATIVES
    
    def generate_replanning_actions(
        self,
        strategy: ReplanningStrategy,
        plan_id: str,
        context: Dict[str, Any]
    ) -> List[ReplanningAction]:
        """
        Generate specific replanning actions.
        
        Creates concrete actions based on the chosen strategy.
        """
        actions = []
        
        if strategy == ReplanningStrategy.ADJUST_TIMELINE:
            actions.append(ReplanningAction(
                action_type=strategy,
                description="Extend timeline to accommodate current progress",
                affected_components=["timeline", "milestones"],
                new_parameters={"timeline_extension": "30 days"},
                priority=0.8,
                estimated_impact="moderate"
            ))
        
        elif strategy == ReplanningStrategy.MODIFY_SCOPE:
            actions.append(ReplanningAction(
                action_type=strategy,
                description="Reduce scope to match available resources",
                affected_components=["scope", "deliverables"],
                new_parameters={"scope_reduction": "20%"},
                priority=0.9,
                estimated_impact="significant"
            ))
        
        elif strategy == ReplanningStrategy.CHANGE_APPROACH:
            actions.append(ReplanningAction(
                action_type=strategy,
                description="Change approach to achieve objectives",
                affected_components=["methodology", "tools"],
                new_parameters={"new_approach": "alternative method"},
                priority=0.7,
                estimated_impact="significant"
            ))
        
        elif strategy == ReplanningStrategy.SEEK_ALTERNATIVES:
            actions.append(ReplanningAction(
                action_type=strategy,
                description="Explore alternative ways to achieve goals",
                affected_components=["objectives", "approach"],
                new_parameters={"alternative_paths": "explore 2-3 alternatives"},
                priority=0.6,
                estimated_impact="variable"
            ))
        
        return actions
    
    def execute_replanning(
        self,
        plan_id: str,
        trigger: ReplanningTrigger,
        context: Dict[str, Any]
    ) -> ReplanningResult:
        """
        Execute the replanning process.
        
        Determines strategy, generates actions, and creates new plan.
        """
        # Determine strategy
        strategy = self.determine_replanning_strategy(trigger, context)
        
        # Generate actions
        actions = self.generate_replanning_actions(strategy, plan_id, context)
        
        # Create new plan
        new_plan_id = f"plan_{self.plan_counter}"
        self.plan_counter += 1
        
        # In full system, would actually modify the plan structure
        self.current_plans[new_plan_id] = {
            "original_plan_id": plan_id,
            "trigger": trigger.value,
            "strategy": strategy.value,
            "actions": [a.description for a in actions],
            "context": context
        }
        
        # Calculate confidence in new plan
        confidence = self._calculate_replanning_confidence(actions, context)
        
        # Generate rationale
        rationale = self._generate_rationale(trigger, strategy, actions)
        
        result = ReplanningResult(
            original_plan_id=plan_id,
            trigger=trigger,
            actions=actions,
            new_plan_id=new_plan_id,
            success=True,
            confidence=confidence,
            rationale=rationale
        )
        
        self.replanning_history.append(result)
        return result
    
    def _calculate_replanning_confidence(self, actions: List[ReplanningAction], context: Dict[str, Any]) -> float:
        """Calculate confidence in replanning outcome."""
        # Base confidence reduced by number of actions
        base_confidence = 0.8
        action_penalty = len(actions) * 0.05
        return max(0.3, base_confidence - action_penalty)
    
    def _generate_rationale(self, trigger: ReplanningTrigger, strategy: ReplanningStrategy, actions: List[ReplanningAction]) -> str:
        """Generate rationale for replanning decision."""
        rationale = f"Replanning triggered by {trigger.value}. "
        rationale += f"Strategy: {strategy.value}. "
        rationale += f"Actions: {len(actions)} actions will be taken to address the situation."
        
        return rationale
    
    def get_replanning_history(self, limit: int = 10) -> List[ReplanningResult]:
        """Get recent replanning results."""
        return self.replanning_history[-limit:]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the replanning engine state."""
        return {
            "total_replans": len(self.replanning_history),
            "current_plans": len(self.current_plans),
            "successful_replans": len([r for r in self.replanning_history if r.success]),
            "by_trigger": {trigger.value: len([r for r in self.replanning_history if r.trigger == trigger]) for trigger in ReplanningTrigger}
        }