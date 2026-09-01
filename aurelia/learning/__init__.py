"""
Aurelia Cognitive OS V3 - Phase 10: Learning Module
=================================================
Learning capabilities for memory consolidation, calibration,
user-specific models, and feedback learning.
"""

from .memory_consolidation import (
    MemoryConsolidator,
    ConsolidationType,
    ConsolidationPriority,
    ConsolidationCandidate,
    ConsolidationResult
)

from .calibration_engine import (
    CalibrationEngine,
    CalibrationType,
    CalibrationRecord,
    CalibrationMetrics
)

from .user_models import (
    UserModelManager,
    ModelType,
    UserFeature,
    UserModel
)

from .feedback_learning import (
    FeedbackLearner,
    FeedbackType,
    FeedbackCategory,
    FeedbackEvent,
    LearningInsight
)

__all__ = [
    # Memory Consolidation
    "MemoryConsolidator",
    "ConsolidationType",
    "ConsolidationPriority",
    "ConsolidationCandidate",
    "ConsolidationResult",
    # Calibration
    "CalibrationEngine",
    "CalibrationType",
    "CalibrationRecord",
    "CalibrationMetrics",
    # User Models
    "UserModelManager",
    "ModelType",
    "UserFeature",
    "UserModel",
    # Feedback Learning
    "FeedbackLearner",
    "FeedbackType",
    "FeedbackCategory",
    "FeedbackEvent",
    "LearningInsight"
]