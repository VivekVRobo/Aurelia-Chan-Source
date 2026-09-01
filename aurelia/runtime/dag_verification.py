"""Verification capability for rendered DAG responses."""

from __future__ import annotations

from typing import Any

from aurelia.verification.firewall import MasterVerificationFirewall, VerificationReport


def verify_rendered_response(
    *,
    context: Any,
    dependencies: dict[str, Any],
) -> VerificationReport:
    """Verify the actual rendered response for reflex, standard, or deep plans."""
    rendered = (
        dependencies.get("renderer")
        or dependencies.get("render_response")
        or dependencies.get("resp_format")
    )
    if rendered is None:
        raise ValueError("Verification requires a rendered response dependency.")

    comp = dependencies.get("comp_model", {})
    numeric_checks = list(comp.get("numeric_checks", []))
    return MasterVerificationFirewall.verify(
        prose_text=str(rendered["response_text"]),
        numeric_checks=numeric_checks or None,
        has_evidence=context.grounded.has_corroborating_evidence,
    )
