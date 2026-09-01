"""
Aurelia Cognitive OS V5 - Phase 5 Strategic Insights Test Suite
================================================================
Tests durable insight tracking, evidence reinforcement, and temporal freshness decay.
"""

import unittest
from datetime import datetime, timezone, timedelta
from aurelia.learning.insight_engine import StrategicInsightEngine
from aurelia.contracts.v5_contracts import StrategicInsight


class TestV5Phase5InsightsAndDecay(unittest.TestCase):
    """Test suite for Phase 5 Insights and Decay."""

    def test_insight_validation_and_receipt(self):
        """Test evidence reinforcement and LearningReceipt generation."""
        engine = StrategicInsightEngine()
        
        # 1. Record insight
        ins = engine.record_insight(
            insight_id="ins_01",
            claim="Active simulation practice produces higher interview retention.",
            category="interview_strategy",
            initial_confidence=0.75
        )
        self.assertEqual(ins.evidence_count, 1)
        
        # 2. Validate with new evidence
        updated, receipt = engine.validate_insight(
            insight_id="ins_01",
            supporting_evidence_ref="session_mock_402",
            confidence_boost=0.05
        )
        self.assertEqual(updated.evidence_count, 2)
        self.assertEqual(updated.confidence, 0.80)
        self.assertEqual(receipt.insight_or_belief_id, "ins_01")
        self.assertEqual(receipt.confidence_delta, 0.05)

    def test_stale_insight_decay_and_deactivation(self):
        """Test decay and deactivation of unvalidated legacy insights."""
        engine = StrategicInsightEngine()
        now = datetime.now(timezone.utc)
        
        # Insight with 90-day half-life created 365 days ago (4 half-lives = ~0.0625 freshness)
        ins = engine.record_insight(
            insight_id="ins_legacy",
            claim="Legacy hiring preference for monolithic languages.",
            category="market_trends",
            initial_confidence=0.80,
            decay_half_life_days=90.0
        )
        # Artificially age the last_validated date
        engine.insights["ins_legacy"] = StrategicInsight(
            insight_id=ins.insight_id,
            claim=ins.claim,
            category=ins.category,
            evidence_count=1,
            confidence=0.80,
            first_observed=now - timedelta(days=365),
            last_validated=now - timedelta(days=365),
            decay_half_life_days=90.0,
            is_active=True
        )
        
        deactivated = engine.sweep_stale_insights(current_time=now, freshness_threshold=0.25)
        self.assertIn("ins_legacy", deactivated)
        self.assertFalse(engine.insights["ins_legacy"].is_active)


if __name__ == "__main__":
    unittest.main()
