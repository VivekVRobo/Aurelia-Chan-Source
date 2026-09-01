"""Ground runtime context in actual memory and career-graph facts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from aurelia.contracts.core_types import UserGoal
from aurelia.knowledge.career_graph import CareerGraph, create_sample_career_graph
from aurelia.memory.retrieval import HybridMemoryRetriever, RetrievedMemoryItem


@dataclass(frozen=True)
class GroundedContext:
    """Context actually retrieved for a cognitive cycle."""

    memories: tuple[RetrievedMemoryItem, ...]
    graph_facts: tuple[str, ...]
    corroborating_evidence_count: int

    @property
    def has_corroborating_evidence(self) -> bool:
        """Return whether retrieved context contains corroborating evidence."""
        return self.corroborating_evidence_count > 0

    def render_for_model(self) -> str:
        """Render only context that was actually retrieved."""
        sections: list[str] = []
        if self.memories:
            memory_lines = [f"- {item.content}" for item in self.memories]
            sections.append("Retrieved memory context:\n" + "\n".join(memory_lines))
        if self.graph_facts:
            graph_lines = [f"- {fact}" for fact in self.graph_facts]
            sections.append("Career graph context:\n" + "\n".join(graph_lines))
        return "\n\n".join(sections)


class RuntimeGrounder:
    """Build truthful runtime context without fabricated trace counters."""

    def __init__(self, career_graph: CareerGraph | None = None) -> None:
        self._career_graph = career_graph or create_sample_career_graph()

    def build(
        self,
        *,
        user_text: str,
        entities: dict[str, Any],
        user_role: str,
        target_role: str,
        active_goal: UserGoal,
        chat_history: list[dict[str, str]] | None,
        persistent_candidates: list[dict[str, Any]] | None = None,
        top_k: int,
    ) -> GroundedContext:
        now = datetime.now(UTC)
        candidates = list(persistent_candidates or ())
        candidates.extend(self._history_candidates(user_text, chat_history, now))
        query_entities = self._query_entities(entities, user_role, target_role)
        memories = HybridMemoryRetriever.retrieve(
            query_text=user_text,
            query_entities=query_entities,
            active_goal=active_goal,
            candidate_items=candidates,
            now=now,
            top_k=max(0, top_k),
        )

        graph_facts = self._graph_facts(user_role, target_role)
        corroborating = sum(1 for item in memories if item.evidence_quality >= 0.85)
        return GroundedContext(
            memories=tuple(memories),
            graph_facts=tuple(graph_facts),
            corroborating_evidence_count=corroborating,
        )

    @staticmethod
    def _history_candidates(
        user_text: str,
        chat_history: list[dict[str, str]] | None,
        now: datetime,
    ) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []
        history = chat_history or []
        for index, turn in enumerate(history):
            role = str(turn.get("role", "unknown"))
            content = str(turn.get("content", "")).strip()
            if not content:
                continue
            if index == len(history) - 1 and role == "user" and content == user_text:
                continue

            # Chat history is useful context, but it is not corroborated evidence.
            reliability = 0.40 if role == "user" else 0.20
            candidates.append(
                {
                    "id": f"chat_{index}",
                    "content": content,
                    "timestamp": now,
                    "reliability_weight": reliability,
                    "source_type": f"chat_{role}",
                }
            )
        return candidates

    @staticmethod
    def _query_entities(
        entities: dict[str, Any],
        user_role: str,
        target_role: str,
    ) -> list[str]:
        values: list[str] = [user_role, target_role]
        for value in entities.values():
            if isinstance(value, (str, int, float)):
                values.append(str(value))
            elif isinstance(value, (list, tuple)):
                values.extend(str(item) for item in value)
        return [value for value in values if value]

    def _graph_facts(self, user_role: str, target_role: str) -> list[str]:
        facts: list[str] = []
        path = self._career_graph.get_shortest_path(user_role, target_role)
        if path:
            facts.append("Career progression path: " + " -> ".join(path))

        required_skills = self._career_graph.get_required_skills(target_role)
        facts.extend(f"{target_role} requires {skill}" for skill in required_skills)
        return facts
