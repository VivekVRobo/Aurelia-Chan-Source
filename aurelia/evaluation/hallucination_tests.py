"""
Aurelia Cognitive OS V3 - Phase 11: Hallucination Tests
=======================================================
Tests for detecting and preventing hallucinations.

Hallucination tests validate that the system doesn't generate
false or unsubstantiated information.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class HallucinationType(Enum):
    """Types of hallucinations to test for."""
    FACTUAL_HALLUCINATION = "factual_hallucination"
    NUMERIC_HALLUCINATION = "numeric_hallucination"
    ATTRIBUTION_HALLUCINATION = "attribution_hallucination"
    TEMPORAL_HALLUCINATION = "temporal_hallucination"
    CONSISTENCY_HALLUCINATION = "consistency_hallucination"


@dataclass
class HallucinationTestCase:
    """
    A test case for hallucination detection.
    
    Tests whether the system generates false information.
    """
    id: str
    hallucination_type: HallucinationType
    description: str
    query: str
    should_have_evidence: bool
    known_facts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HallucinationTestResult:
    """
    Result of a hallucination test.
    
    Contains analysis of whether hallucination occurred.
    """
    test_id: str
    hallucinated: bool
    confidence: float
    hallucination_type: Optional[HallucinationType]
    unsupported_claims: List[str]
    evidence_provided: bool
    timestamp: datetime


class HallucinationTester:
    """
    Tests for detecting and preventing hallucinations.
    
    The hallucination tester:
    - Tests for various types of hallucinations
    - Checks that claims are supported by evidence
    - Validates factual correctness
    - Ensures consistency in responses
    """
    
    def __init__(self):
        self.test_cases: Dict[str, HallucinationTestCase] = {}
        self.test_results: List[HallucinationTestResult] = []
        self.test_counter = 0
    
    def add_test_case(
        self,
        hallucination_type: HallucinationType,
        description: str,
        query: str,
        should_have_evidence: bool,
        known_facts: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> HallucinationTestCase:
        """Add a hallucination test case."""
        test_id = f"hallucination_test_{self.test_counter}"
        
        test_case = HallucinationTestCase(
            id=test_id,
            hallucination_type=hallucination_type,
            description=description,
            query=query,
            should_have_evidence=should_have_evidence,
            known_facts=known_facts or [],
            metadata=metadata or {}
        )
        
        self.test_cases[test_id] = test_case
        self.test_counter += 1
        
        return test_case
    
    def run_test(self, test_id: str, response_func) -> HallucinationTestResult:
        """
        Run a hallucination test.
        
        response_func should take query and return response with evidence.
        """
        test_case = self.get_test_case(test_id)
        if not test_case:
            raise ValueError(f"Test case {test_id} not found")
        
        # Get response
        try:
            response = response_func(test_case.query)
        except Exception as e:
            response = {"content": f"Error: {str(e)}", "evidence": []}
        
        # Analyze for hallucinations
        hallucinated, unsupported_claims = self._detect_hallucination(
            response,
            test_case
        )
        
        # Check if evidence was provided
        evidence_provided = self._check_evidence_provided(response, test_case)
        
        result = HallucinationTestResult(
            test_id=test_id,
            hallucinated=hallucinated,
            confidence=0.8,  # Would be calculated more precisely in full system
            hallucination_type=test_case.hallucination_type if hallucinated else None,
            unsupported_claims=unsupported_claims,
            evidence_provided=evidence_provided,
            timestamp=datetime.now()
        )
        
        self.test_results.append(result)
        return result
    
    def _detect_hallucination(self, response: Dict[str, Any], test_case: HallucinationTestCase) -> tuple[bool, List[str]]:
        """Detect if response contains hallucinations."""
        unsupported_claims = []
        
        # In full system, would use sophisticated NLP techniques
        # For now, use simple heuristics
        
        content = response.get("content", "").lower()
        evidence = response.get("evidence", [])
        
        # Check if response makes claims without evidence when evidence is expected
        if test_case.should_have_evidence and not evidence:
            unsupported_claims.append("Claims made without evidence")
        
        # Check for known facts (in full system would verify against knowledge base)
        if test_case.known_facts:
            for fact in test_case.known_facts:
                if fact.lower() not in content:
                    unsupported_claims.append(f"Potential inconsistency with known fact: {fact}")
        
        return len(unsupported_claims) > 0, unsupported_claims
    
    def _check_evidence_provided(self, response: Dict[str, Any], test_case: HallucinationTestCase) -> bool:
        """Check if evidence was provided for claims."""
        evidence = response.get("evidence", [])
        return len(evidence) > 0 if test_case.should_have_evidence else True
    
    def run_all_tests(self, response_func) -> List[HallucinationTestResult]:
        """Run all hallucination test cases."""
        results = []
        
        for test_id in self.test_cases:
            result = self.run_test(test_id, response_func)
            results.append(result)
        
        return results
    
    def get_test_case(self, test_id: str) -> Optional[HallucinationTestCase]:
        """Get a test case by ID."""
        return self.test_cases.get(test_id)
    
    def get_test_cases_by_type(self, hallucination_type: HallucinationType) -> List[HallucinationTestCase]:
        """Get all test cases of a specific type."""
        return [tc for tc in self.test_cases.values() if tc.hallucination_type == hallucination_type]
    
    def get_hallucination_summary(self) -> Dict[str, Any]:
        """Get a summary of hallucination test results."""
        hallucinated_tests = [r for r in self.test_results if r.hallucinated]
        
        return {
            "total_tests": len(self.test_results),
            "hallucinated": len(hallucinated_tests),
            "clean": len(self.test_results) - len(hallucinated_tests),
            "hallucination_rate": len(hallucinated_tests) / len(self.test_results) if self.test_results else 0.0,
            "by_type": {
                ht.value: len([r for r in hallucinated_tests if r.hallucination_type == ht])
                for ht in HallucinationType
            }
        }