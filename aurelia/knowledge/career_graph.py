"""
Aurelia Cognitive OS V3 - Phase 2: Career Knowledge Graph
=========================================================
Career role relationships, progression paths, and skill requirements.

Graph algorithms can answer many career questions more reliably
than a language model.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from enum import Enum
import copy


class EdgeType(Enum):
    """Types of relationships in the career graph."""
    PROGRESSES_TO = "progresses_to"  # Role A → Role B (career progression)
    REQUIRES = "requires"  # Role → Skill (skill requirement)
    COMMON_IN = "common_in"  # Role → Industry (industry context)
    COMPENSATION_BAND = "compensation_band"  # Role → Salary range


@dataclass
class Node:
    """A node in the career graph (role, skill, industry, etc.)."""
    id: str
    type: str  # "role", "skill", "industry", "market_segment"
    attributes: Dict[str, any] = field(default_factory=dict)


@dataclass
class Edge:
    """An edge in the career graph."""
    source: str
    target: str
    edge_type: EdgeType
    weight: float = 1.0
    attributes: Dict[str, any] = field(default_factory=dict)


class CareerGraph:
    """
    Career knowledge graph representing roles, skills, and relationships.
    
    Enables graph-based career path analysis instead of LLM guessing.
    """
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, List[Edge]] = {}  # source_id -> list of edges
        self.adjacency: Dict[str, Set[str]] = {}  # source_id -> set of target_ids
    
    def add_node(self, node: Node):
        """Add a node to the graph."""
        self.nodes[node.id] = node
        if node.id not in self.edges:
            self.edges[node.id] = []
        if node.id not in self.adjacency:
            self.adjacency[node.id] = set()
    
    def add_edge(self, edge: Edge):
        """Add an edge to the graph."""
        if edge.source not in self.edges:
            self.edges[edge.source] = []
        if edge.source not in self.adjacency:
            self.adjacency[edge.source] = set()
        
        self.edges[edge.source].append(edge)
        self.adjacency[edge.source].add(edge.target)
    
    def get_neighbors(self, node_id: str, edge_type: Optional[EdgeType] = None) -> List[str]:
        """Get neighbors of a node, optionally filtered by edge type."""
        if node_id not in self.adjacency:
            return []
        
        if edge_type is None:
            return list(self.adjacency[node_id])
        
        neighbors = []
        for edge in self.edges.get(node_id, []):
            if edge.edge_type == edge_type:
                neighbors.append(edge.target)
        return neighbors
    
    def get_shortest_path(self, start: str, end: str) -> Optional[List[str]]:
        """Find shortest path between two nodes using BFS."""
        if start not in self.nodes or end not in self.nodes:
            return None
        
        if start == end:
            return [start]
        
        from collections import deque
        
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            current, path = queue.popleft()
            
            for neighbor in self.adjacency.get(current, []):
                if neighbor == end:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def get_all_paths(self, start: str, end: str, max_length: int = 5) -> List[List[str]]:
        """Get all paths between two nodes up to max_length."""
        if start not in self.nodes or end not in self.nodes:
            return []
        
        paths = []
        
        def dfs(current: str, path: List[str], visited: Set[str]):
            if len(path) > max_length:
                return
            
            if current == end:
                paths.append(path.copy())
                return
            
            for neighbor in self.adjacency.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    dfs(neighbor, path + [neighbor], visited)
                    visited.remove(neighbor)
        
        dfs(start, [start], {start})
        return paths
    
    def get_required_skills(self, role_id: str) -> List[str]:
        """Get all skills required for a role."""
        return self.get_neighbors(role_id, EdgeType.REQUIRES)
    
    def get_progression_options(self, role_id: str) -> List[str]:
        """Get all roles this role can progress to."""
        return self.get_neighbors(role_id, EdgeType.PROGRESSES_TO)


def create_sample_career_graph() -> CareerGraph:
    """
    Create a sample career graph with engineering progression paths.
    
    This demonstrates the graph structure. In production, this would
    be loaded from a database or configuration file.
    """
    graph = CareerGraph()
    
    # Add role nodes
    roles = [
        Node("Software Engineer", "role", {"level": "Individual Contributor", "seniority": 1}),
        Node("Senior Software Engineer", "role", {"level": "Individual Contributor", "seniority": 2}),
        Node("Staff Software Engineer", "role", {"level": "Individual Contributor", "seniority": 3}),
        Node("Engineering Manager", "role", {"level": "Management", "seniority": 2}),
        Node("Senior Engineering Manager", "role", {"level": "Management", "seniority": 3}),
        Node("Director of Engineering", "role", {"level": "Executive", "seniority": 4}),
        Node("VP of Engineering", "role", {"level": "Executive", "seniority": 5}),
    ]
    
    for role in roles:
        graph.add_node(role)
    
    # Add skill nodes
    skills = [
        Node("Team Leadership", "skill", {"category": "leadership"}),
        Node("Strategic Planning", "skill", {"category": "strategic"}),
        Node("Budget Ownership", "skill", {"category": "strategic"}),
        Node("Cross-functional Influence", "skill", {"category": "strategic"}),
        Node("Executive Communication", "skill", {"category": "communication"}),
        Node("Software Architecture", "skill", {"category": "technical"}),
        Node("System Design", "skill", {"category": "technical"}),
    ]
    
    for skill in skills:
        graph.add_node(skill)
    
    # Add progression edges (career paths)
    progressions = [
        Edge("Software Engineer", "Senior Software Engineer", EdgeType.PROGRESSES_TO),
        Edge("Senior Software Engineer", "Staff Software Engineer", EdgeType.PROGRESSES_TO),
        Edge("Senior Software Engineer", "Engineering Manager", EdgeType.PROGRESSES_TO),
        Edge("Staff Software Engineer", "Director of Engineering", EdgeType.PROGRESSES_TO),
        Edge("Engineering Manager", "Senior Engineering Manager", EdgeType.PROGRESSES_TO),
        Edge("Senior Engineering Manager", "Director of Engineering", EdgeType.PROGRESSES_TO),
        Edge("Director of Engineering", "VP of Engineering", EdgeType.PROGRESSES_TO),
    ]
    
    for edge in progressions:
        graph.add_edge(edge)
    
    # Add skill requirement edges
    skill_requirements = [
        # Engineering Manager requirements
        Edge("Engineering Manager", "Team Leadership", EdgeType.REQUIRES, weight=3),
        
        # Senior Engineering Manager requirements
        Edge("Senior Engineering Manager", "Team Leadership", EdgeType.REQUIRES, weight=4),
        Edge("Senior Engineering Manager", "Strategic Planning", EdgeType.REQUIRES, weight=3),
        
        # Director requirements
        Edge("Director of Engineering", "Team Leadership", EdgeType.REQUIRES, weight=4),
        Edge("Director of Engineering", "Strategic Planning", EdgeType.REQUIRES, weight=4),
        Edge("Director of Engineering", "Budget Ownership", EdgeType.REQUIRES, weight=3),
        Edge("Director of Engineering", "Cross-functional Influence", EdgeType.REQUIRES, weight=4),
        Edge("Director of Engineering", "Executive Communication", EdgeType.REQUIRES, weight=4),
        
        # VP requirements
        Edge("VP of Engineering", "Strategic Planning", EdgeType.REQUIRES, weight=5),
        Edge("VP of Engineering", "Budget Ownership", EdgeType.REQUIRES, weight=5),
        Edge("VP of Engineering", "Cross-functional Influence", EdgeType.REQUIRES, weight=5),
        Edge("VP of Engineering", "Executive Communication", EdgeType.REQUIRES, weight=5),
    ]
    
    for edge in skill_requirements:
        graph.add_edge(edge)
    
    return graph


def analyze_career_path(graph: CareerGraph, current_role: str, target_role: str) -> Dict[str, any]:
    """
    Analyze career path from current to target role.
    
    Returns structured analysis including:
    - Available paths
    - Required skills for each path
    - Skill gaps
    """
    paths = graph.get_all_paths(current_role, target_role, max_length=5)
    
    if not paths:
        return {
            "status": "no_path_found",
            "message": f"No direct career path found from {current_role} to {target_role}"
        }
    
    analysis = {
        "status": "success",
        "current_role": current_role,
        "target_role": target_role,
        "paths": []
    }
    
    for path in paths:
        path_analysis = {
            "path": path,
            "steps": len(path) - 1,
            "required_skills": set(),
            "skill_gaps": []
        }
        
        # Collect required skills for all roles in path
        for role in path[1:]:  # Skip current role
            required = graph.get_required_skills(role)
            path_analysis["required_skills"].update(required)
        
        # For now, skill gaps would be calculated against user's current skills
        # This would be integrated with the user model in the full system
        path_analysis["required_skills"] = list(path_analysis["required_skills"])
        
        analysis["paths"].append(path_analysis)
    
    return analysis