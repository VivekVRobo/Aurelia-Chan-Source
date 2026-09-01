"""
Aurelia Cognitive OS V3 - Phase 7: Reasoning Interface
=======================================================
Structured LLM reasoning interface.

The reasoning interface provides structured prompts and response
parsing for semantic reasoning tasks.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
import json
import re


class ReasoningTask(Enum):
    """Types of reasoning tasks."""
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    AMBIGUITY_RESOLUTION = "ambiguity_resolution"
    INFERENCE = "inference"
    SYNTHESIS = "synthesis"
    EXPLANATION = "explanation"
    PLANNING_SUGGESTION = "planning_suggestion"


@dataclass
class ReasoningRequest:
    """A structured reasoning request for the LLM."""
    task: ReasoningTask
    context: str
    question: str
    constraints: List[str] = field(default_factory=list)
    expected_format: str = "natural_language"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReasoningResponse:
    """A structured reasoning response from the LLM."""
    task: ReasoningTask
    reasoning: str
    conclusion: str
    confidence: float
    assumptions: List[str] = field(default_factory=list)
    alternative_perspectives: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ReasoningInterface:
    """
    Structured LLM reasoning interface.
    
    The reasoning interface:
    - Provides structured prompts for different reasoning tasks
    - Parses LLM responses into structured format
    - Ensures reasoning is traceable and well-structured
    - Handles different types of semantic reasoning
    """
    
    def __init__(self):
        self.reasoning_templates = {
            ReasoningTask.HYPOTHESIS_GENERATION: self._hypothesis_generation_template,
            ReasoningTask.AMBIGUITY_RESOLUTION: self._ambiguity_resolution_template,
            ReasoningTask.INFERENCE: self._inference_template,
            ReasoningTask.SYNTHESIS: self._synthesis_template,
            ReasoningTask.EXPLANATION: self._explanation_template,
            ReasoningTask.PLANNING_SUGGESTION: self._planning_suggestion_template
        }
    
    def create_reasoning_request(
        self,
        task: ReasoningTask,
        context: str,
        question: str,
        constraints: Optional[List[str]] = None
    ) -> ReasoningRequest:
        """Create a structured reasoning request."""
        return ReasoningRequest(
            task=task,
            context=context,
            question=question,
            constraints=constraints or [],
            expected_format="structured"
        )
    
    def format_prompt(self, request: ReasoningRequest) -> str:
        """Format a reasoning request as a prompt for the LLM."""
        template = self.reasoning_templates.get(request.task)
        if template:
            return template(request)
        else:
            return self._default_template(request)
    
    def parse_response(
        self,
        llm_response: str,
        task: ReasoningTask
    ) -> ReasoningResponse:
        """Parse LLM response into structured format."""
        # Try to extract structured information
        reasoning = self._extract_reasoning(llm_response)
        conclusion = self._extract_conclusion(llm_response)
        confidence = self._extract_confidence(llm_response)
        assumptions = self._extract_assumptions(llm_response)
        alternatives = self._extract_alternatives(llm_response)
        
        return ReasoningResponse(
            task=task,
            reasoning=reasoning,
            conclusion=conclusion,
            confidence=confidence,
            assumptions=assumptions,
            alternative_perspectives=alternatives,
            metadata={"raw_response": llm_response}
        )
    
    def _extract_reasoning(self, response: str) -> str:
        """Extract reasoning section from response."""
        # Look for reasoning keywords
        reasoning_keywords = ["reasoning:", "because:", "since:", "the reason is"]
        
        for keyword in reasoning_keywords:
            if keyword.lower() in response.lower():
                parts = response.lower().split(keyword.lower())
                if len(parts) > 1:
                    return parts[1].strip()
        
        # If no explicit reasoning section, return the response
        return response
    
    def _extract_conclusion(self, response: str) -> str:
        """Extract conclusion from response."""
        # Look for conclusion keywords
        conclusion_keywords = ["therefore:", "thus:", "so:", "conclusion:", "in conclusion"]
        
        for keyword in conclusion_keywords:
            if keyword.lower() in response.lower():
                parts = response.lower().split(keyword.lower())
                if len(parts) > 1:
                    return parts[1].strip()
        
        # If no explicit conclusion, return the last sentence
        sentences = response.split(".")
        if sentences:
            return sentences[-1].strip()
        
        return response
    
    def _extract_confidence(self, response: str) -> float:
        """Extract confidence level from response."""
        # Look for confidence indicators
        confidence_patterns = [
            r"confident:\s*(\d+)%?",
            r"confidence:\s*(\d+)%?",
            r"(\d+)%\s*confident",
            r"highly confident",
            r"somewhat confident",
            r"not confident"
        ]
        
        for pattern in confidence_patterns:
            match = re.search(pattern, response.lower())
            if match:
                try:
                    return float(match.group(1)) / 100
                except (ValueError, IndexError):
                    pass
        
        # Default confidence based on certainty language
        if "highly confident" in response.lower():
            return 0.9
        elif "somewhat confident" in response.lower():
            return 0.6
        elif "not confident" in response.lower():
            return 0.3
        else:
            return 0.7  # Default moderate confidence
    
    def _extract_assumptions(self, response: str) -> List[str]:
        """Extract assumptions from response."""
        assumptions = []
        
        # Look for assumption keywords
        assumption_keywords = ["assuming:", "assumption:", "based on the assumption"]
        
        for keyword in assumption_keywords:
            if keyword.lower() in response.lower():
                parts = response.lower().split(keyword.lower())
                if len(parts) > 1:
                    assumption_text = parts[1].strip()
                    # Split by common delimiters
                    for assumption in re.split(r'[,;.]', assumption_text):
                        if assumption.strip():
                            assumptions.append(assumption.strip())
        
        return assumptions
    
    def _extract_alternatives(self, response: str) -> List[str]:
        """Extract alternative perspectives from response."""
        alternatives = []
        
        # Look for alternative keywords
        alternative_keywords = ["alternatively:", "another perspective:", "on the other hand"]
        
        for keyword in alternative_keywords:
            if keyword.lower() in response.lower():
                parts = response.lower().split(keyword.lower())
                if len(parts) > 1:
                    alt_text = parts[1].strip()
                    alternatives.append(alt_text)
        
        return alternatives
    
    def _hypothesis_generation_template(self, request: ReasoningRequest) -> str:
        """Template for hypothesis generation."""
        return f"""Based on the following context, generate a hypothesis about: {request.question}

