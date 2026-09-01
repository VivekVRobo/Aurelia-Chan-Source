"""Translate verified Aurelia output into the actuator-free RCI character contract."""

from __future__ import annotations

from aurelia.character.affect_engine import AffectIntensity, Emotion
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
from aurelia.runtime.cognitive_runtime import CognitiveCycleResponse


class EmbodimentContractError(RuntimeError):
    """A cognitive result is not eligible to cross the embodiment boundary."""


class AureliaEmbodimentAdapter:
    """Convert a completed cognitive cycle into semantic RCI character intent."""

    @classmethod
    def adapt(cls, result: CognitiveCycleResponse) -> CharacterResponse:
        """Return an actuator-free character response or fail closed."""
        cls._validate_source_cycle(result)
        cue, style = cls._motion_cue(result)
        disposition = (
            MotionDisposition.NONE if cue == MotionCue.NONE else MotionDisposition.OPTIONAL
        )
        return CharacterResponse(
            schema_version=SCHEMA_VERSION,
            interaction_id=cls._interaction_id(result.decision_receipt.decision_id),
            decision_id=result.decision_receipt.decision_id,
            source_character="aurelia",
            speech=SpeechIntent(
                text=result.response_text,
                delivery=cls._speech_delivery(result.persona.emotion),
                interruptible=True,
            ),
            expression=ExpressionIntent(
                expression=result.persona.expression,
                strength=cls._expression_strength(result.persona.emotion_intensity),
            ),
            motion=MotionIntent(
                cue=cue,
                style=style,
                disposition=disposition,
            ),
            verified=True,
            persistence_committed=result.persistence.committed,
            persistence_durable=result.persistence.durable,
        )

    @staticmethod
    def _validate_source_cycle(result: CognitiveCycleResponse) -> None:
        if not result.verification_report.is_safe_to_publish:
            raise EmbodimentContractError("Unverified output cannot cross the embodiment boundary.")
        if not result.decision_receipt.verification_passed:
            raise EmbodimentContractError("Decision receipt is not verified for embodiment.")
        if not result.persistence.committed:
            raise EmbodimentContractError("Uncommitted output cannot cross the embodiment boundary.")
        if result.expression != result.persona.expression:
            raise EmbodimentContractError("Legacy and typed character expressions diverged.")
        if result.portrait_path != result.persona.portrait_path:
            raise EmbodimentContractError("Legacy and typed portrait paths diverged.")
        if not result.response_text.strip():
            raise EmbodimentContractError("Empty speech cannot cross the embodiment boundary.")

    @staticmethod
    def _interaction_id(decision_id: str) -> str:
        suffix = decision_id.removeprefix("dec_")
        return f"interaction_{suffix}"

    @staticmethod
    def _speech_delivery(emotion: Emotion) -> SpeechDelivery:
        mapping = {
            Emotion.SUPPORTIVE: SpeechDelivery.SUPPORTIVE,
            Emotion.CONFIDENT: SpeechDelivery.CONFIDENT,
            Emotion.CAUTIOUS: SpeechDelivery.CAUTIOUS,
            Emotion.ENCOURAGING: SpeechDelivery.ENCOURAGING,
            Emotion.CELEBRATORY: SpeechDelivery.ENCOURAGING,
            Emotion.EMPATHETIC: SpeechDelivery.EMPATHETIC,
            Emotion.CONCERNED: SpeechDelivery.CAUTIOUS,
        }
        return mapping.get(emotion, SpeechDelivery.NEUTRAL)

    @staticmethod
    def _expression_strength(intensity: AffectIntensity) -> ExpressionStrength:
        mapping = {
            AffectIntensity.NONE: ExpressionStrength.NONE,
            AffectIntensity.SUBTLE: ExpressionStrength.SUBTLE,
            AffectIntensity.MODERATE: ExpressionStrength.MODERATE,
            AffectIntensity.STRONG: ExpressionStrength.STRONG,
        }
        return mapping[intensity]

    @staticmethod
    def _motion_cue(result: CognitiveCycleResponse) -> tuple[MotionCue, MotionStyle]:
        emotion = result.persona.emotion
        if emotion in {Emotion.SUPPORTIVE, Emotion.EMPATHETIC}:
            return MotionCue.ACKNOWLEDGE, MotionStyle.RESTRAINED
        if emotion == Emotion.CONFIDENT:
            return MotionCue.PRESENT, MotionStyle.RESTRAINED
        if emotion in {Emotion.CAUTIOUS, Emotion.CONCERNED}:
            return MotionCue.CAUTION, MotionStyle.RESTRAINED
        if emotion in {Emotion.ENCOURAGING, Emotion.CELEBRATORY}:
            return MotionCue.CELEBRATE, MotionStyle.STANDARD
        if result.persona.expression == "analyzing":
            return MotionCue.THINK, MotionStyle.RESTRAINED
        if result.persona.expression == "focused":
            return MotionCue.LISTEN, MotionStyle.RESTRAINED
        return MotionCue.NONE, MotionStyle.RESTRAINED
