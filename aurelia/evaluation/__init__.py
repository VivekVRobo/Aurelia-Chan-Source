"""
Aurelia Cognitive OS V3 - Phase 11: Evaluation Module
=====================================================
Evaluation capabilities for testing system correctness.

Includes golden suite tests, adversarial conversations, hallucination tests,
memory tests, and planning tests.
"""

from .golden_suite import (
    GoldenSuite,
    TestCategory,
    GoldenTestCase,
    TestResult
)

from .adversarial_testing import (
    AdversarialTester,
    AdversarialType,
    TestOutcome,
    AdversarialTestCase,
    AdversarialTestResult
)

from .hallucination_tests import (
    HallucinationTester,
    HallucinationType,
    HallucinationTestCase,
    HallucinationTestResult
)

from .memory_tests import (
    MemoryTester,
    MemoryType,
    MemoryOperation,
    MemoryTestCase,
    MemoryTestResult
)

from .planning_tests import (
    PlanningTester,
    PlanningComponent,
    PlanningScenario,
    PlanningTestCase,
    PlanningTestResult
)

__all__ = [
    # Golden Suite
    "GoldenSuite",
    "TestCategory",
    "GoldenTestCase",
    "TestResult",
    # Adversarial Testing
    "AdversarialTester",
    "AdversarialType",
    "TestOutcome",
    "AdversarialTestCase",
    "AdversarialTestResult",
    # Hallucination Tests
    "HallucinationTester",
    "HallucinationType",
    "HallucinationTestCase",
    "HallucinationTestResult",
    # Memory Tests
    "MemoryTester",
    "MemoryType",
    "MemoryOperation",
    "MemoryTestCase",
    "MemoryTestResult",
    # Planning Tests
    "PlanningTester",
    "PlanningComponent",
    "PlanningScenario",
    "PlanningTestCase",
    "PlanningTestResult"
]