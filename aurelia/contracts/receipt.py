"""
Aurelia Cognitive OS V4 - Decision Lineage & Receipts
=====================================================
Captures complete deterministic provenance for every major decision
enabling bit-for-bit replayability and forensic auditing.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Tuple, Any, Optional, List


@dataclass(frozen=True)
class InferenceRecord:
    """Audit record for an LLM inference call."""
    inference_id: str
    model_name: str
    cognitive_role: str          # "semantic", "reasoning", "critic", "renderer"
    snapshot_id: str
    prompt_template_version: str
    temperature: float
    input_tokens_est: int
    output_tokens_est: int
    latency_ms: float
    parse_success: bool
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    raw_prompt_hash: Optional[str] = None
    output_schema_name: Optional[str] = None


@dataclass(frozen=True)
class DecisionReceipt:
    """
    Complete immutable audit receipt for a decision or analysis cycle.
    Enables `python aurelia.py replay <receipt_id>`.
    """
    decision_id: str
    snapshot_id: str
    request_text: str
    intent_type: str
    
    # Execution Trace
    plan_dag_nodes: Tuple[str, ...]
    capabilities_invoked: Tuple[str, ...]
    inferences_made: Tuple[InferenceRecord, ...]
    
    # Hypotheses & Critics
    hypotheses_considered: Tuple[str, ...]
    selected_hypothesis_id: Optional[str]
    critic_scores: Dict[str, float]
    
    # Verification & Calculations
    numerical_calculations_verified: Tuple[str, ...]
    verification_passed: bool
    verification_severity: str     # "info", "warning", "error", "blocker"
    
    # Final Output & Artifacts
    conclusion_summary: str
    artifacts_generated_ids: Tuple[str, ...]
    confidence_score: float
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    deterministic_replay_hash: str = ""
