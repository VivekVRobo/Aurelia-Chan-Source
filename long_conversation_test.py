#!/usr/bin/env python3
"""
Aurelia-chan Extended Conversation Test
========================================
Simulates 1000+ conversation turns to test response consistency,
topic coverage, and expression changes across various career scenarios.
"""

import random
import time
from datetime import datetime

class AureliaChat:
    def __init__(self):
        self.current_expression = "neutral"
        self.conversation_count = 0
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
        
        # Extended conversation topics
        self.topics = {
            "greeting": [
                "Hello", "Hi there", "Good morning", "Good afternoon", "Hey",
                "Hi Aurelia", "Hello Aurelia-chan", "Good day", "Greetings"
            ],
            "promotion": [
                "I want a promotion", "How do I get promoted?", "I deserve a raise",
                "When should I ask for a promotion?", "My boss won't promote me",
                "I've been here 3 years, no promotion", "Promotion advice needed",
                "How to negotiate a promotion?", "I'm ready for the next level"
            ],
            "resume": [
                "Can you help me with my resume?", "Resume tips please", "My resume needs work",
                "How to improve my CV?", "Resume writing advice", "Executive resume help",
                "Is my resume good enough?", "Resume for senior role",
                "CV for executive position", "Best resume format?"
            ],
            "leadership": [
                "I need to improve my leadership skills", "How to be a better manager?",
                "Leadership development tips", "Team management advice", "Executive leadership",
                "How to lead effectively?", "My team is underperforming",
                "Leadership challenges", "Management vs leadership"
            ],
            "stress": [
                "I'm feeling stressed at work", "Work burnout", "I'm overwhelmed",
                "Too much work stress", "Job burnout symptoms", "Work-life balance",
                "I can't handle the pressure", "Stress management at work",
                "Feeling burned out", "Work stress is affecting me"
            ],
            "salary": [
                "How do I handle salary negotiations?", "Salary negotiation tips",
                "I need a raise", "How to ask for more money?", "Salary discussion advice",
                "Market rate research", "Compensation negotiation",
                "Pay raise conversation", "Salary expectations for executive role"
            ],
            "interview": [
                "Interview preparation tips", "How to ace an executive interview?",
                "Common interview questions", "STAR method interview", "Executive interview",
                "Panel interview advice", "Behavioral interview questions",
                "Final round interview tips", "Interview nervousness"
            ],
            "strategy": [
                "Career growth strategy", "Long-term career planning", "Strategic career moves",
                "Career pivot advice", "Industry transition strategy", "Executive career path",
                "5-year career plan", "Career advancement strategy", "Professional development plan",
                "Strategic networking", "Career development", "Growth plan"
            ],
            "feedback": [
                "Great job on the project", "Excellent work", "Impressive results",
                "Good performance review", "Positive feedback received", "Team success",
                "Project completion celebration", "Achievement unlocked",
                "Well done team", "Outstanding performance"
            ],
            "mistakes": [
                "I made a mistake at work", "Failed project", "Work error",
                "Professional mistake", "Career setback", " messed up at work",
                "Failed presentation", "Project failure", "Work blunder",
                "Need to fix a mistake"
            ],
            "networking": [
                "Networking advice for executives", "How to network effectively?",
                "Professional networking tips", "Building executive relationships",
                "LinkedIn networking strategy", "Industry networking events",
                "Executive networking", "Professional connections",
                "Career networking online", "Network building"
            ],
            "team_conflict": [
                "Team conflict resolution", "Dealing with difficult coworkers",
                "Workplace conflict", "Managing team disputes", "Employee conflict",
                "HR issue with colleague", "Workplace drama", "Team friction",
                "Interpersonal conflict at work", "Resolving work disputes"
            ],
            "gratitude": [
                "Thank you for your help", "Thanks Aurelia", "Appreciate the advice",
                "Thank you so much", "Grateful for guidance", "Thanks for the tips",
                "Your advice helped", "Thank you for mentoring", "Much appreciated"
            ],
            "time_management": [
                "Time management tips", "How to prioritize work?", "Executive time management",
                "Productivity advice", "Work prioritization", "Managing executive schedule",
                "Delegation strategies", "Work-life balance time", "Efficient working",
                "Calendar management for executives"
            ],
            "industry_knowledge": [
                "Industry trends", "Market analysis skills", "Competitive intelligence",
                "Staying current in industry", "Industry knowledge development",
                "Market research skills", "Business acumen development",
                "Sector expertise", "Industry networking", "Market awareness",
                "Industry learning", "Business trends", "Sector analysis"
            ],
            "communication": [
                "Executive communication skills", "Public speaking tips", "Presentation skills",
                "Executive presence", "Board meeting communication", "Stakeholder communication",
                "Email etiquette for executives", "Executive writing skills",
                "Persuasive communication", "Leadership communication"
            ],
            "mentoring": [
                "How to find a mentor?", "Being a good mentor", "Mentorship relationships",
                "Executive mentoring", "Career mentorship", "Professional mentorship advice",
                "Finding executive mentors", "Mentorship programs", "Reverse mentoring"
            ],
            "general": [
                "Career advice", "Professional development", "Work guidance",
                "Career help needed", "Professional growth", "Executive advice",
                "Career questions", "Work challenges", "Professional decisions",
                "General career help", "Professional guidance", "Career support"
            ],
            "critical": [
                "This is critical", "Urgent decision needed", "Crucial matter",
                "Important issue", "Critical situation", "Serious problem",
                "Urgent career matter", "Critical decision", "Important concern"
            ],
            "uncertain": [
                "I'm unsure about my career", "Unclear about next steps", "Vague career goals",
                "Confused about direction", "Unsure about promotion", "Doubt my skills",
                "Uncertain about industry", "Vague on objectives", "Confused career path"
            ],
            "disappointment": [
                "I'm disappointed with my progress", "Let down by my role", "Underwhelmed by job",
                "Not meeting expectations", "Career disappointment", "Failed expectations",
                "Disappointed in growth", "Underwhelmed by opportunities"
            ]
        }
    
    def analyze_expression(self, text):
        """Determine appropriate expression based on text content."""
        lower = text.lower()
        
        # Priority order for expression matching (most specific first)
        if any(word in lower for word in ["mistake", "fail", "warning", "never", "avoid", "error", "failure"]):
            return "warning"
        elif any(word in lower for word in ["doubt", "claim", "unclear", "vague", "unsure", "confused"]):
            return "skeptical"
        elif any(word in lower for word in ["serious", "critical", "crucial", "urgent", "important"]):
            return "serious"
        elif any(word in lower for word in ["disappointed", "let down", "underwhelmed", "expectation"]):
            return "disappointed"
        elif any(word in lower for word in ["problem", "stress", "burnout", "difficult", "tired", "overwhelmed", "struggle", "exhausted"]):
            return "concerned"
        elif any(word in lower for word in ["good", "excellent", "great", "impressive", "congratulations", "success", "achievement", "well done"]):
            return "approval"
        elif any(word in lower for word in ["analyze", "resume", "data", "audit", "metrics", "analysis", "research", "market"]):
            return "analyzing"
        elif any(word in lower for word in ["leadership", "manage", "team", "leader", "executive", "vision", "strategy"]):
            return "confident"
        elif any(word in lower for word in ["help", "guidance", "support", "mentor", "thank", "thanks", "appreciate"]):
            return "empathetic"
        elif any(word in lower for word in ["hello", "hi", "hey", "greetings", "good morning", "good afternoon"]):
            return "focused"
        else:
            return "neutral"
    
    def get_response(self, user_text):
        """Generate Aurelia's response based on user input."""
        self.current_expression = self.analyze_expression(user_text)
        self.conversation_count += 1
        
        lower = user_text.lower()
        
        # More specific topic detection with priority order
        if any(word in lower for word in ["leadership", "manage", "team"]):
            return "Executive leadership requires balancing strategic vision with operational execution. Focus on developing your team, removing obstacles, and creating an environment where high performers can thrive."
        elif any(word in lower for word in ["hello", "hi", "hey", "greetings"]):
            return "Greetings. I am fully focused on your professional growth. What career milestone or strategic challenge shall we tackle next?"
        elif any(word in lower for word in ["promote", "promotion", "raise"]):
            return "Securing a promotion requires proving value before asking for the title. Document your quantifiable impact, build cross-functional alliances, and present a structured case to leadership."
        elif any(word in lower for word in ["resume", "cv"]):
            return "To make your resume executive-ready, shift from listing duties to highlighting key achievements with hard metrics (e.g., 'Increased revenue by 35%'). Try our Resume Audit tab!"
        elif any(word in lower for word in ["interview", "question"]):
            return "For executive interviews, focus on the STAR method: Situation, Task, Action, Result. Lead with outcomes, maintain emotional composure, and always tie answers to business impact."
        elif any(word in lower for word in ["stress", "burnout", "tired", "overwhelmed", "exhausted"]):
            return "Burnout is a strategic risk, not a personal failure. Assess your boundaries, document excessive workloads, and approach leadership with data on how current demands impact long-term productivity."
        elif any(word in lower for word in ["salary", "money", "pay", "compensation"]):
            return "Compensation negotiations should be data-driven. Research market rates, document your quantifiable impact, and present your case with specific examples of business value you've delivered."
        elif any(word in lower for word in ["network", "connection", "relationship"]):
            return "Strategic networking is about cultivating mutually beneficial professional relationships. Focus on providing value first, maintaining authentic connections, and consistently following up with meaningful interactions."
        elif any(word in lower for word in ["conflict", "dispute", "difficult", "drama"]):
            return "Workplace conflict requires strategic intervention. Document specific incidents, address issues privately and professionally, and focus on solutions rather than personal grievances when escalating to HR."
        elif any(word in lower for word in ["time", "prioritize", "productivity", "schedule"]):
            return "Executive time management hinges on ruthless prioritization. Identify your highest-impact activities, delegate operational tasks, and protect strategic thinking time in your calendar as you would any client meeting."
        elif any(word in lower for word in ["communication", "speak", "present", "write"]):
            return "Executive communication demands clarity, brevity, and strategic intent. Structure every interaction with your objective in mind, tailor your message to your audience, and always end with clear next steps."
        elif any(word in lower for word in ["mentor", "guidance", "advice"]):
            return "Effective mentorship requires both strategic guidance and emotional intelligence. Seek mentors who challenge your thinking while supporting your growth, and be prepared to bring specific scenarios to your mentoring relationships."
        elif any(word in lower for word in ["thank", "thanks", "appreciate"]):
            return "You are welcome. Continuous professional development and strategic thinking are the hallmarks of executive growth. What other challenges can we address?"
        elif any(word in lower for word in ["good", "great", "excellent", "impressive", "success", "achievement"]):
            return "Excellent work. Recognizing achievement is important, but ensure you document the specific metrics and business impact that made this success possible for future reference."
        elif any(word in lower for word in ["mistake", "fail", "error", "failure"]):
            return "Executive composure during setbacks is a critical skill. Acknowledge the issue, document the root cause, implement corrective measures, and communicate the resolution plan with transparency to stakeholders."
        elif any(word in lower for word in ["strategy", "plan", "growth", "development"]):
            return "Strategic career planning requires a 3-5 year horizon with specific milestones. Identify your target role, assess skill gaps, create a development timeline, and regularly review progress against market changes."
        elif any(word in lower for word in ["industry", "market", "sector", "trend"]):
            return "Industry expertise requires continuous learning and strategic networking. Subscribe to key publications, attend industry conferences, build relationships with thought leaders, and contribute to professional discussions."
        else:
            return f"Regarding '{user_text}': In executive strategy, clarity and execution precede outcome. Focus on identifying root metrics, establishing clear boundaries, and delivering consistent strategic value."
    
    def simulate_conversation(self, num_turns=1000):
        """Simulate a long conversation with random topics."""
        print("=" * 70)
        print(f"    AURELIA-CHAN — Extended Conversation Test ({num_turns} turns)")
        print("=" * 70)
        print()
        
        # Flatten all topics into a single list
        all_inputs = []
        for category, inputs in self.topics.items():
            all_inputs.extend([(category, inp) for inp in inputs])
        
        # Add some generic inputs to reach the target number
        generic_inputs = [
            "Career advice needed", "Professional growth question", "Work challenge",
            "Executive decision help", "Strategic career move", "Professional development",
            "Career guidance", "Work situation", "Executive dilemma", "Career planning",
            "General career help", "Professional guidance", "Career support"
        ]
        
        # Extend to reach desired number of turns
        while len(all_inputs) < num_turns:
            category = random.choice(list(self.topics.keys()))
            if category in self.topics:
                inp = random.choice(self.topics[category])
                all_inputs.append((category, inp))
            else:
                all_inputs.append(("general", random.choice(generic_inputs)))
        
        # Shuffle for variety
        random.shuffle(all_inputs)
        
        # Track statistics
        expression_counts = {expr: 0 for expr in self.expressions.keys()}
        category_counts = {}
        for cat in self.topics.keys():
            category_counts[cat] = 0
        response_lengths = []
        
        start_time = time.time()
        
        for i, (category, user_input) in enumerate(all_inputs[:num_turns], 1):
            response = self.get_response(user_input)
            expression_counts[self.current_expression] += 1
            category_counts[category] += 1
            response_lengths.append(len(response))
            
            # Print every 100th turn and first/last few
            if i <= 5 or i % 100 == 0 or i >= num_turns - 2:
                print(f"Turn {i}/{num_turns} [{category.upper()}]")
                print(f"You: {user_input}")
                print(f"[{self.current_expression.upper()}] Aurelia: {response[:100]}...")
                print()
        
        elapsed = time.time() - start_time
        
        # Print statistics
        print("=" * 70)
        print("    CONVERSATION STATISTICS")
        print("=" * 70)
        print(f"Total turns: {self.conversation_count}")
        print(f"Elapsed time: {elapsed:.2f} seconds")
        print(f"Average response time: {(elapsed/num_turns)*1000:.2f}ms")
        print()
        
        print("Expression Distribution:")
        for expr, count in sorted(expression_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / num_turns) * 100
            print(f"  {self.expressions[expr]}: {count} ({percentage:.1f}%)")
        print()
        
        print("Topic Distribution:")
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / num_turns) * 100
            print(f"  {cat.upper()}: {count} ({percentage:.1f}%)")
        print()
        
        if response_lengths:
            print(f"Response Length Statistics:")
            print(f"  Average: {sum(response_lengths)/len(response_lengths):.1f} characters")
            print(f"  Min: {min(response_lengths)} characters")
            print(f"  Max: {max(response_lengths)} characters")
        print()
        
        print("=" * 70)
        print("Extended Conversation Test Complete")
        print("=" * 70)

def main():
    chat = AureliaChat()
    
    # You can adjust the number of conversation turns
    num_turns = 1000
    
    chat.simulate_conversation(num_turns)

if __name__ == "__main__":
    main()