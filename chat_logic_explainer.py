#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aurelia-chan Chat Logic Explainer
================================
Shows exactly how the chat system processes user input
and generates responses step by step.
"""

class AureliaChatExplainer:
    def __init__(self):
        self.expressions = {
            "neutral": "01. Neutral / Observing",
            "confident": "02. Subtle Confident Smile", 
            "approval": "03. Soft Approval",
            "focused": "04. Focused Listening",
            "analyzing": "05. Analyzing (Raised Brow)",
            "serious": "06. Serious",
            "warning": "07. Strict Warning",
            "disappointed": "08. Disappointed",
            "skeptical": "09. Skeptical",
            "concerned": "10. Concerned",
            "empathetic": "11. Empathetic"
        }
    
    def analyze_expression_step_by_step(self, text):
        """Show step-by-step expression analysis."""
        print(f"Expression Analysis for: '{text}'")
        print("-" * 50)
        
        lower = text.lower()
        print(f"Step 1: Convert to lowercase -> '{lower}'")
        print()
        
        # Check each category in priority order
        checks = [
            ("Warning", ["mistake", "fail", "warning", "never", "avoid", "error", "failure"]),
            ("Skeptical", ["doubt", "claim", "unclear", "vague", "unsure", "confused"]),
            ("Serious", ["serious", "critical", "crucial", "urgent", "important"]),
            ("Disappointed", ["disappointed", "let down", "underwhelmed", "expectation"]),
            ("Concerned", ["problem", "stress", "burnout", "difficult", "tired", "overwhelmed", "struggle", "exhausted"]),
            ("Approval", ["good", "excellent", "great", "impressive", "congratulations", "success", "achievement", "well done"]),
            ("Analyzing", ["analyze", "resume", "data", "audit", "metrics", "analysis", "research", "market"]),
            ("Confident", ["leadership", "manage", "team", "leader", "executive", "vision", "strategy"]),
            ("Empathetic", ["help", "guidance", "support", "mentor", "thank", "thanks", "appreciate"]),
            ("Focused", ["hello", "hi", "hey", "greetings", "good morning", "good afternoon"])
        ]
        
        found = False
        for expr_name, keywords in checks:
            matched_keywords = [kw for kw in keywords if kw in lower]
            if matched_keywords:
                print(f"Step 2: Check {expr_name} keywords: {keywords}")
                print(f"        -> Matched: {matched_keywords}")
                print(f"        -> EXPRESSION SELECTED: {expr_name.upper()}")
                print(f"        -> Facial expression: {self.expressions[expr_name.lower()]}")
                found = True
                return expr_name.lower()
                break
        
        if not found:
            print("Step 2: No specific keywords matched")
            print("        -> EXPRESSION SELECTED: NEUTRAL")
            print("        -> Facial expression: 01. Neutral / Observing")
            return "neutral"
    
    def get_response_step_by_step(self, text):
        """Show step-by-step response generation."""
        print(f"\nResponse Generation for: '{text}'")
        print("-" * 50)
        
        lower = text.lower()
        print(f"Step 1: Convert to lowercase → '{lower}'")
        print()
        
        # Response mappings with priority
        responses = [
            ("Leadership", ["leadership", "manage", "team"], "Executive leadership requires balancing strategic vision with operational execution. Focus on developing your team, removing obstacles, and creating an environment where high performers can thrive."),
            ("Greeting", ["hello", "hi", "hey", "greetings"], "Greetings. I am fully focused on your professional growth. What career milestone or strategic challenge shall we tackle next?"),
            ("Promotion", ["promote", "promotion", "raise"], "Securing a promotion requires proving value before asking for the title. Document your quantifiable impact, build cross-functional alliances, and present a structured case to leadership."),
            ("Resume", ["resume", "cv"], "To make your resume executive-ready, shift from listing duties to highlighting key achievements with hard metrics (e.g., 'Increased revenue by 35%'). Try our Resume Audit tab!"),
            ("Interview", ["interview", "question"], "For executive interviews, focus on the STAR method: Situation, Task, Action, Result. Lead with outcomes, maintain emotional composure, and always tie answers to business impact."),
            ("Stress", ["stress", "burnout", "tired", "overwhelmed", "exhausted"], "Burnout is a strategic risk, not a personal failure. Assess your boundaries, document excessive workloads, and approach leadership with data on how current demands impact long-term productivity."),
            ("Salary", ["salary", "money", "pay", "compensation"], "Compensation negotiations should be data-driven. Research market rates, document your quantifiable impact, and present your case with specific examples of business value you've delivered."),
            ("Networking", ["network", "connection", "relationship"], "Strategic networking is about cultivating mutually beneficial professional relationships. Focus on providing value first, maintaining authentic connections, and consistently following up with meaningful interactions."),
            ("Conflict", ["conflict", "dispute", "difficult", "drama"], "Workplace conflict requires strategic intervention. Document specific incidents, address issues privately and professionally, and focus on solutions rather than personal grievances when escalating to HR."),
            ("Time Management", ["time", "prioritize", "productivity", "schedule"], "Executive time management hinges on ruthless prioritization. Identify your highest-impact activities, delegate operational tasks, and protect strategic thinking time in your calendar as you would any client meeting."),
            ("Communication", ["communication", "speak", "present", "write"], "Executive communication demands clarity, brevity, and strategic intent. Structure every interaction with your objective in mind, tailor your message to your audience, and always end with clear next steps."),
            ("Mentoring", ["mentor", "guidance", "advice"], "Effective mentorship requires both strategic guidance and emotional intelligence. Seek mentors who challenge your thinking while supporting your growth, and be prepared to bring specific scenarios to your mentoring relationships."),
            ("Gratitude", ["thank", "thanks", "appreciate"], "You are welcome. Continuous professional development and strategic thinking are the hallmarks of executive growth. What other challenges can we address?"),
            ("Achievement", ["good", "great", "excellent", "impressive", "success", "achievement"], "Excellent work. Recognizing achievement is important, but ensure you document the specific metrics and business impact that made this success possible for future reference."),
            ("Mistake", ["mistake", "fail", "error", "failure"], "Executive composure during setbacks is a critical skill. Acknowledge the issue, document the root cause, implement corrective measures, and communicate the resolution plan with transparency to stakeholders."),
            ("Strategy", ["strategy", "plan", "growth", "development"], "Strategic career planning requires a 3-5 year horizon with specific milestones. Identify your target role, assess skill gaps, create a development timeline, and regularly review progress against market changes."),
            ("Industry", ["industry", "market", "sector", "trend"], "Industry expertise requires continuous learning and strategic networking. Subscribe to key publications, attend industry conferences, build relationships with thought leaders, and contribute to professional discussions.")
        ]
        
        found = False
        for category, keywords, response in responses:
            matched_keywords = [kw for kw in keywords if kw in lower]
            if matched_keywords:
                print(f"Step 2: Check {category} keywords: {keywords}")
                print(f"        -> Matched: {matched_keywords}")
                print(f"        -> RESPONSE CATEGORY: {category.upper()}")
                print()
                print(f"Step 3: Generate Response")
                print(f"        -> Response: {response}")
                found = True
                return response
                break
        
        if not found:
            print("Step 2: No specific topic keywords matched")
            print(f"        -> RESPONSE CATEGORY: GENERAL")
            print()
            print(f"Step 3: Generate Generic Response")
            generic_response = f"Regarding '{text}': In executive strategy, clarity and execution precede outcome. Focus on identifying root metrics, establishing clear boundaries, and delivering consistent strategic value."
            print(f"        -> Response: {generic_response}")
            return generic_response
    
    def full_analysis(self, user_input):
        """Complete analysis of user input."""
        print("=" * 70)
        print(f"    AURELIA-CHAN RESPONSE SYSTEM ANALYSIS")
        print("=" * 70)
        print()
        
        expression = self.analyze_expression_step_by_step(user_input)
        response = self.get_response_step_by_step(user_input)
        
        print()
        print("=" * 70)
        print("    FINAL RESULT")
        print("=" * 70)
        print(f"Input: {user_input}")
        print(f"Expression: {expression.upper()}")
        print(f"Response: {response}")
        print("=" * 70)

def main():
    explainer = AureliaChatExplainer()
    
    # Test examples showing different scenarios
    test_inputs = [
        "I need leadership help",
        "I'm feeling stressed at work",
        "Can you help me with my resume?",
        "Thank you for your help",
        "I made a mistake in my presentation",
        "Hello Aurelia",
        "How do I handle salary negotiations?",
        "What's the best strategy for career growth?"
        "Great job on the project",
        "I'm unsure about my career direction"
    ]
    
    for user_input in test_inputs:
        explainer.full_analysis(user_input)
        print("\n")

if __name__ == "__main__":
    main()