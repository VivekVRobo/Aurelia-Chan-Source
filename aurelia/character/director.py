"""
Aurelia Cognitive OS V4 - Character & Expression Director
==========================================================
Decouples persona rendering from analytical facts. Maps verified
cognitive states to the 11 canonical Aurelia expressions.
"""

from typing import Dict, Any, Optional
from aurelia.contracts.core_types import VerificationSeverity


class CharacterDirector:
    """
    Directs Aurelia's emotional affect and facial expression based on cognitive state.
    """

    EXPRESSION_MAP = {
        "neutral": ("01. Neutral / Observing", "01-neutral-observing.png"),
        "confident": ("02. Subtle Confident Smile", "02-subtle-confident-smile.png"),
        "approval": ("03. Soft Approval", "03-soft-approval.png"),
        "focused": ("04. Focused Listening", "04-focused-listening.png"),
        "analyzing": ("05. Analyzing (Raised Brow)", "05-analyzing-raised-brow.png"),
        "serious": ("06. Serious", "06-serious.png"),
        "warning": ("07. Strict Warning", "07-strict-warning.png"),
        "disappointed": ("08. Disappointed", "08-disappointed.png"),
        "skeptical": ("09. Skeptical", "09-skeptical.png"),
        "concerned": ("10. Concerned", "10-concerned.png"),
        "empathetic": ("11. Empathetic", "11-empathetic.png"),
    }

    @classmethod
    def resolve_expression(
        cls,
        cognitive_state: str,              # e.g., "ANALYZING", "BLOCKER", "VERIFIED_HIGH_VALUE", "ENTITLEMENT_WARNING"
        verification_severity: VerificationSeverity = VerificationSeverity.INFO,
        user_sentiment: str = "neutral"
    ) -> str:
        """
        Deterministically resolves the canonical expression key.
        """
        # Blockers or severe errors always trigger Warning or Disappointed
        if verification_severity == VerificationSeverity.BLOCKER:
            return "warning"
        if verification_severity == VerificationSeverity.ERROR:
            return "serious"
            
        state_upper = cognitive_state.upper()
        
        if "WARNING" in state_upper or "ENTITLED" in state_upper:
            return "warning"
        elif "DISAPPOINTED" in state_upper or "UNPREPARED" in state_upper:
            return "disappointed"
        elif "SKEPTICAL" in state_upper or "UNVERIFIED" in state_upper:
            return "skeptical"
        elif "BURNOUT" in state_upper or "CONCERNED" in state_upper:
            return "concerned"
        elif "ANALYZING" in state_upper or "CALCULATING" in state_upper:
            return "analyzing"
        elif "SERIOUS" in state_upper or "REORG" in state_upper:
            return "serious"
        elif "APPROVAL" in state_upper or "HIGH_METRIC" in state_upper:
            return "approval"
        elif "CONFIDENT" in state_upper or "VERIFIED_PLAN" in state_upper:
            return "confident"
        elif "EMPATHETIC" in state_upper or "PIVOT" in state_upper:
            return "empathetic"
        elif "LISTENING" in state_upper:
            return "focused"
            
        return "neutral"
