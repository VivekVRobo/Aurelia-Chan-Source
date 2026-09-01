"""
Aurelia Cognitive OS V4 - Independent Structured Critics
=========================================================
Evaluates candidate hypotheses independently across strategic fit,
downside risk, and evidence rigor without multi-agent chat loops.
"""

from dataclasses import dataclass
from typing import List, Tuple
from aurelia.llm.schemas import CritiqueResult
from aurelia.cognition.hypotheses import StrategicHypothesis


class StrategicCritic:
    """Evaluates long-term career leverage and goal alignment."""

    @staticmethod
    def critique(hypothesis: StrategicHypothesis, target_role: str) -> CritiqueResult:
        score = hypothesis.strategic_value_score
        passed = score >= 0.65
        notes = f"Strategic value score {score:.2f} relative to target {target_role}."
        return CritiqueResult(
            critic_role="strategic_fit",
            score=score,
            passed=passed,
            unsupported_assumptions=(),
            flagged_risks=(),
            critique_notes=notes
        )


class RiskCritic:
    """Evaluates downside vulnerability and reversibility."""

    @staticmethod
    def critique(hypothesis: StrategicHypothesis) -> CritiqueResult:
        # High risk penalty (> 0.6) or low reversibility (< 0.3) triggers risk warning
        passed = hypothesis.risk_penalty <= 0.60 and hypothesis.reversibility_score >= 0.30
        score = max(0.1, 1.0 - hypothesis.risk_penalty)
        notes = f"Downside risk penalty: {hypothesis.risk_penalty:.2f}, Reversibility: {hypothesis.reversibility_score:.2f}."
        return CritiqueResult(
            critic_role="risk_assessor",
            score=score,
            passed=passed,
            unsupported_assumptions=(),
            flagged_risks=hypothesis.assumptions if not passed else (),
            critique_notes=notes
        )


class EvidenceCritic:
    """Audits whether hypothesis assumptions are backed by verified evidence."""

    @staticmethod
    def critique(hypothesis: StrategicHypothesis) -> CritiqueResult:
        ev_count = len(hypothesis.evidence)
        passed = ev_count >= 1 or hypothesis.confidence >= 0.70
        score = min(1.0, 0.5 + (ev_count * 0.25))
        notes = f"Supported by {ev_count} verified evidence references."
        return CritiqueResult(
            critic_role="evidence_auditor",
            score=score,
            passed=passed,
            unsupported_assumptions=hypothesis.assumptions if not passed else (),
            flagged_risks=(),
            critique_notes=notes
        )
