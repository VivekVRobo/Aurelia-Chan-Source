"""Actuator-free embodiment contracts shared with the Robotic Character Interface.

The character layer can request semantic expression only. It cannot carry robot
joint targets, PWM values, servo angles, trajectories, or other actuator-level
commands. RCI's behavior, robotics, and deterministic safety layers remain the
sole authorities for physical motion.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

SCHEMA_VERSION = "rci.character_response.v1"


class SpeechDelivery(StrEnum):
    """Semantic vocal delivery style; never a synthesizer control packet."""

    NEUTRAL = "neutral"
    SUPPORTIVE = "supportive"
    CONFIDENT = "confident"
    CAUTIOUS = "cautious"
    ENCOURAGING = "encouraging"
    EMPATHETIC = "empathetic"


class ExpressionStrength(StrEnum):
    """Semantic strength of the requested character expression."""

    NONE = "none"
    SUBTLE = "subtle"
    MODERATE = "moderate"
    STRONG = "strong"


class MotionCue(StrEnum):
    """High-level optional behavior cue for RCI's deterministic behavior planner."""

    NONE = "none"
    LISTEN = "listen"
    ACKNOWLEDGE = "acknowledge"
    PRESENT = "present"
    CAUTION = "caution"
    CELEBRATE = "celebrate"
    THINK = "think"


class MotionStyle(StrEnum):
    """Character-level motion style that may only reduce or shape behavior."""

    RESTRAINED = "restrained"
    STANDARD = "standard"
    EXPRESSIVE = "expressive"


class MotionDisposition(StrEnum):
    """Whether RCI may consider the cue; Aurelia can never require physical motion."""

    NONE = "none"
    OPTIONAL = "optional"


@dataclass(frozen=True)
class SpeechIntent:
    """Verified prose plus semantic delivery guidance."""

    text: str
    delivery: SpeechDelivery
    interruptible: bool = True


@dataclass(frozen=True)
class ExpressionIntent:
    """Canonical character expression request."""

    expression: str
    strength: ExpressionStrength


@dataclass(frozen=True)
class MotionIntent:
    """Optional semantic cue consumed by RCI's Behavior Planner."""

    cue: MotionCue
    style: MotionStyle
    disposition: MotionDisposition


@dataclass(frozen=True)
class CharacterResponse:
    """Verified character envelope suitable for the RCI cognition boundary."""

    schema_version: str
    interaction_id: str
    decision_id: str
    source_character: str
    speech: SpeechIntent
    expression: ExpressionIntent
    motion: MotionIntent
    verified: bool
    persistence_committed: bool
    persistence_durable: bool

    def to_dict(self) -> dict[str, Any]:
        """Serialize the stable cross-repository contract."""
        return {
            "schema_version": self.schema_version,
            "interaction_id": self.interaction_id,
            "decision_id": self.decision_id,
            "source_character": self.source_character,
            "speech": {
                "text": self.speech.text,
                "delivery": self.speech.delivery.value,
                "interruptible": self.speech.interruptible,
            },
            "expression": {
                "expression": self.expression.expression,
                "strength": self.expression.strength.value,
            },
            "motion": {
                "cue": self.motion.cue.value,
                "style": self.motion.style.value,
                "disposition": self.motion.disposition.value,
            },
            "verified": self.verified,
            "persistence_committed": self.persistence_committed,
            "persistence_durable": self.persistence_durable,
        }
