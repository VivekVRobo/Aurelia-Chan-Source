#!/usr/bin/env python3
"""
Aurelia-chan Terminal Chat Interface
====================================
Command-line interface to chat with Aurelia-chan
using the same logic as the web application.
"""

import sys
import time

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
        if any(word in lower for word in ["mistake", "fail", "warning", "never", "avoid"]):
            return "warning"
        elif any(word in lower for word in ["good", "excellent", "great", "impressive", "congratulations"]):
            return "approval"
        elif any(word in lower for word in ["analyze", "resume", "data", "audit", "metrics"]):
            return "analyzing"
        elif any(word in lower for word in ["doubt", "claim", "unclear", "vague"]):
            return "skeptical"
        elif any(word in lower for word in ["problem", "stress", "burnout", "difficult"]):
            return "concerned"
        elif any(word in lower for word in ["strategy", "leader", "executive", "confident"]):
            return "confident"
        elif any(word in lower for word in ["help", "guidance", "support", "mentor"]):
            return "empathetic"
        elif any(word in lower for word in ["serious", "critical", "crucial"]):
            return "serious"
        else:
            return "focused"
    
    def get_response(self, user_text):
        """Generate Aurelia's response based on user input."""
        self.current_expression = self.analyze_expression(user_text)
        
        lower = user_text.lower()
        
        if any(word in lower for word in ["hello", "hi"]):
            return "Greetings. I am fully focused on your professional growth. What career milestone or strategic challenge shall we tackle next?"
        elif any(word in lower for word in ["promote", "promotion", "raise"]):
            return "Securing a promotion requires proving value before asking for the title. Document your quantifiable impact, build cross-functional alliances, and present a structured case to leadership."
        elif any(word in lower for word in ["resume", "cv"]):
            return "To make your resume executive-ready, shift from listing duties to highlighting key achievements with hard metrics (e.g., 'Increased revenue by 35%'). Try our Resume Audit tab!"
        elif any(word in lower for word in ["interview", "question"]):
            return "For executive interviews, focus on the STAR method: Situation, Task, Action, Result. Lead with outcomes, maintain emotional composure, and always tie answers to business impact."
        elif any(word in lower for word in ["stress", "burnout", "tired"]):
            return "Burnout is a strategic risk, not a personal failure. Assess your boundaries, document excessive workloads, and approach leadership with data on how current demands impact long-term productivity."
        elif any(word in lower for word in ["team", "manage", "lead"]):
            return "Executive leadership requires balancing strategic vision with operational execution. Focus on developing your team, removing obstacles, and creating an environment where high performers can thrive."
        elif any(word in lower for word in ["salary", "money", "pay"]):
            return "Compensation negotiations should be data-driven. Research market rates, document your quantifiable impact, and present your case with specific examples of business value you've delivered."
        elif any(word in lower for word in ["thank", "thanks"]):
            return "You are welcome. Continuous professional development and strategic thinking are the hallmarks of executive growth. What other challenges can we address?"
        else:
            return f"Regarding '{user_text}': In executive strategy, clarity and execution precede outcome. Focus on identifying root metrics, establishing clear boundaries, and delivering consistent strategic value."
    
    def display_expression(self):
        """Show current expression status."""
        expr_info = self.expressions[self.current_expression]
        print(f"\n[Expression: {self.current_expression.upper()}]")
        print(f"  {expr_info}")
        print()
    
    def chat(self):
        """Main chat loop."""
        print("=" * 60)
        print("    AURELIA-CHAN — Executive Career Mentor")
        print("    Terminal Chat Interface")
        print("=" * 60)
        print()
        print("Good day. I am Aurelia, your executive career mentor.")
        print("How may I assist your professional trajectory today?")
        print()
        print("Type 'quit' or 'exit' to end the conversation.")
        print("-" * 60)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\nAurelia: Continue your strategic development with discipline and clarity. Good day.")
                    break
                
                # Simulate processing delay
                print("Aurelia is thinking...", end="", flush=True)
                time.sleep(0.5)
                print("\r" + " " * 30 + "\r", end="", flush=True)
                
                # Get response and update expression
                response = self.get_response(user_input)
                self.display_expression()
                
                print(f"Aurelia: {response}")
                
            except KeyboardInterrupt:
                print("\n\nAurelia: Session interrupted. Continue your professional development with discipline.")
                break
            except Exception as e:
                print(f"\nError: {e}")
                continue

def main():
    chat = AureliaChat()
    chat.chat()

if __name__ == "__main__":
    main()