"""
Aurelia Cognitive OS V5 - Event Significance & Proactive Autonomy Engine
========================================================================
Filters environmental events by strategic significance and enforces strict
proactivity policies with cooldowns and mandatory "Reason to Interrupt" explanations.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from aurelia.contracts.v5_contracts import EventSignificance, ProactiveAction


class EventSignificanceEngine:
    """
    Evaluates whether an event warrants proactive cognitive re-evaluation.
    """

    EVENT_PRIORS = {
        "SALARY_OFFER_RECEIVED": (0.95, 0.90, 0.90),      # (relevance, magnitude, novelty)
        "INTERVIEW_SCHEDULED": (0.90, 0.80, 0.85),
        "COMPETENCY_MILESTONE_MISSED": (0.85, 0.75, 0.70),
        "NEW_RESUME_UPLOADED": (0.80, 0.70, 0.75),
        "ROUTINE_CHAT_GREETING": (0.10, 0.10, 0.10)
    }

    @classmethod
    def evaluate_event(
        cls,
        event_type: str,
        custom_relevance: Optional[float] = None,
        custom_magnitude: Optional[float] = None,
        custom_novelty: Optional[float] = None
    ) -> EventSignificance:
        """Computes composite significance score for an event."""
        p_rel, p_mag, p_nov = cls.EVENT_PRIORS.get(event_type, (0.50, 0.50, 0.50))
        rel = custom_relevance if custom_relevance is not None else p_rel
        mag = custom_magnitude if custom_magnitude is not None else p_mag
        nov = custom_novelty if custom_novelty is not None else p_nov

        # Significance formula: S = 0.40*rel + 0.35*mag + 0.25*nov
        score = (0.40 * rel) + (0.35 * mag) + (0.25 * nov)
        requires_replan = (score >= 0.75)

        return EventSignificance(
            event_type=event_type,
            relevance_to_active_goal=round(rel, 3),
            magnitude=round(mag, 3),
            novelty=round(nov, 3),
            requires_replan=requires_replan,
            significance_score=round(score, 3)
        )


class ProactivityPolicy:
    """
    Enforces governance, cooldown periods, and mandatory 'Reason to Interrupt'.
    """

    def __init__(
        self,
        min_significance: float = 0.75,
        min_confidence: float = 0.70,
        cooldown_hours: float = 4.0
    ):
        self.min_significance = min_significance
        self.min_confidence = min_confidence
        self.cooldown_hours = cooldown_hours
        self.last_proactive_action_time: Optional[datetime] = None

    def should_proactively_interrupt(
        self,
        significance: EventSignificance,
        confidence: float,
        reason_to_interrupt: str,
        current_time: Optional[datetime] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Returns (is_approved, rejection_reason).
        """
        now = current_time or datetime.now(timezone.utc)

        # 1. Check Significance
        if significance.significance_score < self.min_significance:
            return False, f"Event significance ({significance.significance_score:.2f}) below threshold ({self.min_significance:.2f})"

        # 2. Check Confidence
        if confidence < self.min_confidence:
            return False, f"Confidence ({confidence:.2f}) below threshold ({self.min_confidence:.2f})"

        # 3. Check Mandatory 'Reason to Interrupt'
        if not reason_to_interrupt or len(reason_to_interrupt.strip()) < 15:
            return False, "Mandatory 'Reason to Interrupt' clause is missing or insufficient"

        # 4. Check Cooldown
        if self.last_proactive_action_time:
            elapsed_hours = (now - self.last_proactive_action_time).total_seconds() / 3600.0
            if elapsed_hours < self.cooldown_hours:
                return False, f"In cooldown period ({elapsed_hours:.1f}h < {self.cooldown_hours:.1f}h)"

        self.last_proactive_action_time = now
        return True, None
