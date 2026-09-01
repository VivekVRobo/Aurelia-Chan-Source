"""
Aurelia Cognitive OS V3 - Phase 5: Constraint Solver
====================================================
Handles constraints and optimization for planning.

The constraint solver handles:
- Time constraints (deadlines, dependencies)
- Resource constraints (time, budget, energy)
- Preference constraints (user preferences)
- Conflict resolution between constraints
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
from datetime import datetime, timedelta


class ConstraintType(Enum):
    """Types of constraints."""
    TIME = "time"  # Time-based constraints (deadlines, duration)
    RESOURCE = "resource"  # Resource constraints (budget, energy)
    PREFERENCE = "preference"  # User preference constraints
    DEPENDENCY = "dependency"  # Dependency constraints
    MUTUAL_EXCLUSION = "mutual_exclusion"  # Tasks that cannot happen together


class ConstraintSeverity(Enum):
    """Severity of constraint violations."""
    CRITICAL = "critical"  # Must be satisfied
    HIGH = "high"  # Should be satisfied
    MEDIUM = "medium"  # Nice to satisfy
    LOW = "low"  # Optional


@dataclass
class Constraint:
    """
    A constraint in the planning system.
    
    Constraints define what must or should be true in a plan.
    """
    id: str
    constraint_type: ConstraintType
    description: str
    severity: ConstraintSeverity
    is_satisfied: bool = False
    violation_message: Optional[str] = None
    check_function: Optional[Callable] = None  # Function to check if constraint is satisfied
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConstraintViolation:
    """A record of a constraint violation."""
    constraint_id: str
    constraint_description: str
    severity: ConstraintSeverity
    violation_message: str
    suggested_resolution: Optional[str] = None


class ConstraintSolver:
    """
    Handles constraints and optimization for planning.
    
    The constraint solver:
    - Validates plans against constraints
    - Detects constraint violations
    - Suggests resolutions for violations
    - Optimizes plans within constraints
    """
    
    def __init__(self):
        self.constraints: Dict[str, Constraint] = {}
        self.constraint_counter = 0
    
    def add_constraint(self, constraint: Constraint):
        """Add a constraint."""
        self.constraints[constraint.id] = constraint
    
    def create_constraint(
        self,
        constraint_type: ConstraintType,
        description: str,
        severity: ConstraintSeverity = ConstraintSeverity.HIGH,
        check_function: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Constraint:
        """Create and add a new constraint."""
        constraint_id = f"constraint_{self.constraint_counter}"
        
        constraint = Constraint(
            id=constraint_id,
            constraint_type=constraint_type,
            description=description,
            severity=severity,
            check_function=check_function,
            metadata=metadata or {}
        )
        
        self.add_constraint(constraint)
        return constraint
    
    def get_constraint(self, constraint_id: str) -> Optional[Constraint]:
        """Get a constraint by ID."""
        return self.constraints.get(constraint_id)
    
    def get_constraints_by_type(self, constraint_type: ConstraintType) -> List[Constraint]:
        """Get all constraints of a specific type."""
        return [c for c in self.constraints.values() if c.constraint_type == constraint_type]
    
    def get_constraints_by_severity(self, severity: ConstraintSeverity) -> List[Constraint]:
        """Get all constraints of a specific severity."""
        return [c for c in self.constraints.values() if c.severity == severity]
    
    def check_constraint(self, constraint: Constraint, context: Dict[str, Any]) -> bool:
        """Check if a constraint is satisfied."""
        if constraint.check_function:
            return constraint.check_function(context)
        
        # Default constraint checking logic based on type
        if constraint.constraint_type == ConstraintType.TIME:
            # Check time constraints
            if "deadline" in constraint.metadata:
                deadline = constraint.metadata["deadline"]
                current_time = context.get("current_time", datetime.now())
                return current_time <= deadline
        
        elif constraint.constraint_type == ConstraintType.RESOURCE:
            # Check resource constraints
            if "max_budget" in constraint.metadata:
                max_budget = constraint.metadata["max_budget"]
                current_budget = context.get("current_budget", 0)
                return current_budget <= max_budget
        
        return True  # Default to satisfied if no specific check
    
    def validate_plan(self, context: Dict[str, Any]) -> List[ConstraintViolation]:
        """
        Validate a plan against all constraints.
        
        Returns a list of constraint violations.
        """
        violations = []
        
        for constraint in self.constraints.values():
            is_satisfied = self.check_constraint(constraint, context)
            constraint.is_satisfied = is_satisfied
            
            if not is_satisfied:
                violation = ConstraintViolation(
                    constraint_id=constraint.id,
                    constraint_description=constraint.description,
                    severity=constraint.severity,
                    violation_message=constraint.violation_message or f"Constraint '{constraint.description}' not satisfied",
                    suggested_resolution=self.suggest_resolution(constraint, context)
                )
                violations.append(violation)
        
        return violations
    
    def suggest_resolution(self, constraint: Constraint, context: Dict[str, Any]) -> Optional[str]:
        """Suggest a resolution for a constraint violation."""
        if constraint.constraint_type == ConstraintType.TIME:
            if "deadline" in constraint.metadata:
                deadline = constraint.metadata["deadline"]
                return f"Extend deadline to {deadline + timedelta(days=7)} or reduce scope"
        
        elif constraint.constraint_type == ConstraintType.RESOURCE:
            if "max_budget" in constraint.metadata:
                max_budget = constraint.metadata["max_budget"]
                return f"Increase budget beyond {max_budget} or reduce resource requirements"
        
        elif constraint.constraint_type == ConstraintType.DEPENDENCY:
            return "Reorder tasks to satisfy dependencies or remove conflicting dependencies"
        
        return "Review constraint requirements and adjust plan accordingly"
    
    def is_plan_valid(self, context: Dict[str, Any]) -> bool:
        """Check if a plan is valid (no critical violations)."""
        violations = self.validate_plan(context)
        critical_violations = [v for v in violations if v.severity == ConstraintSeverity.CRITICAL]
        return len(critical_violations) == 0
    
    def get_constraint_conflicts(self) -> List[tuple]:
        """
        Detect conflicts between constraints.
        
        Returns a list of tuples (constraint1_id, constraint2_id, conflict_description).
        """
        conflicts = []
        
        # Simple conflict detection: time vs resource conflicts
        time_constraints = self.get_constraints_by_type(ConstraintType.TIME)
        resource_constraints = self.get_constraints_by_type(ConstraintType.RESOURCE)
        
        for time_c in time_constraints:
            for resource_c in resource_constraints:
                # If a tight time constraint conflicts with limited resources
                if (time_c.severity == ConstraintSeverity.CRITICAL and 
                    resource_c.severity == ConstraintSeverity.CRITICAL):
                    conflicts.append((
                        time_c.id,
                        resource_c.id,
                        "Critical time constraint conflicts with critical resource constraint"
                    ))
        
        return conflicts
    
    def optimize_plan(
        self,
        context: Dict[str, Any],
        optimization_objective: str = "minimize_time"
    ) -> Dict[str, Any]:
        """
        Optimize a plan within constraints.
        
        Simple optimization - in a full system this would use more sophisticated algorithms.
        """
        violations = self.validate_plan(context)
        
        if not violations:
            return {"status": "optimal", "violations": []}
        
        # Sort violations by severity
        severity_order = {
            ConstraintSeverity.CRITICAL: 0,
            ConstraintSeverity.HIGH: 1,
            ConstraintSeverity.MEDIUM: 2,
            ConstraintSeverity.LOW: 3
        }
        
        violations.sort(key=lambda v: severity_order[v.severity])
        
        return {
            "status": "needs_optimization",
            "violations": violations,
            "critical_violations": [v for v in violations if v.severity == ConstraintSeverity.CRITICAL],
            "optimization_suggestions": [v.suggested_resolution for v in violations if v.suggested_resolution]
        }
    
    def initialize_default_constraints(self):
        """Initialize default constraints for career planning."""
        # Time constraint: goals should have reasonable deadlines
        self.create_constraint(
            constraint_type=ConstraintType.TIME,
            description="Goals should have reasonable timeframes (not too aggressive)",
            severity=ConstraintSeverity.HIGH,
            metadata={"max_duration_years": 5}
        )
        
        # Resource constraint: learning activities should be sustainable
        self.create_constraint(
            constraint_type=ConstraintType.RESOURCE,
            description="Learning activities should be sustainable (not overwhelming)",
            severity=ConstraintSeverity.MEDIUM,
            metadata={"max_weekly_hours": 20}
        )
        
        # Dependency constraint: tasks should respect dependencies
        self.create_constraint(
            constraint_type=ConstraintType.DEPENDENCY,
            description="Tasks should respect their dependencies",
            severity=ConstraintSeverity.CRITICAL
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the constraint solver state."""
        return {
            "total_constraints": len(self.constraints),
            "by_type": {ct.value: len(self.get_constraints_by_type(ct)) for ct in ConstraintType},
            "by_severity": {cs.value: len(self.get_constraints_by_severity(cs)) for cs in ConstraintSeverity},
            "conflicts": len(self.get_constraint_conflicts())
        }