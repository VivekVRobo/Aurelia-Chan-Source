"""
Aurelia Cognitive OS V6 - Phase 4 Scene Graph Test Suite
=========================================================
Tests accessibility tree parsing and symbolic UI scene graph compilation.
"""

import unittest
from aurelia.screen.scene_graph import (
    UINode,
    UIEdge,
    UISceneGraph,
    SceneGraphCompiler,
    UIRelationType
)


class TestV6Phase4SceneGraph(unittest.TestCase):
    """Test suite for Phase 4 Accessibility & Scene Graph."""

    def test_scene_graph_compilation_and_queries(self):
        """Test compiling accessibility elements into symbolic UI nodes."""
        raw_elements = [
            {
                "id": "editor_01",
                "type": "CodeEditor",
                "label": "aurelia/runtime/cognitive_runtime.py",
                "bbox": (100, 100, 1200, 800),
                "is_active": True,
                "value": "def process_query(...):"
            },
            {
                "id": "btn_run",
                "type": "Button",
                "label": "Run Tests",
                "bbox": (1320, 100, 100, 40),
                "is_active": False
            }
        ]
        
        sg = SceneGraphCompiler.compile_from_accessibility(
            app_name="Visual Studio Code",
            window_title="Aurelia-Chan - Visual Studio Code",
            elements=raw_elements
        )
        
        self.assertEqual(sg.application_name, "Visual Studio Code")
        self.assertEqual(len(sg.nodes), 3) # root_window + 2 elements
        
        # Test finding nodes by type
        editors = sg.find_nodes_by_type("CodeEditor")
        self.assertEqual(len(editors), 1)
        self.assertEqual(editors[0].label, "aurelia/runtime/cognitive_runtime.py")
        
        # Test active nodes
        active = sg.get_active_nodes()
        active_ids = {n.node_id for n in active}
        self.assertIn("editor_01", active_ids)
        self.assertIn("root_window", active_ids)
        
        # Test edges
        edge_relations = {e.relation for e in sg.edges if e.to_node_id == "editor_01"}
        self.assertIn(UIRelationType.CONTAINS, edge_relations)
        self.assertIn(UIRelationType.ACTIVE, edge_relations)


if __name__ == "__main__":
    unittest.main()
