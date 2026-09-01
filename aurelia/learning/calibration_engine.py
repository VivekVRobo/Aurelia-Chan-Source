"""
Aurelia Cognitive OS V3 - Phase 10: Calibration Engine
=======================================================
Calibrates confidence estimates and prediction accuracy.

The calibration engine ensures that the system's confidence
estimates are well-calibrated and aligned with actual outcomes.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime
import statistics


class CalibrationType(Enum):
    """Types of calibration."""
    CONFIDENCE = "confidence"
    PREDICTION = "prediction"
    PROBABILITY = "probability"


@dataclass
class CalibrationRecord:
    """
    A record of a calibration event.
    
    Tracks predicted vs actual outcomes for calibration.
    """
    id: str
    calibration_type: CalibrationType
    predicted_value: float
    actual_value: float
    confidence_estimate: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CalibrationMetrics:
    """
    Metrics for calibration quality.
    
    Contains statistics about how well-calibrated the system is.
    """
    calibration_type: CalibrationType
    total_records: int
    mean_absolute_error: float
    mean_squared_error: float
    calibration_score: float  # 0-1 scale, higher is better
    overconfidence_count: int
    underconfidence_count: int


class CalibrationEngine:
    """
    Calibrates confidence estimates and prediction accuracy.
    
    The calibration engine:
    - Records predictions and their outcomes
    - Calculates calibration metrics
    - Identifies systematic biases (over/underconfidence)
    - Provides calibration feedback
    """
    
    def __init__(self):
        self.records: List[CalibrationRecord] = []
        self.record_counter = 0
        self.metrics: Dict[CalibrationType, CalibrationMetrics] = {}
    
    def record_prediction(
        self,
        calibration_type: CalibrationType,
        predicted_value: float,
        confidence_estimate: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CalibrationRecord:
        """Record a prediction for later calibration."""
        record_id = f"calibration_{self.record_counter}"
        
        record = CalibrationRecord(
            id=record_id,
            calibration_type=calibration_type,
            predicted_value=predicted_value,
            actual_value=None,  # Will be set when outcome is known
            confidence_estimate=confidence_estimate,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.records.append(record)
        self.record_counter += 1
        
        return record
    
    def record_outcome(self, record_id: str, actual_value: float):
        """Record the actual outcome for a prediction."""
        record = self.get_record(record_id)
        if not record:
            raise ValueError(f"Record {record_id} not found")
        
        record.actual_value = actual_value
        
        # Recalculate metrics for this calibration type
        self._calculate_metrics(record.calibration_type)
    
    def _calculate_metrics(self, calibration_type: CalibrationType):
        """Calculate calibration metrics for a specific type."""
        type_records = [r for r in self.records if r.calibration_type == calibration_type and r.actual_value is not None]
        
        if not type_records:
            return
        
        # Calculate errors
        absolute_errors = [abs(r.predicted_value - r.actual_value) for r in type_records]
        squared_errors = [(r.predicted_value - r.actual_value) ** 2 for r in type_records]
        
        mean_absolute_error = statistics.mean(absolute_errors)
        mean_squared_error = statistics.mean(squared_errors)
        
        # Calculate calibration score (inverse of error)
        calibration_score = max(0.0, 1.0 - mean_absolute_error)
        
        # Count over/underconfidence
        overconfidence_count = 0
        underconfidence_count = 0
        
        for record in type_records:
            error = record.predicted_value - record.actual_value
            if error > 0.1:  # Significant overestimation
                overconfidence_count += 1
            elif error < -0.1:  # Significant underestimation
                underconfidence_count += 1
        
        metrics = CalibrationMetrics(
            calibration_type=calibration_type,
            total_records=len(type_records),
            mean_absolute_error=mean_absolute_error,
            mean_squared_error=mean_squared_error,
            calibration_score=calibration_score,
            overconfidence_count=overconfidence_count,
            underconfidence_count=underconfidence_count
        )
        
        self.metrics[calibration_type] = metrics
    
    def get_calibration_score(self, calibration_type: CalibrationType) -> float:
        """Get the calibration score for a specific type."""
        if calibration_type not in self.metrics:
            self._calculate_metrics(calibration_type)
        
        return self.metrics.get(calibration_type, CalibrationMetrics(
            calibration_type=calibration_type,
            total_records=0,
            mean_absolute_error=0.0,
            mean_squared_error=0.0,
            calibration_score=0.0,
            overconfidence_count=0,
            underconfidence_count=0
        )).calibration_score
    
    def adjust_confidence(self, confidence_estimate: float, calibration_type: CalibrationType) -> float:
        """
        Adjust a confidence estimate based on calibration history.
        
        Applies a correction factor based on historical calibration performance.
        """
        calibration_score = self.get_calibration_score(calibration_type)
        
        if calibration_score < 0.7:
            # System tends to be overconfident - reduce estimates
            return confidence_estimate * 0.9
        elif calibration_score > 0.9:
            # System is well-calibrated - no adjustment needed
            return confidence_estimate
        else:
            # Moderate calibration - slight adjustment
            return confidence_estimate * 0.95
    
    def get_bias_feedback(self, calibration_type: CalibrationType) -> str:
        """Get feedback about calibration bias."""
        if calibration_type not in self.metrics:
            return "Insufficient data for bias analysis"
        
        metrics = self.metrics[calibration_type]
        
        if metrics.overconfidence_count > metrics.underconfidence_count * 2:
            return "System tends to be overconfident. Consider reducing confidence estimates."
        elif metrics.underconfidence_count > metrics.overconfidence_count * 2:
            return "System tends to be underconfident. Consider increasing confidence estimates."
        else:
            return "System is reasonably well-calibrated."
    
    def get_record(self, record_id: str) -> Optional[CalibrationRecord]:
        """Get a calibration record by ID."""
        for record in self.records:
            if record.id == record_id:
                return record
        return None
    
    def get_records_by_type(self, calibration_type: CalibrationType) -> List[CalibrationRecord]:
        """Get all records of a specific type."""
        return [r for r in self.records if r.calibration_type == calibration_type]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the calibration engine state."""
        return {
            "total_records": len(self.records),
            "records_with_outcomes": len([r for r in self.records if r.actual_value is not None]),
            "by_type": {
                ct.value: len(self.get_records_by_type(ct))
                for ct in CalibrationType
            },
            "calibration_scores": {
                ct.value: self.get_calibration_score(ct)
                for ct in CalibrationType
            }
        }