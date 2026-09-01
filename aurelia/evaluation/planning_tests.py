"""
Aurelia Cognitive OS V3 - Phase 11: Planning Tests
================================================
Tests for planning system correctness and performance.

Planning tests validate that the planning system (goal engine,
task graphs, constraint solver, progress tracker) functions correctly.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class PlanningComponent(Enum):
    """Planning components to test."""
    GOAL_ENGINE = "goal_engine"
    TASK_GRAPH = "task_graph"
    CONSTRAINT_SOLVER = "constraint_solver"
    PROGRESS_TRACKER = "progress_tracker"


class PlanningScenario(Enum):
    """Planning scenarios to test."""
    SIMPLE_GOAL = "simple_goal"
    HIERARCHICAL_GOALS = "hierarchical_goals"
    DEPENDENCY_RESOLUTION = "dependency_resolution"
    CONSTRAINT_VALIDATION = "constraint_validation"
    RECOVERY_FROM_FAILURE = "recovery_from_failure"


@dataclass
class PlanningTestCase:
    """
    A test case for planning operations.
    
    Tests specific planning system functionality.
    """
    id: str
    component: PlanningComponent
    scenario: PlanningScenario
    description: str
    input_data: Dict[str, Any]
    expected_result: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlanningTestResult:
    """
    Result of a planning test.
    
    Contains the actual result and whether it matched expectations.
    """
    test_id: str
    passed: bool
    actual_result: Dict[str, Any]
    expected_result: Dict[str, Any]
    differences: List[str]
    timestamp: datetime


class PlanningTester:
    """
    Tests for planning system correctness and performance.
    
    The planning tester:
    - Tests goal creation and management
    - Tests task graph operations
    - Tests constraint validation
    - Tests progress tracking
    - Tests dependency resolution
    """
    
    def __init__(self):
        self.test_cases: Dict[str, PlanningTestCase] = {}
        self.test_results: List[PlanningTestResult] = []
        self.test_counter = 0
    
    def add_test_case(
        self,
        component: PlanningComponent,
        scenario: PlanningScenario,
        description: str,
        input_data: Dict[str, Any],
        expected_result: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> PlanningTestCase:
        """Add a planning test case."""
        test_id = f"planning_test_{self.test_counter}"
        
        test_case = PlanningTestCase(
            id=test_id,
            component=component,
            scenario=scenario,
            description=description,
            input_data=input_data,
            expected_result=expected_result,
            metadata=metadata or {}
        )
        
        self.test_cases[test_id] = test_case
        self.test_counter += 1
        
        return test_case
    
    def run_test(self, test_id: str, planning_func) -> PlanningTestResult:
        """
        Run a planning test.
        
        planning_func should take input_data and return actual_result.
        """
        test_case = self.get_test_case(test_id)
        if not test_case:
            raise ValueError(f"Test case {test_id} not found")
        
        # Execute the planning operation
        try:
            actual_result = planning_func(test_case.input_data)
        except Exception as e:
            actual_result = {"error": str(e)}
        
        # Compare with expected result
        passed, differences = self._compare_results(
            actual_result,
            test_case.expected_result
        )
        
        result = PlanningTestResult(
            test_id=test_id,
            passed=passed,
            actual_result=actual_result,
            expected_result=test_case.expected_result,
            differences=differences,
            timestamp=datetime.now()
        )
        
        self.test_results.append(result)
        return result
    
    def _compare_results(self, actual: Dict[str, Any], expected: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Compare actual result with expected result."""
        differences = []
        
        # Check all expected keys
        for key, expected_value in expected.items():
            if key not in actual:
                differences.append(f"Missing key: {key}")
                continue
            
            actual_value = actual[key]
            
            # Allow for approximate numeric comparisons
            if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
                if abs(actual_value - expected_value) > 0.01:
                    differences.append(f"Value mismatch for {key}: expected {expected_value}, got {actual_value}")
            elif actual_value != expected_value:
                differences.append(f"Value mismatch for {key}: expected {expected_value}, got {actual_value}")
        
        # Check for unexpected keys
        for key in actual:
            if key not in expected and key != "timestamp":
                differences.append(f"Unexpected key: {key}")
        
        return len(differences) == 0, differences
    
    def run_all_tests(self, planning_func) -> List[PlanningTestResult]:
        """Run all planning test cases."""
        results = []
        
        for test_id in self.test_cases:
            result = self.run_test(test_id, planning_func)
            results.append(result)
        
        return results
    
    def get_test_case(self, test_id: str) -> Optional[PlanningTestCase]:
        """Get a test case by ID."""
        return self.test_cases.get(test_id)
    
    def get_test_cases_by_component(self, component: PlanningComponent) -> List[PlanningTestCase]:
        """Get all test cases for a specific component."""
        return [tc for tc in self.test_cases.values() if tc.component == component]
    
    def get_test_cases_by_scenario(self, scenario: PlanningScenario) -> List[PlanningTestCase]:
        """Get all test cases for a specific scenario."""
        return [tc for tc in self.test_cases.values() if tc.scenario == scenario]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of planning test results."""
        if not self.test_results:
            return {
                "total_tests": len(self.test_cases),
                "tests_run": 0,
                "passed": 0,
                "failed": 0,
                "pass_rate": 0.0
            }
        
        passed = sum(1 for r in self.test_results if r.passed)
        failed = len(self.test_results) - passed
        
        return {
            "total_tests": len(self.test_cases),
            "tests_run": len(self.test_results),
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / len(self.test_results) if self.test_results else 0.0,
            "by_component": {
                comp.value: {
                    "total": len(self.get_test_cases_by_component(comp)),
                    "passed": len([r for r in self.test_results if r.passed and self.get_test_case(r.test_id).component == comp]),
                    "failed": len([r for r in self.test_results if not r.passed and self.get_test_case(r.test_id).component == comp])
                }
                for comp in PlanningComponent
            },
            "by_scenario": {
                scen.value: {
                    "total": len(self.get_test_cases_by_scenario(scen)),
                    "passed": len([r for r in self.test_results if r.passed and self.get_test_case(r.test_id).scenario == scen]),
                    "failed": len([r for r in self.test_results if not r.passed and self.get_test_case(r.test_id).scenario == scen])
                }
                for scen in PlanningScenario
            }
        }