"""
Aurelia Cognitive OS V3 - Phase 11: Golden Suite
===============================================
Predefined test cases with known correct answers.

The golden suite contains carefully crafted test cases with
expected outcomes to validate system correctness.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class TestCategory(Enum):
    """Categories of golden suite tests."""
    ACCURACY = "accuracy"
    REASONING = "reasoning"
    KNOWLEDGE = "knowledge"
    CONSISTENCY = "consistency"
    SAFETY = "safety"


@dataclass
class GoldenTestCase:
    """
    A test case with known correct answer.
    
    Represents a predefined test scenario with expected outcomes.
    """
    id: str
    category: TestCategory
    description: str
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    tolerance: Dict[str, float] = field(default_factory=dict)  # For approximate matches
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResult:
    """
    Result of running a golden suite test.
    
    Contains the actual output and whether it matched expectations.
    """
    test_id: str
    passed: bool
    actual_output: Dict[str, Any]
    expected_output: Dict[str, Any]
    differences: List[str]
    execution_time: float
    timestamp: datetime


class GoldenSuite:
    """
    Predefined test cases with known correct answers.
    
    The golden suite:
    - Contains carefully crafted test cases
    - Validates system correctness against known answers
    - Tracks test results and performance
    - Provides detailed failure analysis
    """
    
    def __init__(self):
        self.test_cases: Dict[str, GoldenTestCase] = {}
        self.test_results: List[TestResult] = []
        self.test_counter = 0
    
    def add_test_case(
        self,
        category: TestCategory,
        description: str,
        input_data: Dict[str, Any],
        expected_output: Dict[str, Any],
        tolerance: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> GoldenTestCase:
        """Add a test case to the golden suite."""
        test_id = f"golden_test_{self.test_counter}"
        
        test_case = GoldenTestCase(
            id=test_id,
            category=category,
            description=description,
            input_data=input_data,
            expected_output=expected_output,
            tolerance=tolerance or {},
            metadata=metadata or {}
        )
        
        self.test_cases[test_id] = test_case
        self.test_counter += 1
        
        return test_case
    
    def run_test(self, test_id: str, execute_func) -> TestResult:
        """
        Run a single test case.
        
        execute_func should take input_data and return actual_output.
        """
        test_case = self.get_test_case(test_id)
        if not test_case:
            raise ValueError(f"Test case {test_id} not found")
        
        start_time = datetime.now()
        
        # Execute the test
        try:
            actual_output = execute_func(test_case.input_data)
        except Exception as e:
            actual_output = {"error": str(e)}
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Compare with expected output
        passed, differences = self._compare_outputs(
            actual_output,
            test_case.expected_output,
            test_case.tolerance
        )
        
        result = TestResult(
            test_id=test_id,
            passed=passed,
            actual_output=actual_output,
            expected_output=test_case.expected_output,
            differences=differences,
            execution_time=execution_time,
            timestamp=datetime.now()
        )
        
        self.test_results.append(result)
        return result
    
    def _compare_outputs(
        self,
        actual: Dict[str, Any],
        expected: Dict[str, Any],
        tolerance: Dict[str, float]
    ) -> tuple[bool, List[str]]:
        """Compare actual output with expected output."""
        differences = []
        
        # Check all expected keys
        for key, expected_value in expected.items():
            if key not in actual:
                differences.append(f"Missing key: {key}")
                continue
            
            actual_value = actual[key]
            
            # Check for tolerance-based comparison for numeric values
            if key in tolerance and isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
                if abs(actual_value - expected_value) > tolerance[key]:
                    differences.append(f"Value mismatch for {key}: expected {expected_value}, got {actual_value} (tolerance: {tolerance[key]})")
            else:
                # Exact comparison
                if actual_value != expected_value:
                    differences.append(f"Value mismatch for {key}: expected {expected_value}, got {actual_value}")
        
        # Check for unexpected keys
        for key in actual:
            if key not in expected:
                differences.append(f"Unexpected key: {key}")
        
        return len(differences) == 0, differences
    
    def run_all_tests(self, execute_func) -> List[TestResult]:
        """Run all test cases in the golden suite."""
        results = []
        
        for test_id in self.test_cases:
            result = self.run_test(test_id, execute_func)
            results.append(result)
        
        return results
    
    def get_test_case(self, test_id: str) -> Optional[GoldenTestCase]:
        """Get a test case by ID."""
        return self.test_cases.get(test_id)
    
    def get_test_cases_by_category(self, category: TestCategory) -> List[GoldenTestCase]:
        """Get all test cases of a specific category."""
        return [tc for tc in self.test_cases.values() if tc.category == category]
    
    def get_results_by_category(self, category: TestCategory) -> List[TestResult]:
        """Get all test results for a specific category."""
        test_ids = [tc.id for tc in self.get_test_cases_by_category(category)]
        return [r for r in self.test_results if r.test_id in test_ids]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of golden suite results."""
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
            "by_category": {
                cat.value: {
                    "total": len(self.get_test_cases_by_category(cat)),
                    "passed": len([r for r in self.get_results_by_category(cat) if r.passed]),
                    "failed": len([r for r in self.get_results_by_category(cat) if not r.passed])
                }
                for cat in TestCategory
            }
        }