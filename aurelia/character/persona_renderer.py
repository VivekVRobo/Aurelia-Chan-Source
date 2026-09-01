"""Aurelia persona renderer for final user-visible responses.

This module is the character boundary between cognitive content and Aurelia's
affect, expression style, and character state. Persona rendering may shape
presentation, but it must not invent evidence or bypass the final verification
firewall.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aurelia.character.affect_engine import (
    AffectEngine,
    AffectIntensity,
    AffectSuggestion,
    Emotion,
)
from aurelia.character.aurelia_state import AureliaStateManager
from aurelia.character.expression_policy import ExpressionPolicyManager, ExpressionStyle
from aurelia.contracts.core_types import VerificationSeverity
from aurelia.llm.response_renderer import RenderedResponse


@dataclass
class PersonaRenderedResponse:
    """Final response plus the character state that produced it."""

    content: str
    emotion: Emotion
    emotion_intensity: AffectIntensity
    expression_style: ExpressionStyle
    mode: str
    traits: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


class PersonaRenderer:
    """Apply Aurelia's real affect, expression policy, and state manager."""

    EXPRESSION_MAP = {
        "neutral": ("01. Neutral / Observing", "01-neutral-observing.png"),
        "confident": ("02. Subtle Confident Smile", "02-subtle-confident-smile.png"),
        "approval": ("03. Soft Approval", "03-soft-approval.png"),
        "focused": ("04. Focused Listening", "04-focused-listening.png"),
        "analyzing": ("05. Analyzing (Raised Brow)", "05-analyzing-raised-brow.png"),
        "serious": ("06. Serious", "06-serious.png"),
        "warning": ("07. Strict Warning", "07-strict-warning.png"),
        "disappointed": ("08. Disappointed", "08-disappointed.png"),
        "skeptical": ("09. Skeptical", "09-skeptical.png"),
        "concerned": ("10. Concerned", "10-concerned.png"),
        "empathetic": ("11. Empathetic", "11-empathetic.png"),
    }

    def __init__(self) -> None:
        self.affect_engine = AffectEngine()
        self.expression_manager = ExpressionPolicyManager()
        self.state_manager = AureliaStateManager()
        self.state_manager.initialize_state()

    def render_with_persona(
        self,
        base_response: RenderedResponse,
        user_message: str,
        context: str | None = None,
        *,
        cognitive_state: str | None = None,
        evidence_available: bool = False,
    ) -> PersonaRenderedResponse:
        """Render the final text and record the character state used."""
        character_context = context or "standard interaction"
        suggested = self.affect_engine.suggest_affect(
            user_message=user_message,
            context=character_context,
        )
        suggested = self._combine_with_cognitive_state(
            suggested,
            cognitive_state=cognitive_state,
            evidence_available=evidence_available,
        )
        calibrated = self.affect_engine.calibrate_emotional_response(
            suggested,
            professional_constraint=True,
        )
        self.affect_engine.update_emotional_state(
            emotion=calibrated.suggested_emotion,
            intensity=calibrated.suggested_intensity,
            context=character_context,
        )

        adapted_policy = self.expression_manager.adapt_for_context(character_context)
        mode = self.state_manager.get_mode_for_context(character_context)
        self.state_manager.update_mode(mode=mode, context=character_context)

        characterized = self._apply_emotional_expression(
            base_response.content,
            calibrated.suggested_emotion,
            calibrated.suggested_intensity,
        )
        styled = self._apply_expression_style(characterized, adapted_policy.style)

        # Compliance is checked on the *final* persona text, never the pre-persona draft.
        compliance = self.expression_manager.check_compliance(styled)
        violations = tuple(str(item) for item in compliance["violations"])
        blocking_violations = self._blocking_policy_violations(violations)
        active_traits = self.state_manager.get_active_traits()
        return PersonaRenderedResponse(
            content=styled,
            emotion=calibrated.suggested_emotion,
            emotion_intensity=calibrated.suggested_intensity,
            expression_style=adapted_policy.style,
            mode=mode.value,
            traits=[trait.value for trait in active_traits],
            metadata={
                "affect_reasoning": calibrated.reasoning,
                "affect_confidence": calibrated.confidence,
                "evidence_available": evidence_available,
                "cognitive_state": cognitive_state,
                "compliant": bool(compliance["compliant"]),
                "publish_compliant": not blocking_violations,
                "compliance_score": float(compliance["compliance_score"]),
                "violations": violations,
                "blocking_violations": blocking_violations,
                "warnings": tuple(str(item) for item in compliance["warnings"]),
            },
        )

    @classmethod
    def resolve_expression(
        cls,
        *,
        emotion: Emotion,
        cognitive_state: str,
        verification_severity: VerificationSeverity,
    ) -> tuple[str, str]:
        """Resolve canonical expression with verification severity as the final veto."""
        if verification_severity == VerificationSeverity.BLOCKER:
            key = "warning"
        elif verification_severity == VerificationSeverity.ERROR:
            key = "serious"
        elif emotion in {Emotion.SUPPORTIVE, Emotion.EMPATHETIC}:
            key = "empathetic"
        elif emotion in {Emotion.ENCOURAGING, Emotion.CELEBRATORY}:
            key = "approval"
        elif emotion == Emotion.CONFIDENT:
            key = "confident"
        elif emotion == Emotion.CAUTIOUS:
            key = "skeptical"
        elif emotion == Emotion.CONCERNED:
            key = "concerned"
        else:
            state_upper = cognitive_state.upper()
            if "WARNING" in state_upper or "ENTITLED" in state_upper:
                key = "warning"
            elif "DISAPPOINTED" in state_upper or "UNPREPARED" in state_upper:
                key = "disappointed"
            elif "SKEPTICAL" in state_upper or "UNVERIFIED" in state_upper:
                key = "skeptical"
            elif "BURNOUT" in state_upper or "CONCERNED" in state_upper:
                key = "concerned"
            elif "ANALYZING" in state_upper or "CALCULATING" in state_upper:
                key = "analyzing"
            elif "SERIOUS" in state_upper or "REORG" in state_upper:
                key = "serious"
            elif "APPROVAL" in state_upper or "HIGH_METRIC" in state_upper:
                key = "approval"
            elif "CONFIDENT" in state_upper or "VERIFIED_PLAN" in state_upper:
                key = "confident"
            elif "EMPATHETIC" in state_upper or "PIVOT" in state_upper:
                key = "empathetic"
            elif "LISTENING" in state_upper or "FOCUSED" in state_upper:
                key = "focused"
            else:
                key = "neutral"
        return key, f"aurelia-expressions/{cls.EXPRESSION_MAP[key][1]}"

    @staticmethod
    def _combine_with_cognitive_state(
        suggestion: AffectSuggestion,
        *,
        cognitive_state: str | None,
        evidence_available: bool,
    ) -> AffectSuggestion:
        """Use cognitive confidence only when user affect did not provide a stronger signal."""
        if suggestion.suggested_emotion != Emotion.NEUTRAL:
            return suggestion
        if cognitive_state and cognitive_state.upper() == "CONFIDENT":
            return AffectSuggestion(
                suggested_emotion=Emotion.CONFIDENT,
                suggested_intensity=AffectIntensity.SUBTLE,
                reasoning="Cognitive result is confident; use restrained confident delivery.",
                confidence=max(0.75, suggestion.confidence),
                alternatives=[Emotion.NEUTRAL],
            )
        if (
            not evidence_available
            and cognitive_state
            and cognitive_state.upper()
            in {
                "UNCERTAIN",
                "CAUTIOUS",
            }
        ):
            return AffectSuggestion(
                suggested_emotion=Emotion.CAUTIOUS,
                suggested_intensity=AffectIntensity.SUBTLE,
                reasoning="Cognitive state is uncertain and evidence is limited.",
                confidence=max(0.75, suggestion.confidence),
                alternatives=[Emotion.NEUTRAL],
            )
        return suggestion

    @staticmethod
    def _blocking_policy_violations(violations: tuple[str, ...]) -> tuple[str, ...]:
        """Return only policy failures that make the characterized text unsafe to publish.

        The legacy expression policy also flags broad stylistic words such as
        "never". Those are useful review signals but are not automatically unsafe.
        Explicit promises and guarantees are publish blockers.
        """
        blocking_markers = (
            "guarantee",
            "promise",
            "absolutely certain",
            "overpromising language: 'absolutely'",
            "overpromising language: 'definitely'",
            "overpromising language: 'certainly'",
        )
        return tuple(
            violation
            for violation in violations
            if any(marker in violation.lower() for marker in blocking_markers)
        )

    def _apply_emotional_expression(
        self,
        content: str,
        emotion: Emotion,
        intensity: AffectIntensity,
    ) -> str:
        """Apply bounded emotional framing without introducing outcome claims."""
        if intensity == AffectIntensity.NONE:
            return content

        prefixes = {
            Emotion.SUPPORTIVE: {
                AffectIntensity.SUBTLE: "I understand.",
                AffectIntensity.MODERATE: "I understand this is challenging.",
                AffectIntensity.STRONG: "I understand this is a difficult situation.",
            },
            Emotion.ENCOURAGING: {
                AffectIntensity.SUBTLE: "There is useful momentum to assess.",
                AffectIntensity.MODERATE: "There is meaningful progress to assess here.",
                AffectIntensity.STRONG: "There is significant progress to assess here.",
            },
            Emotion.EMPATHETIC: {
                AffectIntensity.SUBTLE: "I understand this matters to you.",
                AffectIntensity.MODERATE: "I understand this situation matters to you.",
                AffectIntensity.STRONG: "I understand this is an important situation for you.",
            },
            Emotion.CONFIDENT: {
                AffectIntensity.SUBTLE: "I can give you a structured assessment.",
                AffectIntensity.MODERATE: "I can give you a clear, structured assessment.",
                AffectIntensity.STRONG: "I can give you a rigorous, structured assessment.",
            },
            Emotion.CAUTIOUS: {
                AffectIntensity.SUBTLE: "This needs careful evaluation.",
                AffectIntensity.MODERATE: "This needs careful evaluation before acting.",
                AffectIntensity.STRONG: "This needs a careful evidence review before acting.",
            },
            Emotion.CONCERNED: {
                AffectIntensity.SUBTLE: "There is a risk signal worth examining.",
                AffectIntensity.MODERATE: "There are risk signals worth examining carefully.",
                AffectIntensity.STRONG: "There are material risk signals that need review.",
            },
        }
        prefix = prefixes.get(emotion, {}).get(intensity, "")
        return f"{prefix}\n\n{content}" if prefix else content

    @staticmethod
    def _apply_expression_style(content: str, style: ExpressionStyle) -> str:
        """Apply deterministic surface-style transformations only."""
        if style == ExpressionStyle.FORMAL:
            content = content.replace("you're", "you are")
            content = content.replace("don't", "do not")
            content = content.replace("can't", "cannot")
        elif style == ExpressionStyle.CONVERSATIONAL:
            if not content.endswith(("!", "?", ".")):
                content += "."
        elif style == ExpressionStyle.MENTORIAL:
            if content and not any(word in content.lower() for word in ["you", "your"]):
                content = "For you, " + content[0].lower() + content[1:]
        return content

    def adjust_engagement(self, level: float) -> None:
        """Adjust Aurelia's engagement level."""
        self.state_manager.update_engagement(level)

    def get_character_summary(self) -> dict[str, Any]:
        """Return the current character-engine state."""
        return {
            "affect": self.affect_engine.get_summary(),
            "expression": self.expression_manager.get_summary(),
            "state": self.state_manager.get_summary(),
            "character_description": self.state_manager.get_character_description(),
        }

    def get_voice_profile(self) -> str:
        """Return Aurelia's current voice-profile description."""
        if not self.state_manager.current_state:
            return "Aurelia: Executive Career Mentor"
        current_emotion = (
            self.affect_engine.current_state.primary_emotion.value
            if self.affect_engine.current_state
            else "None"
        )
        traits = ", ".join(trait.value for trait in self.state_manager.current_state.active_traits)
        return (
            "Aurelia Voice Profile:\n"
            f"- Mode: {self.state_manager.current_state.current_mode.value}\n"
            f"- Active Traits: {traits}\n"
            f"- Engagement: {self.state_manager.current_state.engagement_level:.0%}\n"
            f"- Current Mood: {self.state_manager.current_state.mood}\n"
            f"- Expression Style: {self.expression_manager.current_policy.style.value}\n"
            f"- Current Emotion: {current_emotion}"
        )
