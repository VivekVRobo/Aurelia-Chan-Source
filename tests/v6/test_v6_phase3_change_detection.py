"""
Aurelia Cognitive OS V6 - Phase 3 Change Detection Test Suite
==============================================================
Tests change-driven perception, region diffing, and zero-inference static gating.
"""

import unittest
from aurelia.screen.change_detection import (
    ScreenRegion,
    ScreenState,
    ChangeDetectionEngine
)


class TestV6Phase3ChangeDetection(unittest.TestCase):
    """Test suite for Phase 3 Screen Change Detection."""

    def test_static_screen_zero_vision_inference(self):
        """Invariant: Static screen must execute 0 vision inference."""
        r1 = ScreenRegion("reg_main", 0, 0, 800, 600, "hash_abc123")
        r2 = ScreenRegion("reg_sidebar", 800, 0, 200, 600, "hash_def456")
        
        state1 = ScreenState("Visual Studio Code", "Code.exe", "global_hash_1", (r1, r2))
        state2 = ScreenState("Visual Studio Code", "Code.exe", "global_hash_1", (r1, r2))
        
        diff = ChangeDetectionEngine.evaluate_screen_change(state1, state2)
        self.assertFalse(diff.has_meaningful_change)
        self.assertFalse(diff.requires_vision_inference)
        self.assertEqual(diff.delta_score, 0.0)

    def test_window_switch_triggers_inference(self):
        """Test window focus switch triggers vision evaluation."""
        r1 = ScreenRegion("reg_main", 0, 0, 800, 600, "hash_abc123")
        
        state_vscode = ScreenState("Visual Studio Code", "Code.exe", "hash_1", (r1,))
        state_chrome = ScreenState("Google Chrome", "chrome.exe", "hash_1", (r1,))
        
        diff = ChangeDetectionEngine.evaluate_screen_change(state_vscode, state_chrome)
        self.assertTrue(diff.has_meaningful_change)
        self.assertTrue(diff.window_changed)
        self.assertTrue(diff.requires_vision_inference)

    def test_region_modification_triggers_inference(self):
        """Test semantic modification of subregion triggers vision inspection."""
        r1_old = ScreenRegion("reg_editor", 0, 0, 800, 600, "hash_clean_code")
        r1_new = ScreenRegion("reg_editor", 0, 0, 800, 600, "hash_with_traceback_error")
        
        state_old = ScreenState("Visual Studio Code", "Code.exe", "hash_old", (r1_old,))
        state_new = ScreenState("Visual Studio Code", "Code.exe", "hash_new", (r1_new,))
        
        diff = ChangeDetectionEngine.evaluate_screen_change(state_old, state_new)
        self.assertTrue(diff.has_meaningful_change)
        self.assertTrue(diff.requires_vision_inference)
        self.assertIn("reg_editor", diff.changed_region_ids)


if __name__ == "__main__":
    unittest.main()
