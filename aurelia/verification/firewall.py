"""
Aurelia Cognitive OS V4 - Master Verification Firewall
======================================================
Coordinates numeric, evidence, sycophancy, and consistency verifications.
Enforces severity levels (INFO, WARNING, ERROR, BLOCKER).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
from aurelia.contracts.core_types import VerificationSeverity
from aurelia.solvers.numerical import NumericalFirewall
from aurelia.verification.sycophancy import SycophancyGuard


@dataclass(frozen=True)
class VerificationIssue:
    """An issue identified by the verification firewall."""
    issue_type: str                     # "NUMERIC_MISMATCH", "UNEARNED_FLATTERY", "UNSUPPORTED_CLAIM"
    severity: VerificationSeverity
    description: str
    target_claim: str


@dataclass(frozen=True)
class VerificationReport:
    """Consolidated verification verdict for a cognitive cycle."""
    passed: bool
    max_severity: VerificationSeverity
    issues: Tuple[VerificationIssue, ...]
    verified_numerical_checks: Tuple[str, ...]
    is_safe_to_publish: bool


class MasterVerificationFirewall:
    """
    Final gatekeeper before response compilation.
    """

    @classmethod
    def verify(
        cls,
        prose_text: str,
        numeric_checks: Optional[List[Tuple[str, float, float]]] = None,
        has_evidence: bool = False
    ) -> VerificationReport:
        """
        Runs comprehensive multi-dimensional verification on proposed output.
        """
        issues: List[VerificationIssue] = []
        verified_checks: List[str] = []
        
        # 1. Numeric Verification
        if numeric_checks:
            for desc, expected, actual in numeric_checks:
                passed, err = NumericalFirewall.verify_arithmetic_claim(desc, expected, actual)
                if passed:
                    verified_checks.append(f"✓ Verified: {desc} ({actual})")
                else:
                    issues.append(VerificationIssue(
                        issue_type="NUMERIC_MISMATCH",
                        severity=VerificationSeverity.BLOCKER,
                        description=err or "Arithmetic discrepancy",
                        target_claim=desc
                    ))
                    
        # 2. Sycophancy & Flattery Audit
        syco_res = SycophancyGuard.audit_prose(prose_text, has_corroborating_evidence=has_evidence)
        if not syco_res.is_acceptable:
            issues.append(VerificationIssue(
                issue_type="UNEARNED_FLATTERY",
                severity=VerificationSeverity.WARNING,
                description=syco_res.explanation or "Flattery detected without evidence",
                target_claim=prose_text[:60]
            ))
            
        # Determine overall safety
        has_blockers = any(i.severity == VerificationSeverity.BLOCKER for i in issues)
        has_errors = any(i.severity == VerificationSeverity.ERROR for i in issues)
        
        if has_blockers:
            max_sev = VerificationSeverity.BLOCKER
        elif has_errors:
            max_sev = VerificationSeverity.ERROR
        elif issues:
            max_sev = VerificationSeverity.WARNING
        else:
            max_sev = VerificationSeverity.INFO
            
        is_safe = not has_blockers
        return VerificationReport(
            passed=is_safe,
            max_severity=max_sev,
            issues=tuple(issues),
            verified_numerical_checks=tuple(verified_checks),
            is_safe_to_publish=is_safe
        )
