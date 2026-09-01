"""
Aurelia Cognitive OS V4 - Privacy & Sensitive Data Protection
==============================================================
Ensures local-only bindings, redacts sensitive personal identifiers in logs,
and enforces data privacy boundaries.
"""

import re
from typing import Dict, Any


class PrivacyGuard:
    """
    Masks sensitive personal data in logs and maintains local storage privacy.
    """

    PHONE_REGEX = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
    EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

    @classmethod
    def redact_sensitive_text(cls, text: str) -> str:
        """Masks emails and phone numbers from debug log streams."""
        redacted = cls.EMAIL_REGEX.sub("[EMAIL REDACTED]", text)
        redacted = cls.PHONE_REGEX.sub("[PHONE REDACTED]", redacted)
        return redacted
