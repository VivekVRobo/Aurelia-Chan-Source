"""
Aurelia Cognitive OS - Complete V4 & V5 Full System Test Suite
==============================================================
Runs all 49 V4 tests + all 24 V5 tests = 73 comprehensive tests.
"""

import unittest
import sys

def run_all_tests():
    v4_modules = [
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

    v5_modules = [
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

    v6_modules = [
        'test_v6_phase0_contracts',
        'test_v6_phase1_working_memory',
        'test_v6_phase2_document_intelligence',
        'test_v6_phase3_change_detection',
        'test_v6_phase4_accessibility_and_scene_graph',
        'test_v6_phase5_vision_router',
        'test_v6_phase6_speech_and_prosody',
        'test_v6_phase7_entity_resolution',
        'test_v6_phase8_source_dependence',
        'test_v6_phase9_attention_and_purpose',
        'test_v6_phase10_privacy_firewall',
        'test_v6_phase11_contradiction_engine',
        'test_v6_phase12_context_candidate_set',
        'test_v6_phase13_transactional_receipts',
        'test_v6_adversarial_suite'
    ]

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for mod in v4_modules + v5_modules + v6_modules:
        suite.addTests(loader.loadTestsFromName(mod))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print(f"  TOTAL V4 + V5 COMBINED TESTS RUN: {result.testsRun}")
    print(f"  FAILURES: {len(result.failures)}")
    print(f"  ERRORS:   {len(result.errors)}")
    is_success = result.wasSuccessful()
    print(f"  VERDICT:  {'>>> COMPLETE AURELIA COGNITIVE OS V4 & V5 100% VERIFIED! <<<' if is_success else 'FAILURES DETECTED'}")
    print("=" * 70)
    return is_success

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
