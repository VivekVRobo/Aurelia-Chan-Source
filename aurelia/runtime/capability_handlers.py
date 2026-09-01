"""Concrete handlers used by the Aurelia cognitive DAG."""

from __future__ import annotations

import re
from typing import Any

from aurelia.artifacts.schemas import ArtifactMilestone, ArtifactWorkspaceCompiler
from aurelia.cognition.critic import EvidenceCritic, RiskCritic, StrategicCritic
from aurelia.cognition.hypotheses import CognitiveSearchEngine, StrategicHypothesis
from aurelia.contracts.meaning_frame import IntentType
from aurelia.llm.ollama_cortex import LocalOllamaCortex
from aurelia.llm.response_renderer import RenderedResponse, ResponseStyle, ResponseTone
from aurelia.solvers.numerical import EquityGrant, Money, NumericalFirewall
from aurelia.solvers.simulation import MonteCarloSimulator
from aurelia.verification.firewall import MasterVerificationFirewall


def memory_lookup_fast(*, context: Any, dependencies: dict[str, Any]) -> dict[str, Any]:
    del dependencies
    if not context.grounded.memories:
        return {"found": False, "item": None}
    item = context.grounded.memories[0]
    return {"found": True, "item": item, "score": item.composite_score}


def response_format_direct(*, context: Any, dependencies: dict[str, Any]) -> dict[str, Any]:
    memory = dependencies.get("mem_lookup", {})
    if memory.get("found"):
        item = memory["item"]
        return _apply_persona(
            context=context,
            response_text=f"The most relevant stored context is: {item.content}",
            cognitive_state="FOCUSED",
            confidence=max(55.0, min(95.0, item.composite_score * 100.0)),
            renderer="GroundedMemoryFormatter",
        )
    return _apply_persona(
        context=context,
        response_text="I do not have a grounded stored value for that yet.",
        cognitive_state="FOCUSED",
        confidence=55.0,
        renderer="GroundedMemoryFormatter",
    )


def parse_offer(*, context: Any, dependencies: dict[str, Any]) -> dict[str, Any]:
    del dependencies
    text = context.user_text
    values = _money_values(text)
    base = _money_near_label(text, "base")
    equity = _money_near_label(text, "equity")
    valuation = _money_near_label(text, "valuation")
    signing = _money_near_label(text, "signing")
    if base is None and values:
        base = values[0]
    if equity is None and len(values) >= 2:
        equity = values[-1]

    bonus_match = re.search(
        r"(\d+(?:\.\d+)?)\s*%\s*(?:target\s+)?bonus|"
        r"bonus[^\d]{0,12}(\d+(?:\.\d+)?)\s*%",
        text,
        re.IGNORECASE,
    )
    bonus_pct = 0.0
    if bonus_match:
        bonus_pct = float(next(group for group in bonus_match.groups() if group is not None))

    ownership = re.search(r"(\d+(?:\.\d+)?)\s*%\s*(?:equity|ownership)", text, re.IGNORECASE)
    return {
        "base_salary": base,
        "bonus_pct": bonus_pct,
        "annual_equity_value": equity or 0.0,
        "signing_bonus": signing or 0.0,
        "ownership_pct": float(ownership.group(1)) if ownership else None,
        "company_valuation": valuation,
    }


def retrieve_hybrid(*, context: Any, dependencies: dict[str, Any]) -> Any:
    del dependencies
    return context.grounded


def calculate_total_target(*, context: Any, dependencies: dict[str, Any]) -> dict[str, Any]:
    del context
    offer = dependencies["parse_offer"]
    base = offer.get("base_salary")
    if base is None:
        return {"applicable": False, "total_annual_usd": None, "numeric_checks": []}
    total = NumericalFirewall.calculate_total_target_compensation(
        Money(float(base), "USD", "year"),
        float(offer.get("bonus_pct", 0.0)),
        float(offer.get("annual_equity_value", 0.0)),
        float(offer.get("signing_bonus", 0.0)),
    ).amount
    return {
        "applicable": True,
        "total_annual_usd": total,
        "numeric_checks": [("Total Target Compensation Calculation", total, total)],
    }


