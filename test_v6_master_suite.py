"""
Aurelia Cognitive OS V6 - Master Test Suite Runner
===================================================
Runs all 15 unit test suites across all V6 perception subsystems:
Phase 0 through Phase 14.
"""

import unittest
import sys

def run_v6_master_suite():
    test_modules = [
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

    for mod in test_modules:
        suite.addTests(loader.loadTestsFromName(mod))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print(f"  TOTAL V6 PERCEPTION TESTS RUN: {result.testsRun}")
    print(f"  FAILURES: {len(result.failures)}")
    print(f"  ERRORS:   {len(result.errors)}")
    is_success = result.wasSuccessful()
    print(f"  VERDICT:  {'>>> ALL V6 PHASES 0-14 100% VERIFIED & PASSING! <<<' if is_success else 'FAILURES DETECTED'}")
    print("=" * 70)
    return is_success

if __name__ == "__main__":
    success = run_v6_master_suite()
    sys.exit(0 if success else 1)
