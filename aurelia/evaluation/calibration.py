"""
Aurelia Cognitive OS V4 - Calibration, Benchmarks & Decision Replay
===================================================================
Enables calibration measurement, ablation testing, and bit-for-bit decision replay.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple, Any, Optional
from aurelia.contracts.receipt import DecisionReceipt


@dataclass(frozen=True)
class CalibrationBucket:
    """A confidence calibration bin (e.g. 70-80% predicted confidence)."""
    bin_label: str
    predicted_confidence_mean: float
    observed_accuracy: float
    sample_count: int
    calibration_error: float


class CalibrationEngine:
    """
    Measures and ensures that an 85% confidence prediction is correct ~85% of the time.
    """

    @staticmethod
    def evaluate_calibration(predictions: List[Tuple[float, bool]]) -> List[CalibrationBucket]:
        """
        Takes list of (predicted_confidence, was_actually_correct) tuples
        and computes calibration bins.
        """
        bins = [(0.0, 0.5, "0-50%"), (0.5, 0.7, "50-70%"), (0.7, 0.85, "70-85%"), (0.85, 1.0, "85-100%")]
        buckets: List[CalibrationBucket] = []
        
        for low, high, label in bins:
            bin_items = [p for p in predictions if low <= p[0] < high or (high == 1.0 and p[0] == 1.0)]
            if not bin_items:
                continue
                
            mean_conf = sum(p[0] for p in bin_items) / len(bin_items)
            acc = sum(1 for p in bin_items if p[1]) / len(bin_items)
            err = abs(mean_conf - acc)
            
            buckets.append(CalibrationBucket(
                bin_label=label,
                predicted_confidence_mean=mean_conf,
                observed_accuracy=acc,
                sample_count=len(bin_items),
                calibration_error=err
            ))
            
        return buckets


class DecisionReplayer:
    """
    Deterministic replay engine for forensic debugging.
    """

    @staticmethod
    def verify_receipt_integrity(receipt: DecisionReceipt) -> bool:
        """Verifies that all required audit fields exist and are non-empty."""
        if not receipt.decision_id or not receipt.snapshot_id or not receipt.request_text:
            return False
        if not receipt.capabilities_invoked:
            return False
        return True
