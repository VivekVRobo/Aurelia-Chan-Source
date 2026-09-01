"""
Aurelia Cognitive OS V4 - Phase 7 Artifact Workspace Test Suite
================================================================
Tests Executive Artifact compilation, causal lineage, delta-updates, and rendering.
"""

import unittest
from aurelia.artifacts.schemas import ExecutiveArtifact, ArtifactMilestone, ArtifactType, ArtifactWorkspaceCompiler
from aurelia.artifacts.renderer import ArtifactRenderer


class TestPhase7Artifacts(unittest.TestCase):
    """Test suite for Phase 7 Artifact Workspace."""

    def test_artifact_compilation_and_lineage(self):
        """Test artifact creation with causal lineage."""
        m1 = ArtifactMilestone(
            id="m_d30",
            phase_name="Days 1-30",
            goal="Organizational Audit & Sponsor Mapping",
            actions=("Interview 12 department heads", "Audit cloud budget"),
            deliverables=("30-day executive findings dossier",)
        )
        m2 = ArtifactMilestone(
            id="m_d60",
            phase_name="Days 31-60",
            goal="Strategy Alignment & Quick Wins",
            actions=("Deploy initial latency fix",),
            deliverables=("15% latency reduction report",)
        )
        
        art_v1 = ArtifactWorkspaceCompiler.create_90_day_roadmap(
            artifact_id="art_roadmap_101",
            title="Executive VP 90-Day Transition Blueprint",
            decision_id="dec_42",
            milestones=[m1, m2]
        )
        
        self.assertEqual(art_v1.version, 1)
        self.assertEqual(art_v1.created_from_decision_id, "dec_42")
        self.assertIsNone(art_v1.updated_from_event_id)
        self.assertEqual(len(art_v1.payload["milestones"]), 2)
        self.assertFalse(art_v1.payload["milestones"][0]["is_completed"])

        # Test Delta-Update (marking Day 1-30 completed)
        art_v2 = ArtifactWorkspaceCompiler.update_milestone_status(
            existing=art_v1,
            milestone_id="m_d30",
            is_completed=True,
            event_id="evt_interview_07"
        )
        
        self.assertEqual(art_v2.version, 2)
        self.assertEqual(art_v2.created_from_decision_id, "dec_42")
        self.assertEqual(art_v2.updated_from_event_id, "evt_interview_07")
        self.assertTrue(art_v2.payload["milestones"][0]["is_completed"])
        self.assertFalse(art_v2.payload["milestones"][1]["is_completed"])

    def test_artifact_renderer_to_markdown(self):
        """Test rendering artifact to Markdown."""
        m1 = ArtifactMilestone(
            id="m_1",
            phase_name="Days 1-30",
            goal="Audit",
            actions=("Audit budget",),
            deliverables=("Report",),
            is_completed=True
        )
        art = ArtifactWorkspaceCompiler.create_90_day_roadmap("art_01", "Plan", "dec_1", [m1])
        # Mark completed in v2
        art_v2 = ArtifactWorkspaceCompiler.update_milestone_status(art, "m_1", True, "evt_1")
        
        md = ArtifactRenderer.to_markdown(art_v2)
        self.assertIn("# Plan (v2)", md)
        self.assertIn("### [x] Days 1-30: Audit", md)
        self.assertIn("- Audit budget", md)


if __name__ == "__main__":
    unittest.main()
