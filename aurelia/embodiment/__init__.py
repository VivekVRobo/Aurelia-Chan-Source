"""Actuator-free Aurelia to RCI embodiment boundary."""

from aurelia.embodiment.adapter import AureliaEmbodimentAdapter, EmbodimentContractError
from aurelia.embodiment.contracts import (
    SCHEMA_VERSION,
    CharacterResponse,
    ExpressionIntent,
    ExpressionStrength,
    MotionCue,
    MotionDisposition,
    MotionIntent,
    MotionStyle,
    SpeechDelivery,
    SpeechIntent,
)

__all__ = [
    "SCHEMA_VERSION",
    "AureliaEmbodimentAdapter",
    "CharacterResponse",
    "EmbodimentContractError",
    "ExpressionIntent",
    "ExpressionStrength",
    "MotionCue",
    "MotionDisposition",
    "MotionIntent",
    "MotionStyle",
    "SpeechDelivery",
    "SpeechIntent",
]
