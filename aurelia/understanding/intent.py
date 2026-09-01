"""
Aurelia Cognitive OS V4 - Intent & Semantic Meaning Engine
===========================================================
Deep classification of user intent across 10+ executive strategic domains
with entity extraction and contextual categorization.
"""

import re
from typing import Dict, Any, List, Tuple
from aurelia.contracts.meaning_frame import IntentType


class SemanticMeaningEngine:
    """
    Classifies user intent and extracts financial, role, and timeline entities.
    """

    @classmethod
    def analyze(cls, text: str) -> Tuple[IntentType, Dict[str, Any]]:
        """
        Extracts intent, numbers, compensation figures, and entities.
        """
        lower = text.lower()
        entities: Dict[str, Any] = {}

        # Extract monetary figures ($220k, $180,000, 20%, etc.)
        money_matches = re.findall(r'\$?(\d+[\d,]*)\s*([kKmM]|\bmillion\b|\bthousand\b)?', text)
        pct_matches = re.findall(r'(\d+(?:\.\d+)?)\s*%', text)
        hours_matches = re.findall(r'(\d+)\s*(?:hours|hrs)', lower)

        if money_matches:
            entities["money_mentions"] = money_matches
        if pct_matches:
            entities["percentages"] = [float(p) for p in pct_matches]
        if hours_matches:
            entities["work_hours"] = int(hours_matches[0])

        # 1. Burnout & Operational Workload
        if any(k in lower for k in ["burnout", "burnt out", "drained", "exhausted", "75 hours", "60 hours", "calendar audit", "overwhelmed", "workstream"]):
            return IntentType.BURNOUT_TRIAGE, entities

        # 2. Workplace Politics & Conflict
        if any(k in lower for k in ["takes credit", "boss", "bypass", "politics", "vp dismissed", "dispute", "deadlock", "reorganization", "reorg", "culture shift", "toxic"]):
            return IntentType.WORKPLACE_CONFLICT, entities

        # 3. Compensation & Offers
        if any(k in lower for k in ["salary", "comp", "negotiat", "offer", "bonus", "equity", "package", "counter", "rsu", "valuation", "profit sharing"]):
            return IntentType.COMPENSATION_STRATEGY, entities

        # 4. Career Pivots & Transitions
        if any(k in lower for k in ["pivot", "transition", "shift to", "principal to vp", "move to product", "leaving tech", "b2b to ai"]):
            return IntentType.CAREER_ROADMAP, entities

        # 5. Promotion & Leverage
        if any(k in lower for k in ["promot", "raise", "not ready for vp", "sponsorship", "tenure", "quit with an external offer"]):
            return IntentType.CAREER_ROADMAP, entities

        # 6. Resume / Portfolio
        if any(k in lower for k in ["resume", "cv", "portfolio", "bullet", "spearheaded", "orchestrated"]):
            return IntentType.RESUME_AUDIT, entities

        # 7. Interview / Mock
        if any(k in lower for k in ["interview", "scenario", "hiring manager asks", "mock session"]):
            return IntentType.INTERVIEW_PRACTICE, entities

        # 8. Status / Past Memory Lookup
        if any(k in lower for k in ["last score", "my score", "my goal", "where am i"]):
            return IntentType.STATUS_INQUIRY, entities

        return IntentType.GENERAL_MENTORSHIP, entities
