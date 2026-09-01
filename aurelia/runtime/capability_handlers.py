"""Concrete handlers used by the Aurelia cognitive DAG."""

from __future__ import annotations

import re
from typing import Any

from aurelia.artifacts.schemas import ArtifactMilestone, ArtifactWorkspaceCompiler
from aurelia.cognition.critic import EvidenceCritic, RiskCritic, StrategicCritic
from aurelia.cognition.hypotheses import CognitiveSearchEngine, StrategicHypothesis
from aurelia.contracts.meaning_frame import IntentType
from aurelia.llm.ollama_cortex import LocalOllamaCortex
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
        return {
            "response_text": f"The most relevant stored context is: {item.content}",
            "cognitive_state": "FOCUSED",
            "confidence": max(55.0, min(95.0, item.composite_score * 100.0)),
        }
    return {
        "response_text": "I do not have a grounded stored value for that yet.",
        "cognitive_state": "FOCUSED",
        "confidence": 55.0,
    }


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
        return {
            "response_text": model_response,
            "cognitive_state": "CONFIDENT",
            "confidence": 92.0,
            "renderer": "LocalOllamaCortex",
        }
    if specialist:
        return {
            "response_text": specialist["response_text"],
            "cognitive_state": specialist["cognitive_state"],
            "confidence": specialist["confidence"],
            "renderer": "DeterministicSpecialist",
        }
    response, state, confidence, _, _ = LocalOllamaCortex.synthesize_deterministic_response(
        user_text=context.user_text,
        intent=context.intent,
        entities=context.entities,
        user_role=context.user_role,
        target_role=context.target_role,
    )
    return {
        "response_text": response,
        "cognitive_state": state,
        "confidence": confidence,
        "renderer": "DeterministicResponseSynthesizer",
    }


def verify_response(*, context: Any, dependencies: dict[str, Any]) -> Any:
    rendered = dependencies.get("renderer") or dependencies.get("render_response")
    if rendered is None:
        raise ValueError("Verification requires a rendered response.")
    comp = dependencies.get("comp_model", {})
    return MasterVerificationFirewall.verify(
        prose_text=str(rendered["response_text"]),
        numeric_checks=list(comp.get("numeric_checks", [])) or None,
        has_evidence=context.grounded.has_corrr???
    )
