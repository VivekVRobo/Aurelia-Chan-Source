"""
Aurelia Cognitive OS V6 - Transactional Observation Promotion & Receipts
========================================================================
Executes atomic, transactional promotion of grounded observations to world-state
memory, rolling back upon any verification failure and emitting PerceptionReceipts.
"""

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from aurelia.contracts.v6_contracts import (
    Observation,
    ObservationPromotionStage,
    PerceptionReceipt,
    Modality
)


@dataclass(frozen=True)
class PromotionTransactionResult:
    """Outcome of transactional observation promotion."""
    success: bool
    final_stage: ObservationPromotionStage
    receipt: Optional[PerceptionReceipt]
    rollback_reason: Optional[str]
    committed_fact_keys: Tuple[str, ...]


class TransactionalObservationPromoter:
    """
    Manages atomic promotion pipeline from RAW_OBSERVATION to WORLD_STATE_MEMORY.
    """

    def __init__(self):
        self.committed_receipts: List[PerceptionReceipt] = []
        self.world_state_facts: Dict[str, Any] = {}

    def execute_promotion_transaction(
        self,
        observation: Observation,
        fact_key: str,
        fact_value: Any,
        verification_passed: bool
    ) -> PromotionTransactionResult:
        """
        Executes atomic promotion. If verification fails, rolls back completely.
        """
        # Save snapshot for rollback
        pre_transaction_state = dict(self.world_state_facts)

        try:
            # 1. RAW -> NORMALIZED
            stage_1 = ObservationPromotionStage.NORMALIZED_OBSERVATION

            # 2. NORMALIZED -> GROUNDED
            stage_2 = ObservationPromotionStage.GROUNDED_OBSERVATION

            # 3. GROUNDED -> EVIDENCE
            stage_3 = ObservationPromotionStage.EVIDENCE

            # 4. EVIDENCE -> FACT_CANDIDATE
            stage_4 = ObservationPromotionStage.FACT_CANDIDATE

            # 5. Verification Gate
            if not verification_passed:
                raise ValueError("Verification failure: Observation contradicts high-confidence authoritative facts.")

            # 6. Commit to WORLD_STATE_MEMORY
            stage_5 = ObservationPromotionStage.WORLD_STATE_MEMORY
            self.world_state_facts[fact_key] = fact_value

            # 7. Generate PerceptionReceipt
            receipt = PerceptionReceipt(
                receipt_id=f"rec_percept_{int(time.time()*1000)}",
                session_id=observation.session_id,
                modality=observation.modality,
                root_source_id=observation.provenance.root_source_id,
                raw_retained=False,
                observations_created=(observation.observation_id,),
                evidence_promoted=(f"ev_{fact_key}",),
                world_state_changes=(f"{fact_key}={fact_value}",)
            )
            self.committed_receipts.append(receipt)

            return PromotionTransactionResult(
                success=True,
                final_stage=stage_5,
                receipt=receipt,
                rollback_reason=None,
                committed_fact_keys=(fact_key,)
            )

        except Exception as e:
            # ROLLBACK: restore exact world state
            self.world_state_facts = pre_transaction_state
            return PromotionTransactionResult(
                success=False,
                final_stage=ObservationPromotionStage.FACT_CANDIDATE,
                receipt=None,
                rollback_reason=str(e),
                committed_fact_keys=()
            )
