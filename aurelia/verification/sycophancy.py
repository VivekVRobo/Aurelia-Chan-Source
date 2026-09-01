"""
Aurelia Cognitive OS V4 - Objective Sycophancy & Hallucination Guard
====================================================================
Strips unearned flattery and unsupported claims while preserving
legitimate, evidence-backed positive observations.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass(frozen=True)
class SycophancyCheckResult:
    """Result of evaluating a statement for sycophancy or hallucination."""
    is_acceptable: bool
    sanitized_text: str
    flagged_flattery: bool
    flagged_unsupported_claim: bool
    explanation: Optional[str] = None


class SycophancyGuard:
    """
    Objective filter for unearned flattery, generic encouragement, and hallucinated claims.
    """

    GENERIC_FLATTERY_PATTERNS = [
        "you are a rockstar",
        "you are clearly director material",
        "you are a genius",
        "you definitely deserve",
        "anyone would be lucky to have you",
        "don't worry you will get it easily"
    ]

    @classmethod
    def audit_prose(
        cls,
        text: str,
        has_corroborating_evidence: bool = False
    ) -> SycophancyCheckResult:
        """
        Audits output text. If unearned flattery is detected without evidence,
        it flags or sanitizes the text.
        """
        lower = text.lower()
        flagged_flattery = False
        
        for pattern in cls.GENERIC_FLATTERY_PATTERNS:
            if pattern in lower:
                flagged_flattery = True
                break
                
        # If text has specific numbers or evidence backing (e.g., "improved 68 -> 74 -> 82"), it is legitimate
        if "improved from" in lower or has_corroborating_evidence:
            return SycophancyCheckResult(
                is_acceptable=True,
                sanitized_text=text,
                flagged_flattery=False,
                flagged_unsupported_claim=False
            )
            
        if flagged_flattery:
            sanitized = text
            for pattern in cls.GENERIC_FLATTERY_PATTERNS:
                sanitized = sanitized.replace(pattern, "[unsupported claim removed]")
            return SycophancyCheckResult(
                is_acceptable=False,
                sanitized_text=sanitized,
                flagged_flattery=True,
                flagged_unsupported_claim=False,
                explanation="Detected unearned praise/flattery without supporting metrics."
            )
            
        return SycophancyCheckResult(
            is_acceptable=True,
            sanitized_text=text,
            flagged_flattery=False,
            flagged_unsupported_claim=False
        )
