"""
Aurelia Cognitive OS V3 - Phase 9: Prediction Engine
=================================================
Predicts future states and outcomes based on current data.

The prediction engine uses available data to make informed predictions
about future career progression, skill development, and outcomes.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import statistics


class PredictionType(Enum):
    """Types of predictions."""
    CAREER_PROGRESSION = "career_progression"
    SKILL_ACQUISITION = "skill_acquisition"
    MARKET_TRENDS = "market_trends"
    GOAL_ACHIEVEMENT = "goal_achievement"
    TIMELINE_ESTIMATION = "timeline_estimation"


class PredictionConfidence(Enum):
    """Confidence levels for predictions."""
    HIGH = "high"  # > 0.8
    MEDIUM = "medium"  # 0.5-0.8
    LOW = "low"  # < 0.5
    UNCERTAIN = "uncertain"  # insufficient data


@dataclass
class Prediction:
    """
    A prediction about a future state or outcome.
    
    Predictions are probabilistic estimates based on available data.
    """
    id: str
    prediction_type: PredictionType
    description: str
    predicted_value: Any
    confidence: float
    confidence_level: PredictionConfidence
    time_horizon: str  # e.g., "6 months", "1 year"
    factors: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PredictionAccuracy:
    """Record of prediction accuracy for learning."""
    prediction_id: str
    actual_value: Any
    predicted_value: Any
    accuracy_score: float
    error_magnitude: float
    timestamp: datetime


class PredictionEngine:
    """
    Predicts future states and outcomes based on current data.
    
    The prediction engine:
    - Makes probabilistic predictions about future states
    - Uses historical data and trends when available
    - Provides confidence estimates for predictions
    - Tracks prediction accuracy for learning
    """
    
    def __init__(self):
        self.predictions: Dict[str, Prediction] = {}
        self.accuracy_records: List[PredictionAccuracy] = []
        self.prediction_counter = 0
    
    def create_prediction(
        self,
        prediction_type: PredictionType,
        description: str,
        predicted_value: Any,
        confidence: float,
        time_horizon: str,
        factors: Optional[List[str]] = None,
        assumptions: Optional[List[str]] = None
    ) -> Prediction:
        """Create a new prediction."""
        prediction_id = f"prediction_{self.prediction_counter}"
        
        # Determine confidence level
        if confidence >= 0.8:
            confidence_level = PredictionConfidence.HIGH
        elif confidence >= 0.5:
            confidence_level = PredictionConfidence.MEDIUM
        elif confidence >= 0.3:
            confidence_level = PredictionConfidence.LOW
        else:
            confidence_level = PredictionConfidence.UNCERTAIN
        
        prediction = Prediction(
            id=prediction_id,
            prediction_type=prediction_type,
            description=description,
            predicted_value=predicted_value,
            confidence=confidence,
            confidence_level=confidence_level,
            time_horizon=time_horizon,
            factors=factors or [],
            assumptions=assumptions or []
        )
        
        self.predictions[prediction_id] = prediction
        self.prediction_counter += 1
        
        return prediction
    
    def predict_career_progression(
        self,
        current_role: str,
        target_role: str,
        current_skills: Dict[str, float],
        time_horizon: str = "2 years"
    ) -> Prediction:
        """
        Predict career progression likelihood.
        
        Estimates probability of reaching target role within time horizon.
        """
        # Simple prediction logic - in full system would use more sophisticated models
        target_requirements = {
            "Director": 0.8,  # Minimum average skill level
            "Senior Manager": 0.6,
            "Manager": 0.4
        }
        
        required_level = target_requirements.get(target_role, 0.7)
        current_level = statistics.mean(current_skills.values()) if current_skills else 0.3
        
        # Calculate progress probability
        skill_gap = required_level - current_level
        if skill_gap <= 0:
            probability = 0.9
        elif skill_gap <= 0.2:
            probability = 0.7
        elif skill_gap <= 0.4:
            probability = 0.5
        else:
            probability = 0.3
        
        return self.create_prediction(
            prediction_type=PredictionType.CAREER_PROGRESSION,
            description=f"Probability of reaching {target_role} within {time_horizon}",
            predicted_value=probability,
            confidence=0.7,
            time_horizon=time_horizon,
            factors=[f"Current skill level: {current_level:.2f}", f"Required level: {required_level}"],
            assumptions=["Linear skill development", "No major career disruptions"]
        )
    
    def predict_skill_acquisition(
        self,
        skill_name: str,
        current_level: float,
        target_level: float,
        time_available: str,
        learning_intensity: str = "moderate"
    ) -> Prediction:
        """
        Predict skill acquisition probability.
        
        Estimates probability of reaching target skill level in given time.
        """
        # Simple learning curve model
        intensity_multiplier = {
            "low": 0.5,
            "moderate": 1.0,
            "high": 1.5,
            "intensive": 2.0
        }
        
        multiplier = intensity_multiplier.get(learning_intensity, 1.0)
        
        # Estimate weeks to acquire skill
        skill_gap = target_level - current_level
        if skill_gap <= 0:
            weeks_needed = 0
            probability = 1.0
        else:
            # Simple model: 0.1 skill level per week * intensity
            weeks_needed = skill_gap / (0.1 * multiplier)
            
            # Parse time available
            if "month" in time_available.lower():
                months = int(''.join(filter(str.isdigit, time_available)))
                weeks_available = months * 4
            else:
                weeks_available = 12  # Default 3 months
            
            if weeks_needed <= weeks_available:
                probability = 0.8
            elif weeks_needed <= weeks_available * 1.5:
                probability = 0.5
            else:
                probability = 0.3
        
        return self.create_prediction(
            prediction_type=PredictionType.SKILL_ACQUISITION,
            description=f"Probability of reaching {target_level} in {skill_name} within {time_available}",
            predicted_value=probability,
            confidence=0.6,
            time_horizon=time_available,
            factors=[f"Current level: {current_level}", f"Target level: {target_level}", f"Learning intensity: {learning_intensity}"],
            assumptions=["Consistent learning effort", "Quality learning resources available"]
        )
    
    def predict_goal_achievement(
        self,
        goal_description: str,
        current_progress: float,
        remaining_time: str,
        resource_availability: str = "adequate"
    ) -> Prediction:
        """
        Predict goal achievement probability.
        
        Estimates probability of completing goal within remaining time.
        """
        # Calculate required progress rate
        required_progress = 1.0 - current_progress
        
        # Parse remaining time
        if "month" in remaining_time.lower():
            months = int(''.join(filter(str.isdigit, remaining_time)))
            total_weeks = months * 4
        else:
            total_weeks = 12  # Default 3 months
        
        # Required weekly progress rate
        if total_weeks > 0:
            required_weekly_rate = required_progress / total_weeks
        else:
            required_weekly_rate = 1.0
        
        # Estimate feasibility
        if required_weekly_rate <= 0.02:  # 2% per week
            probability = 0.9
        elif required_weekly_rate <= 0.05:  # 5% per week
            probability = 0.7
        elif required_weekly_rate <= 0.1:  # 10% per week
            probability = 0.5
        else:
            probability = 0.3
        
        # Adjust for resource availability
        if resource_availability == "limited":
            probability *= 0.7
        elif resource_availability == "abundant":
            probability *= 1.1
        
        probability = min(1.0, probability)
        
        return self.create_prediction(
            prediction_type=PredictionType.GOAL_ACHIEVEMENT,
            description=f"Probability of achieving goal: {goal_description}",
            predicted_value=probability,
            confidence=0.7,
            time_horizon=remaining_time,
            factors=[f"Current progress: {current_progress:.0%}", f"Required weekly rate: {required_weekly_rate:.2%}"],
            assumptions=[f"Resource availability: {resource_availability}"]
        )
    
    def record_accuracy(self, prediction_id: str, actual_value: Any):
        """Record actual outcome to track prediction accuracy."""
        prediction = self.get_prediction(prediction_id)
        if not prediction:
            raise ValueError(f"Prediction {prediction_id} not found")
        
        # Calculate accuracy
        if isinstance(prediction.predicted_value, (int, float)) and isinstance(actual_value, (int, float)):
            error = abs(prediction.predicted_value - actual_value)
            # Normalize error to 0-1 scale (assuming max error of 1.0)
            accuracy = max(0.0, 1.0 - error)
        else:
            # For categorical predictions, simple match
            accuracy = 1.0 if prediction.predicted_value == actual_value else 0.0
            error = 0.0 if accuracy == 1.0 else 1.0
        
        accuracy_record = PredictionAccuracy(
            prediction_id=prediction_id,
            actual_value=actual_value,
            predicted_value=prediction.predicted_value,
            accuracy_score=accuracy,
            error_magnitude=error,
            timestamp=datetime.now()
        )
        
        self.accuracy_records.append(accuracy_record)
    
    def get_prediction(self, prediction_id: str) -> Optional[Prediction]:
        """Get a prediction by ID."""
        return self.predictions.get(prediction_id)
    
    def get_predictions_by_type(self, prediction_type: PredictionType) -> List[Prediction]:
        """Get all predictions of a specific type."""
        return [p for p in self.predictions.values() if p.prediction_type == prediction_type]
    
    def get_average_accuracy(self) -> float:
        """Calculate average prediction accuracy."""
        if not self.accuracy_records:
            return 0.0
        
        return statistics.mean([r.accuracy_score for r in self.accuracy_records])
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the prediction engine state."""
        return {
            "total_predictions": len(self.predictions),
            "by_type": {pt.value: len(self.get_predictions_by_type(pt)) for pt in PredictionType},
            "accuracy_records": len(self.accuracy_records),
            "average_accuracy": self.get_average_accuracy(),
            "high_confidence_count": len([p for p in self.predictions.values() if p.confidence_level == PredictionConfidence.HIGH])
        }