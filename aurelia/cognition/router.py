"""
Aurelia Cognitive OS V4 - Cognitive Router & Complexity Classifier
==================================================================
Classifies cognitive complexity, bounds resource budgets, and routes
requests to the minimal necessary sub-graph (Reflex vs Standard vs Deep vs Verified).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional
from aurelia.contracts.meaning_frame import MeaningFrame, IntentType
from aurelia.contracts.snapshot import CognitiveSnapshot


class CognitiveComplexityMode(Enum):
    REFLEX = "reflex"          # Deterministic direct response (0 LLM calls, instant)
    STANDARD = "standard"      # Single-pass specialist + renderer (1 LLM call)
    DEEP = "deep"              # Full DAG: Hypotheses search + Monte Carlo + Critic (2-3 LLM calls)
    VERIFIED = "verified"      # Multi-critic + strict numerical firewall + sensitivity analysis (4+ LLM calls)


@dataclass(frozen=True)
class CognitiveBudget:
    """Resource bounds for a single cognitive cycle."""
    mode: CognitiveComplexityMode
    max_llm_calls: int = 1
    max_critic_calls: int = 0
    max_plan_nodes: int = 10
    max_retrieval_items: int = 10
    max_simulations: int = 1000
    max_context_tokens: int = 8000
    timeout_seconds: float = 30.0


class CognitiveRouter:
    """
    Classifies intent complexity and assigns optimal cognitive budgets.
    """

    @classmethod
    def classify(cls, meaning: MeaningFrame, snapshot: Optional[CognitiveSnapshot] = None) -> CognitiveBudget:
        """
        Determines the optimal execution mode and budget for a request.
        """
        intent = meaning.intent
        
        # 1. Reflex Mode (Status inquiry, score lookup, past fact lookup)
        if intent == IntentType.STATUS_INQUIRY:
            return CognitiveBudget(
                mode=CognitiveComplexityMode.REFLEX,
                max_llm_calls=0,
                max_critic_calls=0,
                max_plan_nodes=3,
                max_retrieval_items=5,
                max_simulations=0,
                max_context_tokens=2000,
                timeout_seconds=5.0
            )

        # 2. Deep / Verified Mode (High-stakes Tradeoffs, Offer Decisions, Major Negotiations)
        if intent in [IntentType.DECISION_EVALUATION, IntentType.COMPENSATION_STRATEGY]:
            return CognitiveBudget(
                mode=CognitiveComplexityMode.DEEP,
                max_llm_calls=3,
                max_critic_calls=2,
                max_plan_nodes=25,
                max_retrieval_items=25,
                max_simulations=1000,
                max_context_tokens=12000,
                timeout_seconds=45.0
            )

        # 3. Standard Mode (Resume audit, mock interview, general roadmap)
        return CognitiveBudget(
            mode=CognitiveComplexityMode.STANDARD,
            max_llm_calls=1,
            max_critic_calls=0,
            max_plan_nodes=10,
            max_retrieval_items=10,
            max_simulations=250,
            max_context_tokens=8000,
            timeout_seconds=20.0
        )
