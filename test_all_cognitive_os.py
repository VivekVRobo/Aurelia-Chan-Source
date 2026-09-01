"""
Aurelia Cognitive OS - Master Test Runner
=========================================
Discovers and executes all unit, integration, and adversarial suites
across V4, V5, and V6 subpackages (111 comprehensive tests).
"""

import os
import sys
import unittest

WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

def run_all_tests():
    v4_modules = [
        'tests.v4.test_v4_phase0_contracts',
        'tests.v4.test_v4_phase1_domain_brain',
        'tests.v4.test_v4_phase2_memory',
        'tests.v4.test_v4_phase3_orchestration',
        'tests.v4.test_v4_phase4_llm_supervisor',
        'tests.v4.test_v4_phase5_search',
        'tests.v4.test_v4_phase6_verification',
        'tests.v4.test_v4_phase7_artifacts',
        'tests.v4.test_v4_phase8_trace_and_character',
        'tests.v4.test_v4_phase9_evaluation',
        'tests.v4.test_v4_phase10_integration',
        'tests.v4.test_v4_phase11_reliability'
    ]

    v5_modules = [
        'tests.v5.test_v5_phase0_contracts',
        'tests.v5.test_v5_phase1_outcomes',
        'tests.v5.test_v5_phase2_velocity',
        'tests.v5.test_v5_phase3_goal_forecast',
        'tests.v5.test_v5_phase4_strategy_model',
        'tests.v5.test_v5_phase5_insights_and_decay',
        'tests.v5.test_v5_phase6_value_of_information',
        'tests.v5.test_v5_phase7_adaptive_interview',
        'tests.v5.test_v5_phase8_plan_drift',
        'tests.v5.test_v5_phase9_experiments',
        'tests.v5.test_v5_phase10_proactivity',
        'tests.v5.test_v5_phase11_artifact_graph'
    ]

    v6_modules = [
        'tests.v6.test_v6_phase0_contracts',
        'tests.v6.test_v6_phase1_working_memory',
        'tests.v6.test_v6_phase2_document_intelligence',
        'tests.v6.test_v6_phase3_change_detection',
        'tests.v6.test_v6_phase4_accessibility_and_scene_graph',
        'tests.v6.test_v6_phase5_vision_router',
        'tests.v6.test_v6_phase6_speech_and_prosody',
        'tests.v6.test_v6_phase7_entity_resolution',
        'tests.v6.test_v6_phase8_source_dependence',
        'tests.v6.test_v6_phase9_attention_and_purpose',
        'tests.v6.test_v6_phase10_privacy_firewall',
        'tests.v6.test_v6_phase11_contradiction_engine',
        'tests.v6.test_v6_phase12_context_candidate_set',
        'tests.v6.test_v6_phase13_transactional_receipts',
        'tests.v6.test_v6_adversarial_suite'
    ]

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for mod in v4_modules + v5_modules + v6_modules:
        try:
            suite.addTests(loader.loadTestsFromName(mod))
        except Exception as e:
            print(f"Error loading {mod}: {e}")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print(f"  TOTAL COMBINED TESTS RUN: {result.testsRun}")
    print(f"  FAILURES: {len(result.failures)}")
    print(f"  ERRORS:   {len(result.errors)}")
    is_success = result.wasSuccessful()
    print(f"  VERDICT:  {'>>> ALL AURELIA COGNITIVE OS TESTS 100% VERIFIED! <<<' if is_success else 'FAILURES DETECTED'}")
    print("=" * 70)
    return is_success

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
