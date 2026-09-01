"""
Aurelia Cognitive OS V6 - Scene-Based Cognitive Router with Candidate Sets
===========================================================================
Parameterizes underspecified user queries by compiling and ranking ContextCandidateSet,
enforcing confidence separation guards before routing.
"""

from typing import Dict, Any, List, Optional, Tuple
from aurelia.contracts.v6_contracts import (
    ContextCandidate,
    ContextCandidateSet
)


class SceneBasedCognitiveRouter:
    """
    Evaluates environmental scene evidence to route contextual queries safely.
    """

    @classmethod
    def rank_context_candidates(
        cls,
        user_query: str,
        active_window_title: str,
        active_process_name: str,
        visible_text_snippet: Optional[str] = None
    ) -> ContextCandidateSet:
        """
        Compiles ranked candidate contexts and calculates separation ratio.
        """
        candidates: List[ContextCandidate] = []
        win_lower = active_window_title.lower()
        proc_lower = active_process_name.lower()
        text_lower = (visible_text_snippet or "").lower()

        # 1. VS Code / Programming Debugging Context
        if "code" in proc_lower or "visual studio" in win_lower or ".py" in win_lower or "traceback" in text_lower:
            conf = 0.92 if ("traceback" in text_lower or "error" in text_lower or "exception" in text_lower) else 0.75
            candidates.append(ContextCandidate(
                context_key="vscode_python_debugging",
                description="Python traceback or code editor buffer visible in VS Code",
                confidence_score=conf,
                evidence_refs=("win_title_vscode", "editor_text_snippet")
            ))

        # 2. Resume / Career Audit Context
        if "resume" in win_lower or "cv" in win_lower or "experience" in text_lower:
            candidates.append(ContextCandidate(
                context_key="resume_audit",
                description="Resume or curriculum vitae open in active document viewer",
                confidence_score=0.90,
                evidence_refs=("win_title_resume",)
            ))

        # 3. Compensation / Offer Letter Context
        if "offer" in win_lower or "salary" in text_lower or "compensation" in win_lower:
            candidates.append(ContextCandidate(
                context_key="salary_negotiation",
                description="Offer letter or compensation document open in active viewport",
                confidence_score=0.88,
                evidence_refs=("win_title_offer",)
            ))

        # 4. Terminal Context
        if "cmd" in proc_lower or "powershell" in proc_lower or "terminal" in win_lower:
            candidates.append(ContextCandidate(
                context_key="terminal_output",
                description="Command line or shell terminal session active",
                confidence_score=0.70,
                evidence_refs=("proc_terminal",)
            ))

        if not candidates:
            candidates.append(ContextCandidate(
                context_key="general_career_dialogue",
                description="No distinctive environmental context matched; defaulting to general mentoring",
                confidence_score=0.50,
                evidence_refs=()
            ))

        # Sort candidates descending by confidence
        sorted_candidates = sorted(candidates, key=lambda c: c.confidence_score, reverse=True)
        top = sorted_candidates[0]

        if len(sorted_candidates) > 1:
            second = sorted_candidates[1]
            sep_ratio = (top.confidence_score - second.confidence_score) / max(0.01, top.confidence_score)
        else:
            sep_ratio = 1.0

        # Separation threshold: >= 0.20 is decisive; < 0.20 is ambiguous
        is_ambiguous = (sep_ratio < 0.20 and len(sorted_candidates) > 1)
        selected = None if is_ambiguous else top.context_key

        return ContextCandidateSet(
            candidates=tuple(sorted_candidates),
            separation_ratio=round(sep_ratio, 3),
            selected_context=selected,
            is_ambiguous=is_ambiguous
        )
