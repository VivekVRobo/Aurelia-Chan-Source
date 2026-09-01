"""Verification capability for rendered DAG responses."""

from __future__ import annotations

from typing import Any

from aurelia.contracts.core_types import VerificationSeverity
from aurelia.verification.firewall import (
    MasterVerificationFirewall,
    VerificationIssue,
    VerificationReport,
)


def verify_rendered_response(
    *,
    context: Any,
    dependencies: dict[str, Any],
) -> VerificationReport:
    """Verify the exact final response for reflex, standard, or deep plans."""
    rendered = (
        dependencies.get("renderer")
        or dependencies.get("render_response")
        or dependencies.get("resp_format")
    )
    if rendered is None:
        raise ValueError("Verification requires a rendered response dependency.")

    comp = dependencies.get("comp_model", {})
    numeric_checks = list(comp.get("numeric_checks", []))
    report = MasterVerificationFirewall.verify(
        prose_text=str(rendered["response_text"]),
        numeric_checks=numeric_checks or None,
        has_evidence=context.grounded.has_corroborating_evidence,
    )

    persona = rendered.get("persona")
    blocking_violations = ()
    if persona is not None:
        blocking_violations = tuple(persona.metadata.get("blocking_violations", ()))
    if not blocking_violations:
        return report

    persona_issue = VerificationIssue(
        issue_type="PERSONA_POLICY_VIOLATION",
        severity=VerificationSeverity.BLOCKER,
        description="Final characterized response violates publish-blocking persona policy: "
        + "; ".join(blocking_violations),
        target_claim=str(rendered["response_text"])[:120],
    )
    return VerificationReport(
        passed=False,
        max_severity=VerificationSeverity.BLOCKER,
        issues=report.issues + (persona_issue,),
        verified_numerical_checks=report.verified_numerical_checks,
        is_safe_to_publish=False,
    )
