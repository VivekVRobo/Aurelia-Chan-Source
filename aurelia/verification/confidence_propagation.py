"""
Aurelia Cognitive OS V3 - Phase 6: Confidence Propagation
=========================================================
Manages uncertainty through the system.

Confidence propagation ensures that uncertainty is properly
managed and communicated throughout the cognitive system.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
from datetime import datetime
from statistics import mean, stdev


class ConfidenceSource(Enum):
    """Sources of confidence information."""
    EVIDENCE = "evidence"  # Confidence from evidence strength
    SPECIALIST_ENGINE = "specialist_engine"  # Confidence from specialist systems
    LLM = "llm"  # Confidence from LLM reasoning
    USER_FEEDBACK = "user_feedback"  # Confidence from user corrections
    EXPERT_KNOWLEDGE = "expert_knowledge"  # Confidence from expert rules


@dataclass
class ConfidenceEstimate:
    """
    A confidence estimate with provenance.
    """
    value: float  # 0-1 scale
    source: ConfidenceSource
    description: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfidencePropagation:
    """
    Result of confidence propagation through a chain of reasoning.
    """
    initial_confidence: float
    propagated_confidence: float
    confidence_loss: float
    propagation_steps: List[Tuple[str, float]]  # (step_description, confidence_at_step)
    final_source: ConfidenceSource


class ConfidencePropagator:
    """
    Manages uncertainty through the system.
    
    The confidence propagator:
    - Tracks confidence from different sources
    - Propagates confidence through reasoning chains
    - Calculates confidence loss
    - Combines multiple confidence estimates
    - Handles uncertainty in final responses
    """
    
    def __init__(self):
        self.confidence_estimates: Dict[str, List[ConfidenceEstimate]] = {}  # item_id -> estimates
        self.estimate_counter = 0
    
    def add_confidence_estimate(
        self,
        item_id: str,
        value: float,
        source: ConfidenceSource,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConfidenceEstimate:
        """Add a confidence estimate for an item."""
        estimate = ConfidenceEstimate(
            value=value,
            source=source,
            description=description,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        if item_id not in self.confidence_estimates:
            self.confidence_estimates[item_id] = []
        
        self.confidence_estimates[item_id].append(estimate)
        self.estimate_counter += 1
        
        return estimate
    
    def get_confidence_estimates(self, item_id: str) -> List[ConfidenceEstimate]:
        """Get all confidence estimates for an item."""
        return self.confidence_estimates.get(item_id, [])
    
    def combine_confidence_estimates(self, item_id: str) -> float:
        """
        Combine multiple confidence estimates for an item.
        
        Uses weighted averaging based on source reliability.
        """
        estimates = self.get_confidence_estimates(item_id)
        
        if not estimates:
            return 0.5  # Default to uncertain
        
        # Source reliability weights
        source_weights = {
            ConfidenceSource.EVIDENCE: 1.0,
            ConfidenceSource.SPECIALIST_ENGINE: 0.9,
            ConfidenceSource.EXPERT_KNOWLEDGE: 0.85,
            ConfidenceSource.USER_FEEDBACK: 0.95,
            ConfidenceSource.LLM: 0.7  # LLM is less reliable for factual claims
        }
        
        # Calculate weighted average
        weighted_sum = 0.0
        total_weight = 0.0
        
        for estimate in estimates:
            weight = source_weights.get(estimate.source, 0.5)
            weighted_sum += estimate.value * weight
            total_weight += weight
        
        if total_weight == 0:
            return mean([e.value for e in estimates])
        
        return weighted_sum / total_weight
    
    def propagate_confidence(
        self,
        initial_confidence: float,
        reasoning_steps: List[Tuple[str, float]]
    ) -> ConfidencePropagation:
        """
        Propagate confidence through a chain of reasoning.
        
        Each reasoning step can reduce confidence.
        """
        current_confidence = initial_confidence
        steps = [("initial", initial_confidence)]
        
        for step_description, step_confidence_impact in reasoning_steps:
            # Apply the confidence impact for this step
            current_confidence = current_confidence * step_confidence_impact
            steps.append((step_description, current_confidence))
        
        confidence_loss = initial_confidence - current_confidence
        
        return ConfidencePropagation(
            initial_confidence=initial_confidence,
            propagated_confidence=current_confidence,
            confidence_loss=confidence_loss,
            propagation_steps=steps,
            final_source=ConfidenceSource.LLM  # Assume final source is LLM
        )
    
    def calculate_chain_confidence(self, chain: List[float]) -> float:
        """
        Calculate confidence for a chain of dependent items.
        
        Chain confidence is the product of individual confidences.
        """
        if not chain:
            return 0.5
        
        chain_confidence = 1.0
        for confidence in chain:
            chain_confidence *= confidence
        
        return chain_confidence
    
    def calculate_aggregate_confidence(self, item_ids: List[str]) -> float:
        """
        Calculate aggregate confidence for multiple items.
        
        Aggregate confidence is the average of individual confidences.
        """
        if not item_ids:
            return 0.5
        
        individual_confidences = []
        for item_id in item_ids:
            combined = self.combine_confidence_estimates(item_id)
            individual_confidences.append(combined)
        
        return mean(individual_confidences)
    
    def detect_low_confidence(self, threshold: float = 0.6) -> List[str]:
        """Detect items with confidence below threshold."""
        low_confidence = []
        
        for item_id in self.confidence_estimates:
            combined = self.combine_confidence_estimates(item_id)
            if combined < threshold:
                low_confidence.append(item_id)
        
        return low_confidence
    
    def get_confidence_summary(self, item_id: str) -> Dict[str, Any]:
        """Get a summary of confidence information for an item."""
        estimates = self.get_confidence_estimates(item_id)
        
        if not estimates:
            return {
                "item_id": item_id,
                "has_estimates": False,
                "combined_confidence": 0.5
            }
        
        combined = self.combine_confidence_estimates(item_id)
        
        return {
            "item_id": item_id,
            "has_estimates": True,
            "estimate_count": len(estimates),
            "combined_confidence": combined,
            "by_source": {
                source.value: len([e for e in estimates if e.source == source])
                for source in ConfidenceSource
            },
            "recent_estimates": len([e for e in estimates if (datetime.now() - e.timestamp).total_seconds() < 86400]),
            "average_confidence": mean([e.value for e in estimates])
        }
    
    def update_confidence_from_feedback(self, item_id: str, feedback_value: float):
        """
        Update confidence based on user feedback.
        
        User feedback is given high weight in confidence calculation.
        """
        self.add_confidence_estimate(
            item_id=item_id,
            value=feedback_value,
            source=ConfidenceSource.USER_FEEDBACK,
            description="User feedback",
            metadata={"feedback_type": "correction"}
        )
    
    def get_global_summary(self) -> Dict[str, Any]:
        """Get a global summary of confidence across all items."""
        if not self.confidence_estimates:
            return {
                "total_items": 0,
                "total_estimates": 0,
                "average_confidence": 0.0
            }
        
        all_confidences = []
        for item_id in self.confidence_estimates:
            combined = self.combine_confidence_estimates(item_id)
            all_confidences.append(combined)
        
        return {
            "total_items": len(self.confidence_estimates),
            "total_estimates": self.estimate_counter,
            "average_confidence": mean(all_confidences),
            "confidence_std": stdev(all_confidences) if len(all_confidences) > 1 else 0.0,
            "low_confidence_count": len([c for c in all_confidences if c < 0.6]),
            "high_confidence_count": len([c for c in all_confidences if c >= 0.8])
        }