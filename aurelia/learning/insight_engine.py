"""
Aurelia Cognitive OS V5 - Strategic Insight & Temporal Freshness Engine
=======================================================================
Maintains durable, evidence-backed strategic insights, validates them
periodically, and applies exponential freshness decay to prevent obsolete beliefs.
"""

import time
import math
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from aurelia.contracts.v5_contracts import StrategicInsight, LearningReceipt


class StrategicInsightEngine:
    """
    Manages durable strategic insights with Bayesian validation and temporal decay.
    """

    def __init__(self):
        self.insights: Dict[str, StrategicInsight] = {}
        self.receipts: List[LearningReceipt] = []

    def record_insight(
        self,
        insight_id: str,
        claim: str,
        category: str,
        initial_confidence: float = 0.75,
        decay_half_life_days: float = 180.0
    ) -> StrategicInsight:
        """Registers a new strategic hypothesis or learned insight."""
        now = datetime.now(timezone.utc)
        insight = StrategicInsight(
            insight_id=insight_id,
            claim=claim,
            category=category,
            evidence_count=1,
            confidence=max(0.1, min(0.99, initial_confidence)),
            first_observed=now,
            last_validated=now,
            decay_half_life_days=decay_half_life_days,
            is_active=True
        )
        self.insights[insight_id] = insight
        return insight

    def validate_insight(
        self,
        insight_id: str,
        supporting_evidence_ref: str,
        confidence_boost: float = 0.05
    ) -> Tuple[StrategicInsight, LearningReceipt]:
        """
        Validates an existing insight with new evidence, refreshes last_validated,
        and increases confidence.
        """
        if insight_id not in self.insights:
            raise KeyError(f"Insight {insight_id} not found.")

        old = self.insights[insight_id]
        now = datetime.now(timezone.utc)
        new_conf = min(0.98, old.confidence + confidence_boost)

        updated = StrategicInsight(
            insight_id=old.insight_id,
            claim=old.claim,
            category=old.category,
            evidence_count=old.evidence_count + 1,
            confidence=round(new_conf, 3),
            first_observed=old.first_observed,
            last_validated=now,
            decay_half_life_days=old.decay_half_life_days,
            is_active=True
        )
        self.insights[insight_id] = updated

        receipt = LearningReceipt(
            receipt_id=f"lr_ins_{int(time.time()*1000)}",
            insight_or_belief_id=insight_id,
            previous_belief=f"Confidence {old.confidence:.2f} (evidence={old.evidence_count})",
            new_evidence_refs=(supporting_evidence_ref,),
            updated_belief=f"Confidence {updated.confidence:.2f} (evidence={updated.evidence_count})",
            update_method="Evidence_Validation_Reinforcement",
            confidence_delta=round(new_conf - old.confidence, 3)
        )
        self.receipts.append(receipt)
        return updated, receipt

    def sweep_stale_insights(
        self,
        current_time: Optional[datetime] = None,
        freshness_threshold: float = 0.25
    ) -> List[str]:
        """
        Evaluates freshness decay across all active insights; deactivates
        insights that have decayed below the threshold without validation.
        """
        now = current_time or datetime.now(timezone.utc)
        deactivated = []

        for i_id, ins in list(self.insights.items()):
            if not ins.is_active:
                continue
            freshness = ins.calculate_current_freshness(now)
            if freshness < freshness_threshold:
                # Deactivate decayed insight
                updated = StrategicInsight(
                    insight_id=ins.insight_id,
                    claim=ins.claim,
                    category=ins.category,
                    evidence_count=ins.evidence_count,
                    confidence=ins.confidence * freshness,
                    first_observed=ins.first_observed,
                    last_validated=ins.last_validated,
                    decay_half_life_days=ins.decay_half_life_days,
                    is_active=False
                )
                self.insights[i_id] = updated
                deactivated.append(i_id)

        return deactivated
