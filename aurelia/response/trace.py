"""
Aurelia Cognitive OS V4 - Safe Structured Cognitive Trace
==========================================================
Generates user-facing structured audit traces of system intelligence.
Absolute Invariant: Raw model thought tokens (<think>...</think>) are NEVER exposed.
Instead, Aurelia reveals exact understanding, evidence used, systems invoked,
alternatives evaluated, calculations verified, and explicit confidence.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any


@dataclass(frozen=True)
class SafeCognitiveTrace:
    """
    Structured, user-verifiable trace of Aurelia's analysis.
    """
    understood_goal: str
    memories_retrieved_count: int
    graph_facts_count: int
    specialists_invoked: Tuple[str, ...]
    alternatives_evaluated: Tuple[str, ...]
    numerical_calculations_verified: Tuple[str, ...]
    unresolved_unknowns: Tuple[str, ...]
    contradictions_detected: int
    confidence_percentage: float
    confidence_level: str                # "High", "Moderate-High", "Cautious", "Low"

    def to_formatted_summary(self) -> str:
        """Renders the standard summary block for UI."""
        lines = [
            "### 🧠 Aurelia's Analysis",
            f"✓ Understood: {self.understood_goal}",
            f"✓ Retrieved {self.memories_retrieved_count} relevant memories & {self.graph_facts_count} graph facts",
            f"✓ Specialists Invoked: {', '.join(self.specialists_invoked)}",
            f"✓ Evaluated {len(self.alternatives_evaluated)} strategic alternatives",
            f"✓ Verified {len(self.numerical_calculations_verified)} numerical calculations",
        ]
        if self.unresolved_unknowns:
            lines.append(f"⚠ Unknown Variables: {', '.join(self.unresolved_unknowns)}")
        if self.contradictions_detected > 0:
            lines.append(f"⚠ Contradictions: {self.contradictions_detected}")
            
        lines.append(f"**Confidence: {self.confidence_percentage:.0f}% ({self.confidence_level})**")
        return "\n".join(lines)
