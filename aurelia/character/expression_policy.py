"""
Aurelia Cognitive OS V3 - Phase 8: Expression Policy
====================================================
Manages how Aurelia expresses herself in responses.

The expression policy ensures consistency in Aurelia's
communication style and maintains professional boundaries.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class ExpressionStyle(Enum):
    """Styles of expression."""
    FORMAL = "formal"
    SEMI_FORMAL = "semi_formal"
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    MENTORIAL = "mentorial"


class ExpressionConstraint(Enum):
    """Constraints on expression."""
    NO_PERSONAL_DISCLOSURE = "no_personal_disclosure"
    NO_POLITICAL_CONTENT = "no_political_content"
    PROFESSIONAL_BOUNDARIES = "professional_boundaries"
    EVIDENCE_REQUIRED = "evidence_required"
    NO_OVERPROMISING = "no_overpromising"


@dataclass
class ExpressionPolicy:
    """
    Policy for how Aurelia should express herself.
    
    Ensures consistency and professional boundaries in communication.
    """
    style: ExpressionStyle
    constraints: List[ExpressionConstraint]
    max_sentence_length: int = 50
    min_sentence_length: int = 5
    preferred_vocab_level: str = "professional"  # simple, professional, technical
    avoid_phrases: List[str] = field(default_factory=list)
    preferred_phrases: List[str] = field(default_factory=list)


class ExpressionPolicyManager:
    """
    Manages how Aurelia expresses herself in responses.
    
    The expression policy manager:
    - Ensures consistent communication style
    - Maintains professional boundaries
    - Checks for inappropriate content
    - Validates expression against policies
    """
    
    def __init__(self):
        self.current_policy = self._create_default_policy()
        self.policy_history: List[ExpressionPolicy] = []
    
    def _create_default_policy(self) -> ExpressionPolicy:
        """Create the default expression policy."""
        return ExpressionPolicy(
            style=ExpressionStyle.PROFESSIONAL,
            constraints=[
                ExpressionConstraint.PROFESSIONAL_BOUNDARIES,
                ExpressionConstraint.EVIDENCE_REQUIRED,
                ExpressionConstraint.NO_OVERPROMISING
            ],
            max_sentence_length=50,
            min_sentence_length=5,
            preferred_vocab_level="professional",
            avoid_phrases=[
                "I promise", "guarantee", "absolutely certain",
                "always", "never", "perfect",
                "hate", "love", "beautiful", "ugly"
            ],
            preferred_phrases=[
                "Based on the evidence",
                "The data suggests",
                "My analysis indicates",
                "Consider the following",
                "This approach may help"
            ]
        )
    
    def set_policy(self, policy: ExpressionPolicy):
        """Set a new expression policy."""
        self.policy_history.append(self.current_policy)
        self.current_policy = policy
    
    def check_compliance(self, text: str) -> Dict[str, Any]:
        """
        Check if text complies with current expression policy.
        
        Returns compliance report with any violations.
        """
        violations = []
        warnings = []
        
        # Check for avoided phrases
        for phrase in self.current_policy.avoid_phrases:
            if phrase.lower() in text.lower():
                violations.append(f"Avoided phrase used: '{phrase}'")
        
        # Check sentence length
        sentences = text.split(".")
        for sentence in sentences:
            if len(sentence.split()) > self.current_policy.max_sentence_length:
                warnings.append(f"Sentence too long: {len(sentence.split())} words")
            elif len(sentence.split()) < self.current_policy.min_sentence_length:
                warnings.append(f"Sentence too short: {len(sentence.split())} words")
        
        # Check for overpromising
        if ExpressionConstraint.NO_OVERPROMISING in self.current_policy.constraints:
            overpromise_phrases = ["guarantee", "promise", "absolutely", "definitely", "certainly"]
            for phrase in overpromise_phrases:
                if phrase.lower() in text.lower():
                    violations.append(f"Overpromising language: '{phrase}'")
        
        # Check for evidence requirement
        if ExpressionConstraint.EVIDENCE_REQUIRED in self.current_policy.constraints:
            if len(text.split()) > 50 and "evidence" not in text.lower() and "data" not in text.lower():
                warnings.append("Long response without evidence backing")
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "compliance_score": 1.0 - (len(violations) * 0.2) - (len(warnings) * 0.05)
        }
    
    def suggest_improvements(self, text: str) -> List[str]:
        """Suggest improvements to better comply with expression policy."""
        compliance = self.check_compliance(text)
        improvements = []
        
        # Replace avoided phrases with preferred ones
        for avoid_phrase in self.current_policy.avoid_phrases:
            if avoid_phrase.lower() in text.lower():
                # Suggest alternatives
                alternatives = [p for p in self.current_policy.preferred_phrases]
                if alternatives:
                    improvements.append(f"Consider replacing '{avoid_phrase}' with '{alternatives[0]}'")
        
        # Fix sentence length issues
        sentences = text.split(".")
        for i, sentence in enumerate(sentences):
            word_count = len(sentence.split())
            if word_count > self.current_policy.max_sentence_length:
                improvements.append(f"Sentence {i+1} is too long ({word_count} words). Consider breaking it down.")
            elif word_count < self.current_policy.min_sentence_length and word_count > 0:
                improvements.append(f"Sentence {i+1} is too short ({word_count} words). Consider combining with another sentence.")
        
        return improvements
    
    def adapt_for_context(self, context: str) -> ExpressionPolicy:
        """
        Adapt expression policy for specific context.
        
        Different contexts may require different expression styles.
        """
        context_lower = context.lower()
        
        # If context suggests a sensitive situation
        if any(word in context_lower for word in ["personal", "stress", "challenge", "difficulty"]):
            adapted = ExpressionPolicy(
                style=ExpressionStyle.MENTORIAL,
                constraints=self.current_policy.constraints.copy(),
                max_sentence_length=self.current_policy.max_sentence_length,
                min_sentence_length=self.current_policy.min_sentence_length,
                preferred_vocab_level=self.current_policy.preferred_vocab_level,
                avoid_phrases=self.current_policy.avoid_phrases.copy(),
                preferred_phrases=self.current_policy.preferred_phrases.copy()
            )
            # Add supportive phrases
            adapted.preferred_phrases.extend([
                "I understand this is challenging",
                "Let's work through this together",
                "Your growth is important"
            ])
            return adapted
        
        # If context suggests celebration
        elif any(word in context_lower for word in ["success", "achievement", "milestone", "progress"]):
            adapted = ExpressionPolicy(
                style=ExpressionStyle.SEMI_FORMAL,
                constraints=self.current_policy.constraints.copy(),
                max_sentence_length=self.current_policy.max_sentence_length,
                min_sentence_length=self.current_policy.min_sentence_length,
                preferred_vocab_level=self.current_policy.preferred_vocab_level,
                avoid_phrases=self.current_policy.avoid_phrases.copy(),
                preferred_phrases=self.current_policy.preferred_phrases.copy()
            )
            # Add celebratory phrases
            adapted.preferred_phrases.extend([
                "Congratulations on",
                "This is excellent progress",
                "You should be proud of"
            ])
            return adapted
        
        # Default to current policy
        return self.current_policy
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the expression policy state."""
        return {
            "current_style": self.current_policy.style.value,
            "constraint_count": len(self.current_policy.constraints),
            "constraint_types": [c.value for c in self.current_policy.constraints],
            "avoided_phrases_count": len(self.current_policy.avoid_phrases),
            "preferred_phrases_count": len(self.current_policy.preferred_phrases),
            "policy_history_length": len(self.policy_history)
        }