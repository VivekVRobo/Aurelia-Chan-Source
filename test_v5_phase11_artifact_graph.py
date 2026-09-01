"""
Aurelia Cognitive OS V5 - Phase 11 Artifact Graph Test Suite
============================================================
Tests artifact-to-fact dependency DAG, staleness propagation, and revalidation.
"""

import unittest
from aurelia.artifacts.dependency_graph import ArtifactDependencyGraph
from aurelia.contracts.v5_contracts import StalenessStatus


class TestV5Phase11ArtifactGraph(unittest.TestCase):
    """Test suite for Phase 11 Artifact Graph & Staleness."""

    def test_staleness_propagation_on_fact_change(self):
        """Test that updating an upstream fact invalidates dependent artifacts."""
        graph = ArtifactDependencyGraph()
        
        # Artifact 1: 90-Day Roadmap (depends on team_size, target_role)
        graph.register_artifact(
            artifact_id="art_roadmap_90",
            title="Director 90-Day Roadmap",
            goal_id="g_dir",
            dependent_fact_keys={"team_size", "target_role"}
        )
        
        # Artifact 2: Compensation Script (depends on base_salary, equity_grant)
        graph.register_artifact(
            artifact_id="art_comp_script",
            title="Counter-Offer Negotiation Script",
            goal_id="g_dir",
            dependent_fact_keys={"base_salary", "equity_grant"}
        )
        
        # User modifies fact: team_size changes from 8 to 14
        affected = graph.trigger_fact_update(
            modified_fact_key="team_size",
            new_value=14,
            triggering_event_id="evt_user_profile_edit"
        )
        
        self.assertEqual(len(affected), 1)
        self.assertEqual(affected[0].artifact_id, "art_roadmap_90")
        self.assertEqual(affected[0].status, StalenessStatus.STALE)
        self.assertIn("team_size", affected[0].stale_reason)
        
        # Roadmap is now STALE, Comp Script remains FRESH
        self.assertEqual(graph.nodes["art_roadmap_90"].status, StalenessStatus.STALE)
        self.assertEqual(graph.nodes["art_comp_script"].status, StalenessStatus.FRESH)
        
        # Revalidate roadmap after revision
        success = graph.revalidate_artifact("art_roadmap_90")
        self.assertTrue(success)
        self.assertEqual(graph.nodes["art_roadmap_90"].status, StalenessStatus.FRESH)


if __name__ == "__main__":
    unittest.main()