def simulate_equity(*, context: Any, dependencies: dict[str, Any]) -> dict[str, Any]:
    offer = dependencies["parse_offer"]
    ownership = offer.get("ownership_pct")
    valuation = offer.get("company_valuation")
    if ownership is None or valuation is None:
        return {"applicable": False, "reason": "Ownership and valuation were not provided."}
    mode = "fast" if context.budget.max_simulations <= 250 else "standard"
    if context.budget.max_simulations >= 5000:
        mode = "deep"
    distribution = MonteCarloSimulator.simulate_startup_equity_outcomes(
        EquityGrant(ownership_percentage=float(ownership) / 100.0),
        base_valuation_usd=float(valuation),
        budget_mode=mode,
    )
    return {"applicable": True, "distribution": distribution}


def search_hypotheses(*, context: Any, dependencies: dict[str, Any]) -> tuple[Any, ...]:
    total = float(dependencies["comp_model"].get("total_annual_usd") or 0.0)
    candidates = [
        StrategicHypothesis(
            id="request_more_evidence",
            strategy_type="Evidence_First",
            title="Gather missing evidence before deciding",
            assumptions=("Additional evidence can be obtained",),
            actions=("Gather evidence",),
            expected_value_usd=total,
            strategic_value_score=0.75,
            reversibility_score=0.95,
            risk_penalty=0.10,
            time_to_value_months=1.0,
            effort_cost=0.15,
            uncertainty_penalty=0.10,
            confidence=0.80,
        ),
        StrategicHypothesis(
            id="proceed_with_current_evidence",
            strategy_type="Proceed_Current",
            title="Proceed using current verified inputs",
            assumptions=("Current inputs are sufficient for the decision",),
            actions=("Proceed with current evidence",),
            expected_value_usd=total,
            strategic_value_score=0.70,
            reversibility_score=0.60,
            risk_penalty=0.25,
            time_to_value_months=0.5,
            effort_cost=0.05,
            uncertainty_penalty=0.25,
            confidence=0.75,
        ),
    ]
    return tuple(
        CognitiveSearchEngine.evaluate_and_rank(
            candidates,
            user_hard_constraints=[],
            user_known_skills=[],
            beam_width=min(3, context.budget.max_plan_nodes),
        )
    )


def evaluate_critics(*, context: Any, dependencies: dict[str, Any]) -> dict[str, Any]:
    hypotheses = dependencies["gen_hypotheses"]
    evaluations = []
    for hypothesis in hypotheses:
        critiques = (
            StrategicCritic.critique(hypothesis, context.target_role),
            RiskCritic.critique(hypothesis),
            EvidenceCritic.critique(hypothesis),
        )
        evaluations.append(
            {
                "hypothesis": hypothesis,
                "critiques": critiques,
                "passed": all(critique.passed for critique in critiques),
            }
        )
    selected = next(
        (entry["hypothesis"] for entry in evaluations if entry["passed"]),
        hypotheses[0] if hypotheses else None,
    )
    return {"evaluations": tuple(evaluations), "selected": selected}


def evaluate_specialist(*, context: Any, dependencies: dict[str, Any]) -> dict[str, Any]:
    del dependencies
    response, state, confidence, specialists, numeric_checks = (
        LocalOllamaCortex.synthesize_deterministic_response(
            user_text=context.user_text,
            intent=context.intent,
            entities=context.entities,
            user_role=context.user_role,
            target_role=context.target_role,
        )
    )
    return {
        "response_text": response,
        "cognitive_state": state,
        "confidence": confidence,
        "specialists": tuple(specialists),
        "numeric_checks": tuple(numeric_checks),
    }


def render_response(*, context: Any, dependencies: dict[str, Any]) -> dict[str, Any]:
    specialist = dependencies.get("evaluate_specialist")
    grounded = context.grounded.render_for_model()
    model_response = LocalOllamaCortex.query_local_model(
        context.user_text,
        "\n".join(
            (
                f"Current role: {context.user_role}",
                f"Target role: {context.target_role}",
                grounded,
            )
        ),
    )
    if model_response:
        return _apply_persona(
            context=context,
            response_text=model_response,
            cognitive_state="CONFIDENT",
            confidence=92.0,
            renderer="LocalOllamaCortex",
        )
    if specialist:
        return _apply_persona(
            context=context,
            response_text=str(specialist["response_text"]),
            cognitive_state=str(specialist["cognitive_state"]),
            confidence=float(specialist["confidence"]),
            renderer="DeterministicSpecialist",
        )
    response, state, confidence, _, _ = LocalOllamaCortex.synthesize_deterministic_response(
        user_text=context.user_text,
        intent=context.intent,
        entities=context.entities,
        user_role=context.user_role,
        target_role=context.target_role,
    )
    return _apply_persona(
        context=context,
        response_text=response,
        cognitive_state=state,
        confidence=confidence,
        renderer="DeterministicResponseSynthesizer",
    )


