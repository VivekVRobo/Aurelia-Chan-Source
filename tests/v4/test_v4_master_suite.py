"""
Aurelia Cognitive OS V4 - Master 12-Phase Test Runner
======================================================
Runs the complete test suite across all 12 Phases:
Phase 0 through Phase 11.
"""

import unittest
import sys

def run_all_phases():
    test_modules = [
        'test_v4_phase0_contracts',
        'test_v4_phase1_domain_brain',
        'test_v4_phase2_memory',
        'test_v4_phase3_orchestration',
        'test_v4_phase4_llm_supervisor',
        'test_v4_phase5_search',
        'test_v4_phase6_verification',
        'test_v4_phase7_artifacts',
        'test_v4_phase8_trace_and_character',
        'test_v4_phase9_evaluation',
        'test_v4_phase10_integration',
        'test_v4_phase11_reliability'
    ]

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for mod in test_modules:
        suite.addTests(loader.loadTestsFromName(mod))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 65)
    print(f"  TOTAL V4 COGNITIVE TESTS RUN: {result.testsRun}")
    print(f"  FAILURES: {len(result.failures)}")
    print(f"  ERRORS:   {len(result.errors)}")
    is_success = result.wasSuccessful()
    print(f"  VERDICT:  {'>>> ALL 12 PHASES 100% VERIFIED & PASSING! <<<' if is_success else 'FAILURES DETECTED'}")
    print("=" * 65)
    return is_success

if __name__ == "__main__":
    success = run_all_phases()
    sys.exit(0 if success else 1)
