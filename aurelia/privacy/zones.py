"""
Aurelia Cognitive OS V6 - Privacy Zones & Pre-Capture Firewall
===============================================================
Enforces strict pre-capture exclusion of password managers, banking apps,
incognito windows, and restricted paths before any perception occurs.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Set, Tuple
from aurelia.contracts.v6_contracts import PrivacyClass


@dataclass(frozen=True)
class PrivacyCheckResult:
    """Outcome of pre-capture privacy policy evaluation."""
    is_capture_allowed: bool
    privacy_class: PrivacyClass
    matched_denial_rule: Optional[str]
    rationale: str


class PrivacyFirewall:
    """
    Pre-capture firewall evaluating processes, window titles, and file paths.
    """

    DENIED_PROCESSES: Set[str] = {
        "1password.exe",
        "bitwarden.exe",
        "keepass.exe",
        "lastpass.exe",
        "enpass.exe",
        "authy.exe"
    }

    DENIED_TITLE_KEYWORDS: List[str] = [
        "incognito",
        "private browsing",
        "inprivate",
        "bank",
        "chase online",
        "wellsfargo",
        "netbanking",
        "password manager"
    ]

    DENIED_PATH_PATTERNS: List[str] = [
        "/.ssh/",
        "/.aws/",
        "/passwords",
        "/tax_returns",
        "/confidential_personal"
    ]

    @classmethod
    def evaluate_pre_capture(
        cls,
        process_name: Optional[str] = None,
        window_title: Optional[str] = None,
        file_path: Optional[str] = None
    ) -> PrivacyCheckResult:
        """
        Evaluates whether perception capture is permitted.
        Enforced strictly BEFORE any screenshot or file read.
        """
        # 1. Check Process Name
        if process_name:
            proc_lower = process_name.lower()
            if proc_lower in cls.DENIED_PROCESSES:
                return PrivacyCheckResult(
                    is_capture_allowed=False,
                    privacy_class=PrivacyClass.DENIED,
                    matched_denial_rule=f"Denied process: {process_name}",
                    rationale="Password manager or authentication tool detected. Pre-capture firewall engaged."
                )

        # 2. Check Window Title
        if window_title:
            title_lower = window_title.lower()
            for kw in cls.DENIED_TITLE_KEYWORDS:
                if kw in title_lower:
                    return PrivacyCheckResult(
                        is_capture_allowed=False,
                        privacy_class=PrivacyClass.DENIED,
                        matched_denial_rule=f"Denied window keyword: '{kw}'",
                        rationale="Private window or banking application detected. Pre-capture firewall engaged."
                    )

        # 3. Check File Path
        if file_path:
            norm_path = file_path.lower().replace('\\', '/')
            for pattern in cls.DENIED_PATH_PATTERNS:
                if pattern in norm_path:
                    return PrivacyCheckResult(
                        is_capture_allowed=False,
                        privacy_class=PrivacyClass.DENIED,
                        matched_denial_rule=f"Denied path pattern: '{pattern}'",
                        rationale="Restricted personal directory detected. Pre-capture firewall engaged."
                    )

        # Approved for capture
        return PrivacyCheckResult(
            is_capture_allowed=True,
            privacy_class=PrivacyClass.PUBLIC,
            matched_denial_rule=None,
            rationale="Pre-capture checks passed. No privacy exclusions matched."
        )
