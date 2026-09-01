"""
Aurelia Cognitive OS V3 - Phase 11: Memory Tests
===============================================
Tests for memory system correctness and performance.

Memory tests validate that the memory systems (working, episodic,
semantic, procedural, strategic) function correctly.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class MemoryType(Enum):
    """Types of memory to test."""
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    STRATEGIC = "strategic"


class MemoryOperation(Enum):
    """Memory operations to test."""
    STORE = "store"
    RETRIEVE = "retrieve"
    UPDATE = "update"
    DELETE = "delete"
    CONSOLIDATE = "consolidate"


@dataclass
class MemoryTestCase:
    """
    A test case for memory operations.
    
    Tests specific memory system operations.
    """
    id: str
    memory_type: MemoryType
    operation: MemoryOperation
    description: str
    input_data: Dict[str, Any]
    expected_result: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryTestResult:
    """
    Result of a memory test.
    
    Contains the actual result and whether it matched expectations.
    """
    test_id: str
    passed: bool
    actual_result: Dict[str, Any]
    expected_result: Dict[str, Any]
    differences: List[str]
    timestamp: datetime


class MemoryTester:
    """
    Tests for memory system correctness and performance.
    
    The memory tester:
    - Tests all memory system operations
    - Validates data integrity
    - Tests retrieval accuracy
    - Tests consolidation processes
    """
    
    def __init__(self):
        self.test_cases: Dict[str, MemoryTestCase] = {}
        self.test_results: List[MemoryTestResult] = []
        self.test_counter = 0
    
    def add_test_case(
        self,
        memory_type: MemoryType,
        operation: MemoryOperation,
        description: str,
        input_data: Dict[str, Any],
        expected_result: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> MemoryTestCase:
        """Add a memory test case."""
        test_id = f"memory_test_{self.test_counter}"
        
        test_case = MemoryTestCase(
            id=test_id,
            memory_type=memory_type,
            operation=operation,
            description=description,
            input_data=input_data,
            expected_result=expected_result,
            metadata=metadata or {}
        )
        
        self.test_cases[test_id] = test_case
        self.test_counter += 1
        
        return test_case
    
    def run_test(self, test_id: str, memory_func) -> MemoryTestResult:
        """
        Run a memory test.
        
        memory_func should take input_data and return actual_result.
        """
        test_case = self.get_test_case(test_id)
        if not test_case:
            raise ValueError(f"Test case {test_id} not found")
        
        # Execute the memory operation
        try:
            actual_result = memory_func(test_case.input_data)
        except Exception as e:
            actual_result = {"error": str(e)}
        
        # Compare with expected result
        passed, differences = self._compare_results(
            actual_result,
            test_case.expected_result
        )
        
        result = MemoryTestResult(
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
            
            if actual_value != expected_value:
                differences.append(f"Value mismatch for {key}: expected {expected_value}, got {actual_value}")
        
        # Check for unexpected keys
        for key in actual:
            if key not in expected and key != "timestamp":  # Allow timestamp differences
                differences.append(f"Unexpected key: {key}")
        
        return len(differences) == 0, differences
    
    def run_all_tests(self, memory_func) -> List[MemoryTestResult]:
        """Run all memory test cases."""
        results = []
        
        for test_id in self.test_cases:
            result = self.run_test(test_id, memory_func)
            results.append(result)
        
        return results
    
    def get_test_case(self, test_id: str) -> Optional[MemoryTestCase]:
        """Get a test case by ID."""
        return self.test_cases.get(test_id)
    
    def get_test_cases_by_memory_type(self, memory_type: MemoryType) -> List[MemoryTestCase]:
        """Get all test cases for a specific memory type."""
        return [tc for tc in self.test_cases.values() if tc.memory_type == memory_type]
    
    def get_test_cases_by_operation(self, operation: MemoryOperation) -> List[MemoryTestCase]:
        """Get all test cases for a specific operation."""
        return [tc for tc in self.test_cases.values() if tc.operation == operation]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of memory test results."""
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
            "by_memory_type": {
                mt.value: {
                    "total": len(self.get_test_cases_by_memory_type(mt)),
                    "passed": len([r for r in self.test_results if r.passed and self.get_test_case(r.test_id).memory_type == mt]),
                    "failed": len([r for r in self.test_results if not r.passed and self.get_test_case(r.test_id).memory_type == mt])
                }
                for mt in MemoryType
            },
            "by_operation": {
                op.value: {
                    "total": len(self.get_test_cases_by_operation(op)),
                    "passed": len([r for r in self.test_results if r.passed and self.get_test_case(r.test_id).operation == op]),
                    "failed": len([r for r in self.test_results if not r.passed and self.get_test_case(r.test_id).operation == op])
                }
                for op in MemoryOperation
            }
        }