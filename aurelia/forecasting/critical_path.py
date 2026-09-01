"""
Aurelia Cognitive OS V5 - Critical Path Method (CPM) for Career Goals
======================================================================
Applies deterministic project-management Critical Path graph algorithms
to determine which competency gap currently governs the goal timeline.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Set, Tuple, Optional
from aurelia.contracts.v5_contracts import CriticalPathNode


@dataclass
class PrerequisiteDependency:
    """Directed edge in the competency prerequisite graph."""
    from_node: str
    to_node: str


class CriticalPathEngine:
    """
    Computes Critical Path (zero slack) across career prerequisites.
    """

    @classmethod
    def compute_critical_path(
        cls,
        competencies: Dict[str, Dict[str, float]], # id -> {current, target, weeks_needed}
        dependencies: List[PrerequisiteDependency]
    ) -> Tuple[Dict[str, CriticalPathNode], str]:
        """
        Calculates ES, EF, LS, LF, Slack, and returns (node_dict, bottleneck_id).
        """
        nodes: Dict[str, CriticalPathNode] = {}
        
        # 1. Initialize nodes and forward pass (Earliest Start / Finish)
        earliest_start: Dict[str, float] = {k: 0.0 for k in competencies}
        earliest_finish: Dict[str, float] = {}

        # Build adjacency maps
        predecessors: Dict[str, List[str]] = {k: [] for k in competencies}
        successors: Dict[str, List[str]] = {k: [] for k in competencies}
        
        for dep in dependencies:
            if dep.from_node in competencies and dep.to_node in competencies:
                predecessors[dep.to_node].append(dep.from_node)
                successors[dep.from_node].append(dep.to_node)

        # Topological forward pass
        for node_id, data in competencies.items():
            preds = predecessors[node_id]
            if preds:
                es = max(earliest_finish.get(p, 0.0) for p in preds)
            else:
                es = 0.0
            earliest_start[node_id] = es
            dur = max(1.0, data.get("weeks_needed", 4.0))
            earliest_finish[node_id] = es + dur

        max_project_week = max(earliest_finish.values()) if earliest_finish else 1.0

        # Backward pass (Latest Start / Finish)
        latest_finish: Dict[str, float] = {k: max_project_week for k in competencies}
        latest_start: Dict[str, float] = {}

        for node_id in reversed(list(competencies.keys())):
            succs = successors[node_id]
            dur = max(1.0, competencies[node_id].get("weeks_needed", 4.0))
            if succs:
                lf = min(latest_start.get(s, max_project_week) for s in succs)
            else:
                lf = max_project_week
            latest_finish[node_id] = lf
            latest_start[node_id] = lf - dur

        # Calculate Slack and identify Critical Path
        critical_bottleneck = ""
        max_duration_on_cp = -1.0

        for node_id, data in competencies.items():
            es = earliest_start[node_id]
            lf = latest_finish[node_id]
            dur = max(1.0, data.get("weeks_needed", 4.0))
            slack = round(lf - es - dur, 2)
            is_cp = (slack <= 0.05)

            nodes[node_id] = CriticalPathNode(
                node_id=node_id,
                name=data.get("name", node_id),
                estimated_weeks=dur,
                current_score=data.get("current", 2.0),
                target_score=data.get("target", 4.0),
                is_on_critical_path=is_cp,
                earliest_start_week=es,
                latest_finish_week=lf,
                slack_weeks=max(0.0, slack)
            )

            if is_cp and dur > max_duration_on_cp:
                max_duration_on_cp = dur
                critical_bottleneck = data.get("name", node_id)

        return nodes, critical_bottleneck