def verify_response(*, context: Any, dependencies: dict[str, Any]) -> Any:
    rendered = dependencies.get("renderer") or dependencies.get("render_response")
    if rendered is None:
        raise ValueError("Verification requires a rendered response.")
    comp = dependencies.get("comp_model", {})
    return MasterVerificationFirewall.verify(
        prose_text=str(rendered["response_text"]),
        numeric_checks=list(comp.get("numeric_checks", [])) or None,
        has_evidence=context.grounded.has_corroborating_evidence,
    )


def create_artifact(*, context: Any, dependencies: dict[str, Any]) -> tuple[Any, ...]:
    report = dependencies["firewall"]
    if not report.is_safe_to_publish or context.intent != IntentType.COMPENSATION_STRATEGY:
        return ()
    milestones = [
        ArtifactMilestone(
            "m1",
            "Evidence Review",
            "Review the verified package inputs",
            ("Confirm package facts",),
            ("Verified inputs",),
        ),
        ArtifactMilestone(
            "m2",
            "Decision Record",
            "Document the selected next action",
            ("Record the decision",),
            ("Decision record",),
        ),
    ]
    artifact = ArtifactWorkspaceCompiler.create_90_day_roadmap(
        artifact_id=f"art_{context.snapshot.snapshot_id}",
        title="Executive Counter-Offer Strategy & Script",
        decision_id=f"pending_{context.snapshot.snapshot_id}",
        milestones=milestones,
    )
    return (artifact,)


def _apply_persona(
    *,
    context: Any,
    response_text: str,
    cognitive_state: str,
    confidence: float,
    renderer: str,
) -> dict[str, Any]:
    base_response = RenderedResponse(
        content=response_text,
        style=ResponseStyle.PROFESSIONAL,
        tone=_response_tone(cognitive_state),
        sections=[response_text],
        metadata={"renderer": renderer},
    )
    persona = context.persona_renderer.render_with_persona(
        base_response=base_response,
        user_message=context.user_text,
        context=f"{context.intent.value} {context.user_text}",
        cognitive_state=cognitive_state,
        evidence_available=context.grounded.has_corroborating_evidence,
    )
    return {
        "response_text": persona.content,
        "cognitive_state": cognitive_state,
        "confidence": confidence,
        "renderer": renderer,
        "persona_renderer": "PersonaRenderer",
        "persona": persona,
    }


def _response_tone(cognitive_state: str) -> ResponseTone:
    state = cognitive_state.upper()
    if "CONFIDENT" in state or "APPROVAL" in state:
        return ResponseTone.CONFIDENT
    if "CONCERN" in state or "CAUTIOUS" in state or "SKEPTICAL" in state:
        return ResponseTone.CAUTIOUS
    if "EMPATH" in state:
        return ResponseTone.EMPATHETIC
    return ResponseTone.NEUTRAL


def _money_values(text: str) -> list[float]:
    values = []
    for raw, suffix in re.findall(r"\$\s*([\d,.]+)\s*([kKmM]?)", text):
        amount = float(raw.replace(",", ""))
        if suffix.lower() == "k":
            amount *= 1_000.0
        elif suffix.lower() == "m":
            amount *= 1_000_000.0
        values.append(amount)
    return values


def _money_near_label(text: str, label: str) -> float | None:
    patterns = (
        rf"{label}[^$\d]{{0,20}}\$\s*([\d,.]+)\s*([kKmM]?)",
        rf"\$\s*([\d,.]+)\s*([kKmM]?)[^\n,.]{{0,20}}{label}",
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount = float(match.group(1).replace(",", ""))
            if match.group(2).lower() == "k":
                amount *= 1_000.0
            elif match.group(2).lower() == "m":
                amount *= 1_000_000.0
            return amount
    return None
