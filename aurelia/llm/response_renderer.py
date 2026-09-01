"""
Aurelia Cognitive OS V3 - Phase 7: Response Renderer
=====================================================
Converts structured responses to natural language.

The response renderer converts structured system outputs
into natural language responses with Aurelia's persona.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from aurelia.cognition.contracts import ResponsePlan


class ResponseStyle(Enum):
    """Styles of responses."""
    PROFESSIONAL = "professional"
    DIRECT = "direct"
    SUPPORTIVE = "supportive"
    ANALYTICAL = "analytical"
    CONVERSATIONAL = "conversational"


class ResponseTone(Enum):
    """Tones of responses."""
    NEUTRAL = "neutral"
    ENCOURAGING = "encouraging"
    CAUTIOUS = "cautious"
    CONFIDENT = "confident"
    EMPATHETIC = "empathetic"


@dataclass
class RenderedResponse:
    """
    A fully rendered natural language response.
    
    Converts structured plans into natural language with persona.
    """
    content: str
    style: ResponseStyle
    tone: ResponseTone
    sections: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResponseRenderer:
    """
    Converts structured responses to natural language.
    
    The response renderer:
    - Converts ResponsePlan to natural language
    - Applies Aurelia's persona and voice
    - Manages response style and tone
    - Structures responses for clarity
    """
    
    def __init__(self):
        self.persona_traits = {
            "professional": True,
            "focused": True,
            "supportive": True,
            "evidence_based": True,
            "action_oriented": True
        }
    
    def render_response(
        self,
        response_plan: ResponsePlan,
        style: ResponseStyle = ResponseStyle.PROFESSIONAL,
        tone: ResponseTone = ResponseTone.NEUTRAL
    ) -> RenderedResponse:
        """
        Render a response plan into natural language.
        
        Converts structured plan into natural language with persona.
        """
        # Build response sections
        sections = []
        
        # Opening
        opening = self._generate_opening(response_plan, tone)
        sections.append(opening)
        
        # Main content from claims
        main_content = self._generate_main_content(response_plan, style)
        sections.append(main_content)
        
        # Recommendations
        if response_plan.recommendations:
            recommendation_section = self._generate_recommendation_section(response_plan.recommendations)
            sections.append(recommendation_section)
        
        # Uncertainty and questions
        if response_plan.uncertainty or response_plan.questions:
            consideration_section = self._generate_consideration_section(response_plan.uncertainty, response_plan.questions)
            sections.append(consideration_section)
        
        # Closing
        closing = self._generate_closing(response_plan, tone)
        sections.append(closing)
        
        # Combine sections
        content = "\n\n".join(sections)
        
        # Apply persona
        content = self._apply_persona(content)
        
        return RenderedResponse(
            content=content,
            style=style,
            tone=tone,
            sections=sections,
            metadata={"response_intent": response_plan.intent}
        )
    
    def _generate_opening(self, response_plan: ResponsePlan, tone: ResponseTone) -> str:
        """Generate opening section."""
        if tone == ResponseTone.ENCOURAGING:
            return "I appreciate you sharing that with me. Let's work through this together."
        elif tone == ResponseTone.CAUTIOUS:
            return "Let me carefully consider this to provide you with the most accurate guidance."
        elif tone == ResponseTone.CONFIDENT:
            return "Based on the available information, I can provide you with clear guidance."
        elif tone == ResponseTone.EMPATHETIC:
            return "I understand this is important to you. Let's explore this thoughtfully."
        else:
            return "Thank you for that input. Let me provide some structured guidance."
    
    def _generate_main_content(self, response_plan: ResponsePlan, style: ResponseStyle) -> str:
        """Generate main content section."""
        if response_plan.claims:
            claims_text = " ".join([str(claim) for claim in response_plan.claims[:2]])
        else:
            claims_text = "Based on our analysis, here are the key considerations."
        
        if style == ResponseStyle.DIRECT:
            return claims_text
        elif style == ResponseStyle.ANALYTICAL:
            return f"Analysis: {claims_text}\n\nKey considerations: This requires careful evaluation of multiple factors."
        elif style == ResponseStyle.SUPPORTIVE:
            return f"{claims_text}\n\nI'm here to support you through this process."
        elif style == ResponseStyle.CONVERSATIONAL:
            return f"That's a great question. {claims_text} Let me elaborate on this."
        else:  # PROFESSIONAL
            return claims_text
    
    def _generate_recommendation_section(self, recommendations: List[str]) -> str:
        """Generate recommendations section."""
        if not recommendations:
            return ""
        
        rec_lines = ["Recommendations:"]
        for i, rec in enumerate(recommendations, 1):
            rec_lines.append(f"{i}. {rec}")
        
        return "\n".join(rec_lines)
    
    def _generate_consideration_section(self, uncertainty: List[str], questions: List[str]) -> str:
        """Generate uncertainty and questions section."""
        if not uncertainty and not questions:
            return ""
        
        lines = []
        
        if uncertainty:
            lines.append("Important considerations:")
            for i, item in enumerate(uncertainty, 1):
                lines.append(f"{i}. {item}")
        
        if questions:
            lines.append("Questions to consider:")
            for i, question in enumerate(questions, 1):
                lines.append(f"{i}. {question}")
        
        return "\n".join(lines)
    
    def _generate_closing(self, response_plan: ResponsePlan, tone: ResponseTone) -> str:
        """Generate closing section."""
        if tone == ResponseTone.ENCOURAGING:
            return "You're making good progress. Let's continue building on this foundation."
        elif tone == ResponseTone.CAUTIOUS:
            return "I recommend proceeding with these considerations in mind. We can adjust as needed."
        elif tone == ResponseTone.CONFIDENT:
            return "This approach positions you well for success. Execute on these steps and we can review progress."
        elif tone == ResponseTone.EMPATHETIC:
            return "Remember that professional growth is a journey. Take these steps at your own pace."
        else:
            return "Let's proceed with this approach and monitor progress together."
    
    def _apply_persona(self, content: str) -> str:
        """Apply Aurelia's persona to the content."""
        # Professional traits
        if self.persona_traits["professional"]:
            content = self._ensure_professional_language(content)
        
        # Focused traits
        if self.persona_traits["focused"]:
            content = self._ensure_focused_content(content)
        
        # Evidence-based traits
        if self.persona_traits["evidence_based"]:
            content = self._ensure_evidence_based_language(content)
        
        # Action-oriented traits
        if self.persona_traits["action_oriented"]:
            content = self._ensure_action_oriented_language(content)
        
        return content
    
    def _ensure_professional_language(self, content: str) -> str:
        """Ensure professional language."""
        # Simple replacements - in full system would be more sophisticated
        replacements = {
            "good": "strong",
            "bad": "suboptimal",
            "really": "significantly",
            "very": "considerably",
            "awesome": "excellent",
            "cool": "notable"
        }
        
        for informal, formal in replacements.items():
            content = content.replace(informal, formal)
        
        return content
    
    def _ensure_focused_content(self, content: str) -> str:
        """Ensure content is focused and direct."""
        # Remove excessive elaboration
        sentences = content.split(".")
        focused_sentences = []
        
        for sentence in sentences:
            if len(sentence.strip()) > 10:  # Keep substantive sentences
                focused_sentences.append(sentence.strip())
        
        return ". ".join(focused_sentences) + "."
    
    def _ensure_evidence_based_language(self, content: str) -> str:
        """Ensure evidence-based language."""
        # Add qualifiers where certainty is low
        # In full system would use actual confidence scores
        return content  # Placeholder for full implementation
    
    def _ensure_action_oriented_language(self, content: str) -> str:
        """Ensure action-oriented language."""
        # Add action verbs where appropriate
        action_verbs = ["consider", "implement", "develop", "pursue", "establish"]
        
        # Simple check - in full system would be more sophisticated
        for verb in action_verbs:
            if verb not in content.lower():
                # Add action orientation if missing
                pass  # Placeholder for full implementation
        
        return content
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the response renderer state."""
        return {
            "persona_traits": self.persona_traits,
            "available_styles": [style.value for style in ResponseStyle],
            "available_tones": [tone.value for tone in ResponseTone]
        }