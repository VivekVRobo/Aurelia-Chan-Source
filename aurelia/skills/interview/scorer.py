"""
Aurelia Cognitive OS V3 - Phase 2: Interview Intelligence
=========================================================
Interview response scoring and competency evidence extraction.

Specialist engine that scores interview responses using structured
analysis, not subjective LLM assessment.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import re
from aurelia.cognition.contracts import InterviewEvidence, Evidence


class InterviewQuestionType(Enum):
    """Types of interview questions."""
    BEHAVIORAL = "behavioral"  # "Tell me about a time..."
    SITUATIONAL = "situational"  # "What would you do if..."
    TECHNICAL = "technical"  # Domain-specific questions
    LEADERSHIP = "leadership"  # Leadership scenarios
    STRATEGIC = "strategic"  # Strategic thinking questions


class STARComponent(Enum):
    """STAR method components."""
    SITUATION = "situation"
    TASK = "task"
    ACTION = "action"
    RESULT = "result"


@dataclass
class STARAnalysis:
    """Analysis of STAR method completeness."""
    has_situation: bool
    has_task: bool
    has_action: bool
    has_result: bool
    completeness_score: float  # 0-1
    issue_count: int


@dataclass
class CompetencyScore:
    """Score for a specific competency."""
    competency: str
    score: float  # 0-10 scale
    evidence: List[str]
    confidence: float


@dataclass
class InterviewResponse:
    """A single interview response."""
    question: str
    question_type: InterviewQuestionType
    answer: str
    star_analysis: Optional[STARAnalysis] = None
    competency_scores: List[CompetencyScore] = field(default_factory=list)
    overall_score: float = 0.0
    feedback: List[str] = field(default_factory=list)


class InterviewScorer:
    """
    Specialist engine for interview response scoring.
    
    Uses deterministic analysis rules, not subjective LLM assessment.
    """
    
    # STAR detection patterns
    SITUATION_KEYWORDS = ["situation", "context", "background", "when", "at my previous company"]
    TASK_KEYWORDS = ["task", "goal", "objective", "needed to", "challenge was"]
    ACTION_KEYWORDS = ["i", "we", "led", "managed", "created", "developed", "implemented"]
    RESULT_KEYWORDS = ["result", "outcome", "achieved", "succeeded", "improved", "reduced", "increased"]
    
    # Competency keywords
    LEADERSHIP_KEYWORDS = ["led", "managed", "directed", "supervised", "team", "influence"]
    CONFLICT_MANAGEMENT_KEYWORDS = ["conflict", "dispute", "disagreement", "resolve", "mediate"]
    STRATEGIC_THINKING_KEYWORDS = ["strategy", "strategic", "plan", "long-term", "vision", "roadmap"]
    COMMUNICATION_KEYWORDS = ["communicated", "presented", "explained", "negotiated", "influenced"]
    PROBLEM_SOLVING_KEYWORDS = ["problem", "challenge", "solution", "solve", "resolved", "overcame"]
    
    # Metric patterns
    METRIC_PATTERNS = [
        r'(\d+)%',
        r'\$\d+[kKmM]?',
        r'(\d+)\s*(people|team members|employees)',
        r'(\d+)\s*(weeks|months|years)',
        r'by\s+(\d+)%',
    ]
    
    def detect_question_type(self, question: str) -> InterviewQuestionType:
        """Detect the type of interview question."""
        question_lower = question.lower()
        
        if "tell me about a time" in question_lower or "describe a situation" in question_lower:
            return InterviewQuestionType.BEHAVIORAL
        elif "what would you do" in question_lower or "how would you handle" in question_lower:
            return InterviewQuestionType.SITUATIONAL
        elif "lead" in question_lower or "manage" in question_lower or "team" in question_lower:
            return InterviewQuestionType.LEADERSHIP
        elif "strategy" in question_lower or "strategic" in question_lower or "plan" in question_lower:
            return InterviewQuestionType.STRATEGIC
        else:
            return InterviewQuestionType.TECHNICAL
    
    def analyze_star_completeness(self, answer: str) -> STARAnalysis:
        """
        Analyze STAR method completeness in an answer.
        
        STAR = Situation, Task, Action, Result
        """
        answer_lower = answer.lower()
        
        # Detect each component
        has_situation = any(kw in answer_lower for kw in self.SITUATION_KEYWORDS)
        has_task = any(kw in answer_lower for kw in self.TASK_KEYWORDS)
        has_action = any(kw in answer_lower for kw in self.ACTION_KEYWORDS)
        has_result = any(kw in answer_lower for kw in self.RESULT_KEYWORDS)
        
        # Calculate completeness
        components_present = sum([has_situation, has_task, has_action, has_result])
        completeness_score = components_present / 4.0
        
        # Count issues
        issue_count = 4 - components_present
        
        return STARAnalysis(
            has_situation=has_situation,
            has_task=has_task,
            has_action=has_action,
            has_result=has_result,
            completeness_score=completeness_score,
            issue_count=issue_count
        )
    
    def detect_metrics(self, answer: str) -> int:
        """Count how many metrics are present in the answer."""
        metric_count = 0
        for pattern in self.METRIC_PATTERNS:
            if re.search(pattern, answer, re.IGNORECASE):
                metric_count += 1
        return metric_count
    
    def calculate_specificity(self, answer: str) -> float:
        """
        Calculate specificity score (0-1).
        
        Higher specificity = more concrete details, fewer vague statements.
        """
        answer_lower = answer.lower()
        
        # Vague indicators (lower specificity)
        vague_indicators = [
            "very", "really", "quite", "somewhat", "kind of",
            "a lot", "good", "bad", "nice", "great"
        ]
        vague_count = sum(1 for kw in vague_indicators if kw in answer_lower)
        
        # Specific indicators (higher specificity)
        specific_indicators = [
            "specifically", "exactly", "precisely", "concretely",
            "for example", "such as", "including", "named"
        ]
        specific_count = sum(1 for kw in specific_indicators if kw in answer_lower)
        
        # Base score
        specificity = 0.5
        
        # Adjust based on indicators
        specificity += (specific_count * 0.1)
        specificity -= (vague_count * 0.05)
        
        # Boost if metrics present
        if self.detect_metrics(answer) > 0:
            specificity += 0.15
        
        return max(0.0, min(1.0, specificity))
    
    def calculate_ownership_clarity(self, answer: str) -> float:
        """
        Calculate ownership clarity (0-1).
        
        Higher = clear about personal vs team contribution.
        """
        answer_lower = answer.lower()
        
        # First-person indicators (personal ownership)
        first_person = answer_lower.count("i ")
        
        # Team indicators (team contribution)
        team_indicators = ["we", "our team", "my team", "the team"]
        team_count = sum(1 for kw in team_indicators if kw in answer_lower)
        
        # Good balance: some "I" for personal action, some "we" for team context
        if first_person > 0 and team_count > 0:
            return 0.8
        elif first_person > 0:
            return 0.6  # Good ownership, may lack team context
        elif team_count > 0:
            return 0.4  # Team context but unclear personal contribution
        else:
            return 0.3  # Unclear ownership
    
    def score_competency(self, answer: str, competency: str, keywords: List[str]) -> CompetencyScore:
        """Score a specific competency based on keyword presence and quality."""
        answer_lower = answer.lower()
        
        # Count keyword matches
        keyword_matches = sum(1 for kw in keywords if kw in answer_lower)
        
        # Base score from keyword presence
        base_score = min(keyword_matches / 3.0, 1.0) * 7.0  # Max 7 from keywords
        
        # Boost from STAR completeness
        star = self.analyze_star_completeness(answer)
        star_boost = star.completeness_score * 2.0  # Max 2 from STAR
        
        # Boost from metrics
        metric_count = self.detect_metrics(answer)
        metric_boost = min(metric_count * 0.5, 1.0)  # Max 1 from metrics
        
        total_score = base_score + star_boost + metric_boost
        
        # Collect evidence
        evidence = []
        if keyword_matches > 0:
            evidence.append(f"Used {keyword_matches} competency-relevant keywords")
        if star.completeness_score > 0.5:
            evidence.append("Structured response with STAR method")
        if metric_count > 0:
            evidence.append(f"Included {metric_count} quantified metrics")
        
        return CompetencyScore(
            competency=competency,
            score=min(total_score, 10.0),
            evidence=evidence,
            confidence=0.7 if keyword_matches > 0 else 0.3
        )
    
    def score_response(self, question: str, answer: str) -> InterviewResponse:
        """
        Score a complete interview response.
        
        Returns structured evidence that career analysis uses directly.
        """
        question_type = self.detect_question_type(question)
        star_analysis = self.analyze_star_completeness(answer)
        specificity = self.calculate_specificity(answer)
        ownership = self.calculate_ownership_clarity(answer)
        metrics_count = self.detect_metrics(answer)
        
        # Score relevant competencies based on question type
        competency_scores = []
        
        if question_type == InterviewQuestionType.LEADERSHIP:
            competency_scores.append(
                self.score_competency(answer, "leadership", self.LEADERSHIP_KEYWORDS)
            )
            competency_scores.append(
                self.score_competency(answer, "conflict_management", self.CONFLICT_MANAGEMENT_KEYWORDS)
            )
        elif question_type == InterviewQuestionType.STRATEGIC:
            competency_scores.append(
                self.score_competency(answer, "strategic_thinking", self.STRATEGIC_THINKING_KEYWORDS)
            )
            competency_scores.append(
                self.score_competency(answer, "communication", self.COMMUNICATION_KEYWORDS)
            )
        else:
            # General scoring for other types
            competency_scores.append(
                self.score_competency(answer, "problem_solving", self.PROBLEM_SOLVING_KEYWORDS)
            )
            competency_scores.append(
                self.score_competency(answer, "communication", self.COMMUNICATION_KEYWORDS)
            )
        
        # Calculate overall score
        if competency_scores:
            overall_score = sum(cs.score for cs in competency_scores) / len(competency_scores)
            # Adjust for STAR and metrics
            overall_score = (overall_score * 0.6) + (star_analysis.completeness_score * 2.0) + (specificity * 1.0)
            overall_score = min(overall_score, 10.0)
        else:
            overall_score = 0.0
        
        # Generate feedback
        feedback = []
        if star_analysis.completeness_score < 0.5:
            feedback.append("Response lacks STAR structure - add Situation, Task, Action, Result")
        if metrics_count == 0:
            feedback.append("Include quantified metrics to strengthen your answer")
        if specificity < 0.5:
            feedback.append("Be more specific - avoid vague language like 'very' or 'a lot'")
        if ownership < 0.5:
            feedback.append("Clarify your personal contribution vs team contribution")
        
        return InterviewResponse(
            question=question,
            question_type=question_type,
            answer=answer,
            star_analysis=star_analysis,
            competency_scores=competency_scores,
            overall_score=overall_score,
            feedback=feedback
        )
    
    def extract_interview_evidence(self, response: InterviewResponse) -> InterviewEvidence:
        """
        Convert scored response to structured evidence.
        
        This is what the user model and gap analysis use.
        """
        competencies = {}
        for cs in response.competency_scores:
            competencies[cs.competency] = cs.score / 10.0  # Normalize to 0-1
        
        missing_evidence = []
        if response.star_analysis.completeness_score < 0.75:
            missing_evidence.append("STAR method completeness")
        if self.detect_metrics(response.answer) == 0:
            missing_evidence.append("quantified outcomes")
        
        return InterviewEvidence(
            competencies=competencies,
            missing_evidence=missing_evidence,
            star_completeness=response.star_analysis.completeness_score,
            specificity=self.calculate_specificity(response.answer),
            quantified_impact=min(self.detect_metrics(response.answer) / 2.0, 1.0)
        )