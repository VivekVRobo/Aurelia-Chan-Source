#!/usr/bin/env python3
"""
Aurelia-chan Improved Response Tester
======================================
Test the improved response logic with better topic coverage.
"""

class AureliaChat:
    def __init__(self):
        self.current_expression = "neutral"
        self.expressions = {
            "neutral": "01. Neutral / Observing - Calm executive evaluation and structured focus.",
            "confident": "02. Subtle Confident Smile - Refined assurance in strategic direction.",
            "approval": "03. Soft Approval - Restrained praise for high-value achievements.",
            "focused": "04. Focused Listening - Deep analytical attention to career details.",
            "analyzing": "05. Analyzing (Raised Brow) - Critical inspection of plans or resume metrics.",
            "serious": "06. Serious - Uncompromising clarity on high-stakes decisions.",
            "warning": "07. Strict Warning - Firm correction against strategic mistakes.",
            "disappointed": "08. Disappointed - Measured disappointment in lack of preparation.",
            "skeptical": "09. Skeptical - Questioning unsubstantiated or vague claims.",
            "concerned": "10. Concerned - Strategic empathy for burn-out or toxic environments.",
            "empathetic": "11. Empathetic - Warm executive mentorship during challenging pivots."
        }
    
    def analyze_expression(self, text):
        """Determine appropriate expression based on text content."""
        lower = text.lower()
        if any(word in lower for word in ["mistake", "fail", "warning", "never", "avoid", "error"]):
            return "warning"
        elif any(word in lower for word in ["good", "excellent", "great", "impressive", "congratulations"]):
            return "approval"
        elif any(word in lower for word in ["analyze", "resume", "data", "audit", "metrics"]):
            return "analyzing"
        elif any(word in lower for word in ["doubt", "claim", "unclear", "vague"]):
            return "skeptical"
        elif any(word in lower for word in ["problem", "stress", "burnout", "difficult", "tired"]):
            return "concerned"
        elif any(word in lower for word in ["strategy", "leader", "executive", "confident", "leadership", "manage", "team"]):
            return "confident"
        elif any(word in lower for word in ["help", "guidance", "support", "mentor", "thank", "thanks"]):
            return "empathetic"
        elif any(word in lower for word in ["serious", "critical", "crucial"]):
            return "serious"
        elif any(word in lower for word in ["hello", "hi"]):
            return "focused"
        else:
            return "focused"
    
    def get_response(self, user_text):
        """Generate Aurelia's response based on user input."""
        self.current_expression = self.analyze_expression(user_text)
        
        lower = user_text.lower()
        
        # Check for leadership first (before general greeting)
        if any(word in lower for word in ["leadership", "manage", "team"]):
            return "Executive leadership requires balancing strategic vision with operational execution. Focus on developing your team, removing obstacles, and creating an environment where high performers can thrive."
        elif any(word in lower for word in ["hello", "hi"]):
            return "Greetings. I am fully focused on your professional growth. What career milestone or strategic challenge shall we tackle next?"
        elif any(word in lower for word in ["promote", "promotion", "raise"]):
            return "Securing a promotion requires proving value before asking for the title. Document your quantifiable impact, build cross-functional alliances, and present a structured case to leadership."
        elif any(word in lower for word in ["resume", "cv"]):
            return "To make your resume executive-ready, shift from listing duties to highlighting key achievements with hard metrics (e.g., 'Increased revenue by 35%'). Try our Resume Audit tab!"
        elif any(word in lower for word in ["stress", "burnout", "tired"]):
            return "Burnout is a strategic risk, not a personal failure. Assess your boundaries, document excessive workloads, and approach leadership with data on how current demands impact long-term productivity."
        elif any(word in lower for word in ["salary", "money", "pay"]):
            return "Compensation negotiations should be data-driven. Research market rates, document your quantifiable impact, and present your case with specific examples of business value you've delivered."
        elif any(word in lower for word in ["thank", "thanks"]):
            return "You are welcome. Continuous professional development and strategic thinking are the hallmarks of executive growth. What other challenges can we address?"
        elif any(word in lower for word in ["good", "great", "excellent", "impressive"]):
            return "Excellent work. Recognizing achievement is important, but ensure you document the specific metrics and business impact that made this success possible for future reference."
        elif any(word in lower for word in ["mistake", "fail", "error"]):
            return "Executive composure during setbacks is a critical skill. Acknowledge the issue, document the root cause, implement corrective measures, and communicate the resolution plan with transparency to stakeholders."
        else:
            return f"Regarding '{user_text}': In executive strategy, clarity and execution precede outcome. Focus on identifying root metrics, establishing clear boundaries, and delivering consistent strategic value."
    
    def display_expression(self):
        """Show current expression status."""
        expr_info = self.expressions[self.current_expression]
        print(f"\n[Expression: {self.current_expression.upper()}]")
        print(f"  {expr_info}")
        print()

def main():
    chat = AureliaChat()
    
    print("=" * 70)
    print("    AURELIA-CHAN — Improved Response Test")
    print("=" * 70)
    print()
    
    # Test the previously problematic inputs
    test_inputs = [
        "Hello",
        "I want a promotion", 
        "Can you help me with my resume?",
        "I'm feeling stressed at work",
        "How do I handle salary negotiations?",
        "I need to improve my leadership skills",  # Previously problematic
        "Great job on the project",              # Previously problematic
        "I made a mistake in my presentation",   # Previously problematic
        "What's the best strategy for career growth?",
        "Thank you for your help"
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"Test {i}/{len(test_inputs)}")
        print("-" * 70)
        print(f"You: {user_input}")
        
        response = chat.get_response(user_input)
        chat.display_expression()
        
        print(f"Aurelia: {response}")
        print()
    
    print("=" * 70)
    print("Improved Response Test Complete")
    print("=" * 70)

if __name__ == "__main__":
    main()