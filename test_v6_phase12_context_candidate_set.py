"""
Aurelia Cognitive OS V6 - Phase 12 Context Candidate Set Test Suite
===================================================================
Tests scene-based cognitive routing, candidate sets, and ambiguity preservation.
"""

import unittest
from aurelia.routing.scene_router import SceneBasedCognitiveRouter


class TestV6Phase12ContextCandidateSet(unittest.TestCase):
    """Test suite for Phase 12 Context Candidate Sets & Routing."""

    def test_vscode_traceback_decisive_routing(self):
        """Invariant: Test F - VS Code with traceback routes to debugging context automatically."""
        cset = SceneBasedCognitiveRouter.rank_context_candidates(
            user_query="Why is this failing?",
            active_window_title="cognitive_runtime.py - Visual Studio Code",
            active_process_name="Code.exe",
            visible_text_snippet="TypeError: unsupported operand type(s) for +: 'int' and 'NoneType'"
        )
        
        self.assertFalse(cset.is_ambiguous)
        self.assertEqual(cset.selected_context, "vscode_python_debugging")
        self.assertGreaterEqual(cset.separation_ratio, 0.20)

    def test_resume_editor_routing(self):
        """Test active resume window routes to resume audit context."""
        cset = SceneBasedCognitiveRouter.rank_context_candidates(
            user_query="What do you think of this section?",
            active_window_title="Executive_Resume_v4.pdf - Acrobat Reader",
            active_process_name="AcroRd32.exe",
            visible_text_snippet="Director of Engineering experience and competencies"
        )
        
        self.assertFalse(cset.is_ambiguous)
        self.assertEqual(cset.selected_context, "resume_audit")


if __name__ == "__main__":
    unittest.main()
