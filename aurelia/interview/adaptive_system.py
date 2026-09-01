"""
Aurelia Cognitive OS V5 - Adaptive Diagnostic Interview System
===============================================================
Selects interview scenarios dynamically to maximize diagnostic Information Gain
over unmeasured, high-uncertainty competency gaps.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple


@dataclass(frozen=True)
class InterviewQuestionNode:
    """Interview question with target competency tags and diagnostic power."""
    question_id: str
    scenario_title: str
    target_competency: str
    prompt_text: str
    diagnostic_power: float # 0.0 to 1.0 (ability to distinguish skill level)
    difficulty_level: str # "Senior", "Director", "VP", "Executive"


class AdaptiveInterviewEngine:
    """
    Diagnostic question selector based on Information Gain.
    """

    def __init__(self):
        self.question_bank: List[InterviewQuestionNode] = self._load_default_bank()

    def _load_default_bank(self) -> List[InterviewQuestionNode]:
        """Loads canonical executive scenario bank."""
        return [
            InterviewQuestionNode(
                question_id="q_comp_neg",
                scenario_title="High-Stakes Salary Negotiation",
                target_competency="financial_negotiation",
                prompt_text="The hiring manager offers a package 15% below your target. How do you negotiate?",
                diagnostic_power=0.92,
                difficulty_level="Director"
            ),
            InterviewQuestionNode(
                question_id="q_budget_cut",
                scenario_title="Critical P&L Budget Reduction",
                target_competency="budget_governance",
                prompt_text="You must cut your departmental OPEX by 22% within 60 days without missing key roadmap SLAs. How do you prioritize?",
                diagnostic_power=0.95,
                difficulty_level="VP"
            ),
            InterviewQuestionNode(
                question_id="q_exec_conflict",
                scenario_title="Executive Alignment & Conflict",
                target_competency="stakeholder_alignment",
                prompt_text="A senior VP publicly dismisses your proposal in a board meeting. How do you respond?",
                diagnostic_power=0.88,
                difficulty_level="Director"
            ),
            InterviewQuestionNode(
                question_id="q_org_scaling",
                scenario_title="Rapid Organizational Restructuring",
                target_competency="org_scaling",
                prompt_text="Your engineering org must scale from 35 to 140 across 3 timezones in 9 months. What is your management topology?",
                diagnostic_power=0.90,
                difficulty_level="VP"
            )
        ]

    def select_next_question(
        self,
        known_competency_confidence: Dict[str, float], # competency_id -> confidence (0.0 to 1.0)
        asked_question_ids: List[str]
    ) -> Optional[InterviewQuestionNode]:
        """
        Selects next question that maximizes Information Gain:
        IG = (1.0 - confidence) * diagnostic_power.
        """
        unasked = [q for q in self.question_bank if q.question_id not in asked_question_ids]
        if not unasked:
            return None

        def calc_ig(q: InterviewQuestionNode) -> float:
            conf = known_competency_confidence.get(q.target_competency, 0.20)
            uncertainty = 1.0 - conf
            return uncertainty * q.diagnostic_power

        return max(unasked, key=calc_ig)
