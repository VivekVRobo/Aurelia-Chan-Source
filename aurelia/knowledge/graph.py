"""
Aurelia Cognitive OS V4 - Temporal Career Knowledge Graph V2
=============================================================
Graph representations of roles, competencies, skills, compensation bands,
and historical facts with explicit temporal validity (valid_from, valid_to).
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Set, Optional, Tuple, Any


class NodeType(Enum):
    PERSON = "person"
    ROLE = "role"
    SKILL = "skill"
    COMPETENCY = "competency"
    INDUSTRY = "industry"
    COMPENSATION_BAND = "compensation_band"
    COMPANY_STAGE = "company_stage"
    EVIDENCE = "evidence"


class EdgeType(Enum):
    PROGRESSES_TO = "progresses_to"        # Role -> Role
    REQUIRES = "requires"                  # Role -> Competency
    CONTRIBUTES_TO = "contributes_to"      # Skill -> Competency
    DEMONSTRATES = "demonstrates"          # Person -> Skill / Competency
    COMPENSATION_FOR = "compensation_for"  # Role -> CompensationBand
    CHANGES_VALUE_OF = "changes_value_of"  # CompanyStage -> Skill


@dataclass(frozen=True)
class TemporalEdge:
    """An edge in the career graph with temporal validity bounds."""
    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float = 1.0
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source_version: str = "canon_v4.0"
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_active_at(self, target_time: Optional[datetime] = None) -> bool:
        """Checks if this edge was active at a specific timestamp."""
        check_time = target_time or datetime.now(timezone.utc)
        if self.valid_from and check_time < self.valid_from:
            return False
        if self.valid_to and check_time > self.valid_to:
            return False
        return True


@dataclass(frozen=True)
class KnowledgeNode:
    """A node in the career knowledge graph."""
    id: str
    node_type: NodeType
    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)


class TemporalCareerGraph:
    """
    Career knowledge graph enabling symbolic graph search, pathfinding,
    and temporal relationship queries.
    """

    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: Dict[str, List[TemporalEdge]] = {}  # source_id -> list of edges
        self._populate_canonical_ontology()

    def add_node(self, node: KnowledgeNode) -> None:
        self.nodes[node.id] = node
        if node.id not in self.edges:
            self.edges[node.id] = []

    def add_edge(self, edge: TemporalEdge) -> None:
        if edge.source_id not in self.edges:
            self.edges[edge.source_id] = []
        self.edges[edge.source_id].append(edge)

    def get_neighbors(
        self,
        node_id: str,
        edge_type: Optional[EdgeType] = None,
        at_time: Optional[datetime] = None
    ) -> List[Tuple[KnowledgeNode, TemporalEdge]]:
        """Finds valid active neighbors matching edge type and temporal bounds."""
        results = []
        for edge in self.edges.get(node_id, []):
            if edge_type and edge.edge_type != edge_type:
                continue
            if not edge.is_active_at(at_time):
                continue
            target_node = self.nodes.get(edge.target_id)
            if target_node:
                results.append((target_node, edge))
        return results

    def find_progression_path(self, from_role_id: str, to_role_id: str) -> Optional[List[str]]:
        """Finds canonical career stepping-stone path using BFS."""
        if from_role_id not in self.nodes or to_role_id not in self.nodes:
            return None
        if from_role_id == to_role_id:
            return [from_role_id]

        queue = [[from_role_id]]
        visited = {from_role_id}

        while queue:
            path = queue.pop(0)
            current = path[-1]

            if current == to_role_id:
                return path

            for neighbor, _ in self.get_neighbors(current, EdgeType.PROGRESSES_TO):
                if neighbor.id not in visited:
                    visited.add(neighbor.id)
                    queue.append(path + [neighbor.id])

        return None

    def _populate_canonical_ontology(self) -> None:
        """Seed graph with canonical executive career paths."""
        # Roles
        roles = [
            ("role_swe", "Software Engineer"),
            ("role_senior_swe", "Senior Software Engineer"),
            ("role_staff_swe", "Staff Software Engineer"),
            ("role_em", "Engineering Manager"),
            ("role_senior_em", "Senior Engineering Manager"),
            ("role_director", "Director of Engineering"),
            ("role_vp_eng", "VP of Engineering"),
            ("role_cto", "Chief Technology Officer")
        ]
        for r_id, r_name in roles:
            self.add_node(KnowledgeNode(id=r_id, node_type=NodeType.ROLE, name=r_name))

        # Progression Paths
        progressions = [
            ("role_swe", "role_senior_swe"),
            ("role_senior_swe", "role_staff_swe"),
            ("role_senior_swe", "role_em"),
            ("role_em", "role_senior_em"),
            ("role_staff_swe", "role_senior_em"),
            ("role_senior_em", "role_director"),
            ("role_director", "role_vp_eng"),
            ("role_vp_eng", "role_cto")
        ]
        for src, tgt in progressions:
            self.add_edge(TemporalEdge(source_id=src, target_id=tgt, edge_type=EdgeType.PROGRESSES_TO))
