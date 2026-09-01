"""
Aurelia Cognitive OS V6 - Multimodal Contradiction & Severity Engine
====================================================================
Cross-validates multi-source observations and classifies detected discrepancies
into COSMETIC, MINOR, MATERIAL, and CRITICAL severities without silent override.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from aurelia.contracts.v6_contracts import ConflictSeverity


@dataclass(frozen=True)
class PerceptualConflict:
    """Detected discrepancy between two evidence sources."""
    conflict_id: str
    entity_type: str
    source_a_label: str
    source_a_value: Any
    source_b_label: str
    source_b_value: Any
    severity: ConflictSeverity
    explanation: str
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class MultimodalContradictionEngine:
    """
    Evaluates conflicting assertions across screen, documents, and speech.
    """

    @classmethod
    def evaluate_conflict(
        cls,
        entity_type: str,
        source_a_label: str,
        val_a: Any,
        source_b_label: str,
        val_b: Any
    ) -> Optional[PerceptualConflict]:
        """
        Detects discrepancy and computes conflict severity.
        """
        # If values match exactly, no conflict
        if val_a == val_b:
            return None

        cid = f"conf_{entity_type.lower()}"

        # 1. Compensation numerical discrepancy
        if entity_type == "COMPENSATION_AMOUNT":
            num_a = float(val_a)
            num_b = float(val_b)
            delta_pct = abs(num_a - num_b) / max(num_a, num_b)

            if delta_pct < 0.05:
                sev = ConflictSeverity.COSMETIC
            elif delta_pct < 0.15:
                sev = ConflictSeverity.MINOR
            else:
                sev = ConflictSeverity.MATERIAL # e.g. ₹28L vs ₹38L

            return PerceptualConflict(
                conflict_id=cid,
                entity_type=entity_type,
                source_a_label=source_a_label,
                source_a_value=val_a,
                source_b_label=source_b_label,
                source_b_value=val_b,
                severity=sev,
                explanation=f"Compensation mismatch: {source_a_label} specifies {val_a} while {source_b_label} specifies {val_b} ({delta_pct*100:.1f}% divergence)."
            )

        # 2. Date / Day Conflict (e.g. Thursday vs Wednesday)
        if entity_type in ["INTERVIEW_DATE", "DEADLINE_DATE"]:
            return PerceptualConflict(
                conflict_id=cid,
                entity_type=entity_type,
                source_a_label=source_a_label,
                source_a_value=val_a,
                source_b_label=source_b_label,
                source_b_value=val_b,
                severity=ConflictSeverity.CRITICAL,
                explanation=f"Temporal interview conflict: {source_a_label} shows '{val_a}' but {source_b_label} indicates '{val_b}'. Immediate clarification required."
            )

        # 3. Team size
        if entity_type == "TEAM_SIZE":
            delta = abs(int(val_a) - int(val_b))
            sev = ConflictSeverity.MINOR if delta <= 2 else ConflictSeverity.MATERIAL
            return PerceptualConflict(
                conflict_id=cid,
                entity_type=entity_type,
                source_a_label=source_a_label,
                source_a_value=val_a,
                source_b_label=source_b_label,
                source_b_value=val_b,
                severity=sev,
                explanation=f"Team size mismatch: {source_a_label} ({val_a}) vs {source_b_label} ({val_b})."
            )

        # Generic default mismatch
        return PerceptualConflict(
            conflict_id=cid,
            entity_type=entity_type,
            source_a_label=source_a_label,
            source_a_value=val_a,
            source_b_label=source_b_label,
            source_b_value=val_b,
            severity=ConflictSeverity.MINOR,
            explanation=f"Discrepancy detected between {source_a_label} ({val_a}) and {source_b_label} ({val_b})."
        )
