"""
Aurelia Cognitive OS V5 - Master Test Suite Runner
===================================================
Runs all 12 unit test suites across all V5 subsystems:
Phase 0 through Phase 11.
"""

import unittest
import sys

def run_v5_master_suite():
    test_modules = [
        'test_v5_phase0_contracts',
        'test_v5_phase1_outcomes',
        'test_v5_phase2_velocity',
        'test_v5_phase3_goal_forecast',
        'test_v5_phase4_strategy_model',
        'test_v5_phase5_insights_and_decay',
        'test_v5_phase6_value_of_information',
        'test_v5_phase7_adaptive_interview',
        'test_v5_phase8_plan_drift',
        'test_v5_phase9_experiments',
        'test_v5_phase10_proactivity',
        'test_v5_phase11_artifact_graph'
    ]

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for mod in test_modules:
        suite.addTests(loader.loadTestsFromName(mod))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print(f"  TOTAL V5 COGNITIVE TESTS RUN: {result.testsRun}")
    print(f"  FAILURES: {len(result.failures)}")
    print(f"  ERRORS:   {len(result.errors)}")
    is_success = result.wasSuccessful()
    print(f"  VERDICT:  {'>>> ALL V5 PHASES 0-11 100% VERIFIED & PASSING! <<<' if is_success else 'FAILURES DETECTED'}")
    print("=" * 70)
    return is_success

if __name__ == "__main__":
    success = run_v5_master_suite()
    sys.exit(0 if success else 1)
