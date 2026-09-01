"""
Aurelia Cognitive OS V6 - Accessibility-First UI Scene Graph
============================================================
Compiles native accessibility trees and screen layouts into symbolic graph
representations with topological relationships (ABOVE, CONTAINS, ACTIVE).
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Set


class UIRelationType:
    CONTAINS = "CONTAINS"
    ABOVE = "ABOVE"
    BELOW = "BELOW"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    ACTIVE = "ACTIVE"


@dataclass(frozen=True)
class UINode:
    """Discrete UI element node in the scene graph."""
    node_id: str
    control_type: str # "Button", "InputField", "CodeEditor", "Dialog", "TextRegion", "Window"
    label: str
    bounding_box: Tuple[int, int, int, int] # (x, y, w, h)
    is_active: bool = False
    is_enabled: bool = True
    raw_value: Optional[str] = None


@dataclass(frozen=True)
class UIEdge:
    """Directed topological relation between two UI nodes."""
    from_node_id: str
    to_node_id: str
    relation: str # e.g. CONTAINS, ABOVE, ACTIVE


@dataclass(frozen=True)
class UISceneGraph:
    """Symbolic scene graph of the active user interface."""
    application_name: str
    window_title: str
    nodes: Tuple[UINode, ...]
    edges: Tuple[UIEdge, ...]
    root_node_id: str
    compiled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def get_node(self, node_id: str) -> Optional[UINode]:
        for n in self.nodes:
            if n.node_id == node_id:
                return n
        return None

    def find_nodes_by_type(self, control_type: str) -> List[UINode]:
        return [n for n in self.nodes if n.control_type.lower() == control_type.lower()]

    def get_active_nodes(self) -> List[UINode]:
        return [n for n in self.nodes if n.is_active]


class SceneGraphCompiler:
    """
    Compiles raw accessibility elements into a connected UISceneGraph.
    """

    @classmethod
    def compile_from_accessibility(
        cls,
        app_name: str,
        window_title: str,
        elements: List[Dict[str, Any]]
    ) -> UISceneGraph:
        """Constructs UISceneGraph from accessibility tree dicts."""
        nodes: List[UINode] = []
        edges: List[UIEdge] = []
        
        root_id = "root_window"
        root_node = UINode(
            node_id=root_id,
            control_type="Window",
            label=window_title,
            bounding_box=(0, 0, 1920, 1080),
            is_active=True
        )
        nodes.append(root_node)

        for el in elements:
            nid = el.get("id", f"node_{len(nodes)}")
            node = UINode(
                node_id=nid,
                control_type=el.get("type", "TextRegion"),
                label=el.get("label", ""),
                bounding_box=el.get("bbox", (0, 0, 100, 100)),
                is_active=el.get("is_active", False),
                is_enabled=el.get("is_enabled", True),
                raw_value=el.get("value")
            )
            nodes.append(node)
            edges.append(UIEdge(root_id, nid, UIRelationType.CONTAINS))
            if node.is_active:
                edges.append(UIEdge(root_id, nid, UIRelationType.ACTIVE))

        return UISceneGraph(
            application_name=app_name,
            window_title=window_title,
            nodes=tuple(nodes),
            edges=tuple(edges),
            root_node_id=root_id
        )