Context:
{request.context}

Provide your reasoning and then state your hypothesis clearly.

Format your response as:
Reasoning: [your reasoning]
Hypothesis: [your hypothesis]
Confidence: [0-1]
"""
    
    def _ambiguity_resolution_template(self, request: ReasoningRequest) -> str:
        """Template for ambiguity resolution."""
        return f"""The following context contains ambiguity: {request.question}

Context:
{request.context}

Identify the ambiguity and suggest how to resolve it.

Format your response as:
Ambiguity: [describe the ambiguity]
Resolution: [how to resolve it]
Confidence: [0-1]
"""
    
    def _inference_template(self, request: ReasoningRequest) -> str:
        """Template for inference."""
        return f"""Based on the context, what can you infer about: {request.question}

Context:
{request.context}

Provide your reasoning and conclusion.

Format your response as:
Reasoning: [your reasoning]
Conclusion: [your conclusion]
Confidence: [0-1]
"""
    
    def _synthesis_template(self, request: ReasoningRequest) -> str:
        """Template for synthesis."""
        return f"""Synthesize the following information to answer: {request.question}

Context:
{request.context}

Combine the relevant information into a coherent response.

Format your response as:
Synthesis: [your synthesized response]
Key points: [bullet points of key information]
Confidence: [0-1]
"""
    
    def _explanation_template(self, request: ReasoningRequest) -> str:
        """Template for explanation."""
        return f"""Explain the following in the context of: {request.question}

Context:
{request.context}

Provide a clear, step-by-step explanation.

Format your response as:
Explanation: [your explanation]
Steps: [numbered steps if applicable]
Confidence: [0-1]
"""
    
    def _planning_suggestion_template(self, request: ReasoningRequest) -> str:
        """Template for planning suggestions."""
        return f"""Based on the context, suggest a plan for: {request.question}

Context:
{request.context}

Provide actionable steps and considerations.

Format your response as:
Plan: [your suggested plan]
Steps: [numbered steps]
Considerations: [important considerations]
Confidence: [0-1]
"""
    
    def _default_template(self, request: ReasoningRequest) -> str:
        """Default template for unknown task types."""
        return f"""Task: {request.task.value}
Question: {request.question}

Context:
{request.context}

Provide a thoughtful response addressing the question.
"""