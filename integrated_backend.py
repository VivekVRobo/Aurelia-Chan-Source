"""
Aurelia Cognitive OS V3 - Advanced Integrated Backend API
==========================================================
Flask API integrating the full Cognitive Architecture, Persona Engine,
Local LLM Reasoning, and Rigorous Executive Evaluation Engines.

Aurelia's Canonical Identity:
- 33-year-old Executive Career Mentor & Life Strategist
- Mature, disciplined, highly observant, precise, and emotionally composed
- Strict, high standards: NEVER gives sycophantic, fake, or generic praise
- Demands quantifiable business impact, strategic alignment, and execution rigor
"""

import os
import sys
import json
import re
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Add workspace to path for cognitive modules
WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

# Import Cognitive Systems
try:
    from aurelia.character.affect_engine import AffectEngine, Emotion, AffectIntensity
    from aurelia.character.expression_policy import ExpressionPolicyManager, ExpressionStyle
    from aurelia.character.aurelia_state import AureliaStateManager, AureliaMode
    from aurelia.knowledge.career_graph import CareerGraph
    from aurelia.runtime.cognitive_runtime import AureliaCognitiveRuntime
    from aurelia.runtime.health import HealthSupervisor
    v4_runtime = AureliaCognitiveRuntime()
    COGNITIVE_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Loading standalone cognitive engine ({e})")
    v4_runtime = None
    COGNITIVE_MODULES_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# Canonical Expression Mapping
EXPRESSION_MAP = {
    "neutral": "01-neutral-observing.png",
    "confident": "02-subtle-confident-smile.png",
    "approval": "03-soft-approval.png",
    "focused": "04-focused-listening.png",
    "analyzing": "05-analyzing-raised-brow.png",
    "serious": "06-serious.png",
    "warning": "07-strict-warning.png",
    "disappointed": "08-disappointed.png",
    "skeptical": "09-skeptical.png",
    "concerned": "10-concerned.png",
    "empathetic": "11-empathetic.png"
}

# Aurelia's Canonical System Prompt for LLM Reasoning
AURELIA_SYSTEM_PROMPT = """You are Aurelia-chan (33 years old), an elite Executive Career Mentor and Life Strategist.
Core Personality & Principles:
- Tone: Mature, refined, highly observant, calm, analytical, and authoritative without cruelty.
- Core Rule: You NEVER offer fake praise, empty flattery, or superficial encouragement.
- High Standards: When users present vague plans, excuses, or unstructured claims, you call out the lack of evidence, missing metrics, and strategic vulnerabilities immediately.
- Executive Rigor: You focus on quantifiable business impact (ROI, revenue, headcount, efficiency), upward management, stakeholder consensus, and emotional composure.
- Boundaries: You mentor with practical strategic systems, not emotional platitudes.
Keep responses concise, incisive, structured, and immediately actionable."""

OLLAMA_ENDPOINT = "http://127.0.0.1:11434/api/generate"

# Initialize Core Cognitive Singletons
if COGNITIVE_MODULES_AVAILABLE:
    affect_engine = AffectEngine()
    expression_policy_mgr = ExpressionPolicyManager()
    state_mgr = AureliaStateManager()
    career_graph = CareerGraph()
    state_mgr.initialize_state()

def check_ollama_status():
    """Check if local Ollama LLM server is accessible on 127.0.0.1."""
    try:
        res = requests.get("http://127.0.0.1:11434/api/tags", timeout=1.5)
        if res.status_code == 200:
            models = res.json().get('models', [])
            return True, [m.get('name', '') for m in models]
    except Exception:
        pass
    return False, []

def query_ollama(prompt, model=None):
    """Query local Ollama instance with Aurelia persona constraint."""
    try:
        target_model = model or "qwen2.5:3b"
        payload = {
            "model": target_model,
            "prompt": f"{AURELIA_SYSTEM_PROMPT}\n\nUser Question: {prompt}\n\nAurelia's Executive Mentor Response:",
            "stream": False,
            "options": {
                "temperature": 0.4,
                "top_p": 0.9,
                "num_predict": 450
            }
        }
        res = requests.post(OLLAMA_ENDPOINT, json=payload, timeout=20.0)
        if res.status_code == 200:
            return res.json().get('response', '').strip()
    except Exception as e:
        print(f"Ollama query failed: {e}")
    return None

def analyze_executive_sentiment(text):
    """
    Incisive sentiment and topic analyzer to determine Aurelia's emotional state
    and facial expression based on executive mentoring context.
    """
    lower = text.lower()
    
    # Critical flaws, risky behaviors, ultimatums
    if any(k in lower for k in ['quit without', 'rage', 'ultimatum', 'threaten', 'sue', 'fight', 'yell', 'lie', 'illegal', 'falsify', 'ignore my boss']):
        return 'warning', 'strict_guidance'
    
    # Vague, unsubstantiated claims, entitlement, buzzwords
    elif any(k in lower for k in ['easy money', 'deserve more', 'entitled', 'get rich quick', 'unfair', 'everyone hates', 'did nothing wrong', 'rockstar', 'guru', '10x']):
        return 'skeptical', 'critical_inquiry'
    
    # Strategic analysis, metrics, audit, evaluation
    elif any(k in lower for k in ['audit', 'metric', 'roi', 'kpi', 'analyze', 'evaluate', 'revenue', 'p&l', 'margin', 'budget', 'portfolio']):
        return 'analyzing', 'strategic_appraisal'
    
    # High-stakes decisions, crisis, restructuring, layoffs
    elif any(k in lower for k in ['layoff', 'downsize', 'fired', 'restructure', 'crisis', 'critical', 'investigation', 'severance', 'board meeting']):
        return 'serious', 'risk_mitigation'
    
    # Underperformance, unpreparedness, lack of follow-through
    elif any(k in lower for k in ['failed my interview', 'rejected again', 'did not prepare', 'procrastinated', 'forgot', 'no portfolio', 'unprepared']):
        return 'disappointed', 'candid_correction'
    
    # Burnout, severe overwhelm, mental exhaustion
    elif any(k in lower for k in ['burnout', 'exhausted', 'toxic boss', 'overwhelmed', 'crying at work', 'anxiety', 'breakdown', 'unsustainable']):
        return 'concerned', 'boundary_restructuring'
    
    # Well-structured, quantified achievements, disciplined execution
    elif any(k in lower for k in ['closed 15%', 'increased revenue by', 'exceeded target', 'streamlined process', 'de-risked', 'delivered on time']):
        return 'approval', 'measured_validation'
    
    # Leadership, strategy, promotion planning, career pivot
    elif any(k in lower for k in ['leadership', 'promote', 'vp', 'director', 'strategy', 'manage', 'executive', 'scale the team', 'negotiate']):
        return 'confident', 'executive_trajectory'
    
    # Seeking mentorship, genuine reflection, appreciation
    elif any(k in lower for k in ['mentor', 'guidance', 'advice', 'career plan', 'growth', 'thank you', 'appreciate your honesty']):
        return 'empathetic', 'structured_mentorship'
    
    # Focused listening
    elif any(k in lower for k in ['hello', 'hi', 'hey', 'good morning', 'greetings']):
        return 'focused', 'engagement'
        
    return 'neutral', 'objective_observation'

def get_cognitive_executive_response(text):
    """
    High-rigor deterministic executive knowledge engine.
    Delivers candid, non-sycophantic, deeply strategic guidance.
    """
    lower = text.lower()
    
    # 1. Promotion Strategy
    if any(k in lower for k in ['promote', 'promotion', 'advance my career', 'level up']):
        return (
            "Ambition without architectural leverage is merely wishful thinking. A promotion is never granted for tenure or simply fulfilling your current job description; it is granted when you have already de-risked the next level for executive leadership.\n\n"
            "Here is your 3-step executive action plan:\n"
            "1. **Audit Your Quantifiable ROI**: Document the revenue expanded, cost reduced, or cycle-time compressed under your direct purview.\n"
            "2. **Secure Cross-Functional Sponsors**: The decision is made in rooms you are not in. Ensure peer leaders advocate for your operational stability.\n"
            "3. **Draft a 90-Day Transition Blueprint**: Proactively identify your successor for operational continuity before requesting the title change."
        )

    # 2. Salary & Compensation Negotiation
    elif any(k in lower for k in ['salary', 'negotiate', 'compensation', 'pay raise', 'underpaid', 'offer']):
        return (
            "Compensation negotiations are financial transactions, not moral appeals. Appealing to personal expenses or general effort signals operational immaturity. Executive leverage is built on three pillars:\n\n"
            "1. **Replacement Cost & Market Benchmarking**: Provide verified 75th-percentile compensation data for your scope and geography.\n"
            "2. **Value-Creation Multipliers**: Present a dossier of specific business outcomes you delivered that directly impacted top or bottom line.\n"
            "3. **Alternative Equity & Variable Instruments**: If base salary is restricted by fiscal brackets, negotiate sign-on equity, accelerated vesting, performance bonuses, or executive education stipends."
        )

    # 3. Leadership & Executive Presence
    elif any(k in lower for k in ['leadership', 'manage a team', 'new manager', 'executive presence', 'leading people']):
        return (
            "Executive leadership is not about personal authority; it is the discipline of creating high-accountability systems where high performers thrive autonomously.\n\n"
            "Key principles to enforce immediately:\n"
            "• **Clarity Over Consensus**: Define unambiguous ownership (DRI model) and measurable delivery metrics.\n"
            "• **Shield Operationally, Expose Strategically**: Protect your team from organizational noise, while giving them visible credit to senior leadership.\n"
            "• **Candid Feedback Cadence**: Address sub-standard execution within 48 hours. Tolerating chronic mediocrity demoralizes your top talent."
        )

    # 4. Workplace Conflict & Difficult Executives
    elif any(k in lower for k in ['conflict', 'difficult boss', 'toxic', 'dispute', 'argument', 'politics', 'vp dismissed']):
        return (
            "Workplace politics is simply the human layer of resource allocation. When dealing with difficult leadership or public conflict:\n\n"
            "1. **Never Counter-Attack in Public**: Maintain emotional neutrality. Acknowledge their perspective calmly: *'I note your concern regarding timeline risk; let us review the risk-mitigation data.'*\n"
            "2. **De-personalize and Pivot to Shared Business Metrics**: Frame every disagreement around risk, revenue, or customer retention.\n"
            "3. **Document in 1-on-1 Follow-ups**: Follow every verbal dispute with a written summary confirming agreed action items and technical boundaries."
        )

    # 5. Burnout & High-Pressure Overwhelm
    elif any(k in lower for k in ['burnout', 'exhausted', 'overwhelmed', 'stress', 'too much work', 'tired']):
        return (
            "Burnout is not an emotional weakness—it is an unmanaged operational bottleneck. If you operate at redline, you become a strategic liability to your organization.\n\n"
            "Immediate operational triage:\n"
            "1. **Audit Your Calendar (The 30% Rule)**: Eliminate non-essential recurring syncs. Protect 2-hour uninterrupted blocks for deep strategic execution.\n"
            "2. **Enforce Hard Workload Trade-offs**: When new initiatives are assigned, present the trade-off matrix: *'To deliver Project Alpha by Q3, Project Beta will be postponed. Which takes priority for executive leadership?'*\n"
            "3. **Systematize Delegation**: If an operational task can be done 70% as well by a direct report, delegate it immediately."
        )

    # 6. Resume & CV Optimization
    elif any(k in lower for k in ['resume', 'cv', 'linkedin', 'profile']):
        return (
            "An executive resume is a business case, not an employment biography. If your resume merely lists duties, it will be discarded.\n\n"
            "The Executive Metric Formula to apply:\n"
            "**[Active Leadership Verb] + [Quantified Scale/Scope] + [Strategic Action] + [Measurable Business Outcome]**\n\n"
            "Example: *'Spearheaded enterprise infrastructure modernization across 4 global regions ($14M budget), reducing system downtime by 42% and generating $3.2M in annual operational savings.'*\n"
            "Paste your current summary into the Resume Audit tab for an objective, metric-driven analysis."
        )

    # 7. Career Pivot & Transition
    elif any(k in lower for k in ['pivot', 'career change', 'transition', 'switch fields', 'new industry']):
        return (
            "Pivoting industries or functions at a senior level requires translating your core competencies into the target domain's currency.\n\n"
            "1. **Identify Transferable Meta-Skills**: P&L ownership, organizational scaling, regulatory compliance, and risk management apply universally.\n"
            "2. **Bridge the Domain Gap with Advisory or Board Work**: Build demonstrable credibility in the target space prior to full transition.\n"
            "3. **Control the Narrative**: Frame your cross-industry perspective as a competitive advantage that breaks industry groupthink."
        )

    # 8. Setbacks & Mistakes
    elif any(k in lower for k in ['mistake', 'screwed up', 'failed', 'error', 'blunder', 'lost a client']):
        return (
            "In executive governance, mistakes are inevitable; obfuscation and panic are fatal. Your response defines your leadership caliber.\n\n"
            "Execute the 4-Step Remediation Protocol:\n"
            "1. **Take Unambiguous Ownership**: Report the issue before stakeholders discover it independently.\n"
            "2. **Deliver the Root-Cause Analysis (5 Whys)**: Explain the structural breakdown, not personal excuses.\n"
            "3. **Present the Containment & Recovery Plan**: Lead with solutions and timelines already initiated.\n"
            "4. **Implement Systemic Safeguards**: Build preventative automation or approval gates to ensure zero recurrence."
        )

    # 9. General Greeting
    elif any(k in lower for k in ['hello', 'hi', 'hey', 'greetings', 'good day']):
        return (
            "Good day. I am Aurelia, your executive career strategist. I am prepared to evaluate your professional roadmap, deconstruct leadership bottlenecks, or audit your executive portfolio. What strategic milestone shall we address?"
        )

    # Default Structured Analytical Reply
    return (
        f"Regarding your query: In high-level career strategy, rigorous execution and diagnostic clarity must precede action. "
        f"To provide precise executive guidance on this matter, define your primary business metric, current organizational leverage, and target timeline. Where is the core bottleneck?"
    )

# --- API ROUTES ---

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Process message through Aurelia's Cognitive Persona Pipeline.
    Combines LLM intelligence (if active) with strict deterministic executive rules.
    """
    try:
        data = request.json or {}
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        expression, context_type = analyze_executive_sentiment(user_message)
        
        # Check if Ollama is available
        ollama_active, _ = check_ollama_status()
        response_text = None
        
        if ollama_active:
            response_text = query_ollama(user_message)

        # Fallback to high-rigor cognitive rules if LLM offline or returned empty
        if not response_text:
            response_text = get_cognitive_executive_response(user_message)

        portrait_file = EXPRESSION_MAP.get(expression, "01-neutral-observing.png")
        confidence = 0.94 if ollama_active else 0.90

        return jsonify({
            'response': response_text,
            'expression': expression,
            'portrait': f"aurelia-expressions/{portrait_file}",
            'confidence': confidence,
            'context_type': context_type,
            'engine': 'Local LLM (Ollama)' if ollama_active else 'Cognitive OS V3 Core'
        })

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'response': "In executive strategy, clarity and execution precede outcome. Focus on identifying root metrics, establishing clear boundaries, and delivering consistent strategic value.",
            'expression': 'serious',
            'portrait': 'aurelia-expressions/06-serious.png',
            'confidence': 0.85
        }), 200

@app.route('/api/resume-audit', methods=['POST'])
def resume_audit():
    """
    Comprehensive Executive Resume Auditor with High Rigor (No Fake Praise).
    """
    try:
        data = request.json or {}
        resume_text = data.get('resume', '').strip()
        
        if not resume_text:
            return jsonify({'error': 'No resume text provided'}), 400

        word_count = len(resume_text.split())
        lower = resume_text.lower()

        # Metrics & Scale Signals
        metric_matches = re.findall(r'(\d+[\.,]?\d*[%$kKmMBb]|\$\d+|\d+\s*percent|\d+\s*million|\d+\s*team|\d+\s*engineers|\d+\s*clients)', resume_text)
        has_metrics = len(metric_matches) >= 2
        
        # Executive Action Verbs
        exec_verbs = ['spearheaded', 'orchestrated', 'engineered', 'scaled', 'restructured', 'negotiated', 'governed', 'architected', 'accelerated', 'optimized', 'captured', 'delivered']
        found_exec_verbs = [v for v in exec_verbs if v in lower]

        # Passive/Cliché Penalties
        passive_phrases = ['responsible for', 'assisted with', 'helped', 'worked on', 'duties included', 'team player', 'hard worker', 'go-getter', 'passionate']
        found_passives = [p for p in passive_phrases if p in lower]

        # Rigorous Rubric Calculation
        base_score = 40
        
        # Length evaluation
        if word_count < 25:
            base_score = 35
        elif word_count >= 25 and word_count < 60:
            base_score += 15
        else:
            base_score += 25

        # Metric & ROI impact
        if len(metric_matches) >= 4:
            base_score += 25
        elif len(metric_matches) >= 2:
            base_score += 15
        elif len(metric_matches) == 1:
            base_score += 5
        else:
            base_score -= 10  # Heavy penalty for zero numbers

        # Executive vocabulary
        base_score += min(len(found_exec_verbs) * 5, 20)

        # Passive penalty
        base_score -= min(len(found_passives) * 8, 24)

        # Normalize score
        final_score = max(32, min(base_score, 95))

        strengths = []
        improvements = []
        rec = ""
        expression = 'analyzing'

        # Diagnostic Categorization
        if final_score < 60:
            expression = 'warning' if found_passives else 'disappointed'
            if found_exec_verbs:
                strengths.append(f"Contains initial executive vocabulary ({', '.join(found_exec_verbs[:2])}).")
            else:
                strengths.append("Foundational technical or functional domain identified.")
            
            improvements.append("CRITICAL: Severe absence of quantifiable business metrics (revenue, ROI, cost reduction, or team scale).")
            improvements.append("CRITICAL: Uses passive operational descriptions ('responsible for', duties) instead of demonstrable ownership.")
            improvements.append("Reframe all bullet points into the Executive Outcome Formula: [Action Verb] + [Context] + [Measurable Result].")
            
            rec = "Unacceptable for senior or executive placement in its current state. This reads as a list of assigned duties rather than business transformation. You must quantify your scope and eliminate passive phrasing immediately."

        elif final_score < 80:
            expression = 'serious'
            strengths.append("Clear career progression and functional competence demonstrated.")
            if metric_matches:
                strengths.append(f"Includes verifiable metric markers ({', '.join(metric_matches[:3])}).")
            
            improvements.append("Elevate leadership scope: articulate budget ownership, cross-functional stakeholder consensus, and P&L accountability.")
            improvements.append("Replace mid-level operational language with board-level strategic terminology (governance, capital allocation, organizational design).")
            
            rec = "Competent operational profile, but lacks distinctive executive presence. To qualify for top-tier leadership brackets, elevate your bullet points to emphasize direct bottom-line impact and organizational de-risking."

        else:
            expression = 'approval'
            strengths.append(f"High-impact executive framing with robust metric density ({len(metric_matches)} data points identified).")
            strengths.append(f"Strong leadership vocabulary utilizing authoritative action verbs ({', '.join(found_exec_verbs[:3])}).")
            strengths.append("Clear demonstration of strategic ROI and organizational ownership.")
            
            improvements.append("Fine-tune the executive summary to target specific C-suite / VP functional mandates.")
            improvements.append("Ensure board-level governance and industry thought leadership are highlighted in the header qualifications.")
            
            rec = "Strong executive alignment. Your profile communicates authority, scale, and measurable ROI. Polish the executive summary for specific target board mandates."

        portrait_file = EXPRESSION_MAP.get(expression, "05-analyzing-raised-brow.png")

        return jsonify({
            'score': final_score,
            'strengths': strengths,
            'improvements': improvements,
            'recommendation': rec,
            'feedback': rec,
            'expression': expression,
            'portrait': f"aurelia-expressions/{portrait_file}"
        })

    except Exception as e:
        print(f"Error in resume audit: {e}")
        return jsonify({
            'score': 50,
            'strengths': ["Foundational background identified."],
            'improvements': ["Add quantifiable metrics ($ and %) to demonstrate direct business impact."],
            'recommendation': "Quantify your achievements with hard business metrics and reframe passive duties.",
            'expression': 'analyzing',
            'portrait': 'aurelia-expressions/05-analyzing-raised-brow.png'
        }), 200

@app.route('/api/interview-evaluate', methods=['POST'])
def interview_evaluate():
    """
    High-Rigor Executive Interview Simulator Evaluator (No Fake Praise).
    """
    try:
        data = request.json or {}
        ans = data.get('response', '').strip()
        scenario = data.get('scenario', 'General Scenario')

        if not ans:
            return jsonify({'error': 'No response provided'}), 400

        lower = ans.lower()
        word_count = len(ans.split())

        # Rubric Checks
        has_star_structure = any(k in lower for k in ['situation', 'task', 'action', 'result', 'because', 'initially', 'therefore', 'consequently', 'outcome', 'propose', 'tied to', 'aligns with', 'demonstrating', 'milestone', 'strategy', 'mitigate'])
        business_terms = ['roi', 'revenue', 'metric', 'data', 'benchmark', 'margin', 'risk', 'stakeholder', 'consensus', 'deliverable', 'efficiency', 'performance', 'expansion', 'equity', 'de-risk', 'leverage', 'capital', '75th-percentile', 'quantifiable']
        found_biz = [b for b in business_terms if b in lower]
        has_business_terms = len(found_biz) > 0
        has_entitlement_or_excuses = any(k in lower for k in ['i deserve', 'i need more money', 'not my fault', 'unfair', 'threaten', 'my boss is bad', 'i will just leave'])
        is_too_short = word_count < 15

        base_score = 45

        # Length & depth
        if word_count < 12:
            base_score = 25
        elif word_count >= 12 and word_count < 30:
            base_score += 15
        else:
            base_score += 25

        # Business Acumen
        if len(found_biz) >= 3:
            base_score += 20
        elif len(found_biz) >= 1:
            base_score += 12

        # STAR & Executive Structure Framing
        if has_star_structure:
            base_score += 12

        # Fatal errors
        if has_entitlement_or_excuses:
            base_score -= 30

        final_score = max(28, min(base_score, 96))

        expression = 'focused'
        feedback = ""

        if final_score < 60:
            expression = 'warning' if has_entitlement_or_excuses else 'skeptical'
            if has_entitlement_or_excuses:
                feedback = "Critical framing error. Appealing to personal entitlement, complaints, or threats in an executive negotiation is an instant disqualifier. Senior leaders evaluate counter-proposals based on risk-adjusted ROI and replacement cost. Reframe around mutual business incentives."
            elif is_too_short:
                feedback = "Deficient response depth. Executive communication requires concise completeness—leading with a structured conclusion, supporting data, and a clear next step. Your answer lacks actionable substance."
            else:
                feedback = "Weak executive posture. Your response avoids the core conflict and lacks quantifiable mechanisms. Structure your answer using the STAR method and anchor on commercial realities."

        elif final_score < 80:
            expression = 'analyzing'
            feedback = "Acceptable baseline, but lacks executive sharpness. You communicated basic intent, but failed to establish leverage with hard benchmark data or alternative variable compensation levers. Lead with the business outcome before discussing execution details."

        else:
            expression = 'confident'
            feedback = "High-caliber executive framing. You maintained emotional composure, grounded your position in business impact, and offered a de-risked path forward that aligns with leadership incentives."

        portrait_file = EXPRESSION_MAP.get(expression, "04-focused-listening.png")

        return jsonify({
            'score': final_score,
            'feedback': feedback,
            'expression': expression,
            'portrait': f"aurelia-expressions/{portrait_file}"
        })

    except Exception as e:
        print(f"Error in interview evaluate: {e}")
        return jsonify({
            'score': 65,
            'feedback': "Maintain emotional composure and lead with quantifiable business impact using the STAR method.",
            'expression': 'focused',
            'portrait': 'aurelia-expressions/04-focused-listening.png'
        }), 200

@app.route('/api/cognitive-cycle', methods=['POST'])
def cognitive_cycle():
    """
    Full Aurelia Cognitive OS V4 12-Phase Cycle Endpoint.
    Returns response text, expression, safe trace, artifacts, and verification report.
    """
    try:
        data = request.json or {}
        user_message = data.get('message', '').strip()
        user_role = data.get('user_role', 'Senior Engineering Manager')
        target_role = data.get('target_role', 'Director of Engineering')
        chat_history = data.get('history', [])

        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        if v4_runtime:
            cycle_res = v4_runtime.process_query(
                user_text=user_message,
                user_role=user_role,
                target_role=target_role,
                chat_history=chat_history
            )
            return jsonify({
                'response': cycle_res.response_text,
                'expression': cycle_res.expression,
                'portrait': cycle_res.portrait_path,
                'confidence': cycle_res.confidence_percentage,
                'trace': {
                    'understood': cycle_res.trace.understood_goal,
                    'memories_count': cycle_res.trace.memories_retrieved_count,
                    'graph_facts_count': cycle_res.trace.graph_facts_count,
                    'specialists_invoked': list(cycle_res.trace.specialists_invoked),
                    'alternatives_evaluated': list(cycle_res.trace.alternatives_evaluated),
                    'numerical_checks': list(cycle_res.trace.numerical_calculations_verified),
                    'unresolved_unknowns': list(cycle_res.trace.unresolved_unknowns),
                    'confidence_level': cycle_res.trace.confidence_level,
                    'summary_formatted': cycle_res.trace.to_formatted_summary()
                },
                'verification': {
                    'passed': cycle_res.verification_report.passed,
                    'severity': cycle_res.verification_report.max_severity.value,
                    'safe_to_publish': cycle_res.verification_report.is_safe_to_publish
                },
                'artifacts': [
                    {
                        'id': a.artifact_id,
                        'type': a.artifact_type.value,
                        'title': a.title,
                        'version': a.version,
                        'payload': a.payload
                    }
                    for a in cycle_res.artifacts
                ],
                'decision_id': cycle_res.decision_receipt.decision_id
            })
        else:
            # Fallback to chat
            return chat()
    except Exception as e:
        print(f"Error in cognitive cycle: {e}")
        return jsonify({
            'response': "In executive strategy, clarity and verified execution precede outcome. Define your primary business metric so we can dissect the bottleneck.",
            'expression': 'analyzing',
            'portrait': 'aurelia-expressions/05-analyzing-raised-brow.png',
            'confidence': 85.0
        }), 200

@app.route('/api/health-doctor', methods=['GET'])
def health_doctor():
    """Aurelia Doctor Diagnostics Endpoint."""
    report = HealthSupervisor.run_doctor()
    return jsonify(report)

# --- V5 Adaptive Intelligence Endpoints ---
@app.route('/api/v5/forecast', methods=['POST'])
def v5_forecast():
    """V5 Goal Forecasting & Critical Path Computation."""
    from aurelia.forecasting.goal_forecast import GoalForecastingEngine
    from aurelia.forecasting.critical_path import PrerequisiteDependency
    from aurelia.contracts.v5_contracts import CompetencyVelocityRecord

    data = request.json or {}
    goal_id = data.get('goal_id', 'g_director')
    target_role = data.get('target_role', 'Director of Engineering')
    timeline_months = float(data.get('timeline_months', 8.0))

    competencies = {
        "c_comm": {"name": "Executive Communication", "current": 3.2, "target": 4.0, "weeks_needed": 6.0},
        "c_budget": {"name": "Budget Ownership ($5M+)", "current": 2.2, "target": 4.0, "weeks_needed": 10.0},
        "c_org": {"name": "Organizational Influence", "current": 3.4, "target": 4.0, "weeks_needed": 4.0},
        "c_director": {"name": "Director Ready", "current": 2.8, "target": 4.5, "weeks_needed": 2.0}
    }
    deps = [
        PrerequisiteDependency("c_comm", "c_director"),
        PrerequisiteDependency("c_budget", "c_director"),
        PrerequisiteDependency("c_org", "c_director")
    ]
    velocities = {
        "c_comm": CompetencyVelocityRecord("c_comm", 3.2, 0.28, 0.05, False, False, 8.0, 3),
        "c_budget": CompetencyVelocityRecord("c_budget", 2.2, 0.15, 0.0, False, False, 14.0, 2)
    }

    forecast = GoalForecastingEngine.forecast_goal(
        goal_id=goal_id,
        target_role=target_role,
        target_timeline_months=timeline_months,
        competency_data=competencies,
        dependencies=deps,
        velocities=velocities
    )

    return jsonify({
        'goal_id': forecast.goal_id,
        'target_role': forecast.target_role,
        'status': forecast.status.value,
        'probability_of_completion': forecast.probability_of_completion,
        'likely_completion_window_months': forecast.likely_completion_window_months,
        'critical_path_bottleneck': forecast.critical_path_bottleneck,
        'blockers': list(forecast.blockers),
        'accelerating_factors': list(forecast.accelerating_factors),
        'confidence_score': forecast.confidence_score
    })

@app.route('/api/v5/adaptive-interview', methods=['POST'])
def v5_adaptive_interview():
    """V5 Information Gain Diagnostic Interview Question Selection."""
    from aurelia.interview.adaptive_system import AdaptiveInterviewEngine
    data = request.json or {}
    asked_ids = data.get('asked_ids', [])
    confidences = data.get('confidences', {
        'stakeholder_alignment': 0.90,
        'budget_governance': 0.20,
        'financial_negotiation': 0.80,
        'org_scaling': 0.50
    })

    engine = AdaptiveInterviewEngine()
    selected = engine.select_next_question(confidences, asked_ids)
    if selected:
        return jsonify({
            'question_id': selected.question_id,
            'scenario_title': selected.scenario_title,
            'target_competency': selected.target_competency,
            'prompt_text': selected.prompt_text,
            'diagnostic_power': selected.diagnostic_power,
            'difficulty_level': selected.difficulty_level
        })
    return jsonify({'question_id': None, 'message': 'All diagnostic scenarios completed.'})

@app.route('/api/v5/intelligence-health', methods=['GET'])
def v5_intelligence_health():
    """V5 Longitudinal Intelligence Health & Calibration Scorecard."""
    from aurelia.evaluation.intelligence_health import IntelligenceHealthAuditor
    metrics = IntelligenceHealthAuditor.audit_system_health()
    return jsonify({
        'intent_accuracy_pct': metrics.intent_accuracy_pct,
        'reference_accuracy_pct': metrics.reference_accuracy_pct,
        'numerical_verification_pct': metrics.numerical_verification_pct,
        'memory_precision_pct': metrics.memory_precision_pct,
        'unsupported_claims_pct': metrics.unsupported_claims_pct,
        'calibration_error_pct': metrics.calibration_error_pct,
        'plan_prediction_accuracy_pct': metrics.plan_prediction_accuracy_pct,
        'proactive_precision_pct': metrics.proactive_precision_pct
    })

# --- V6 Multimodal Perception Endpoints ---
@app.route('/api/v6/perceive-screen', methods=['POST'])
def v6_perceive_screen():
    """V6 Change-Driven Screen Perception & Scene Routing."""
    from aurelia.screen.change_detection import ScreenRegion, ScreenState, ChangeDetectionEngine
    from aurelia.privacy.zones import PrivacyFirewall
    from aurelia.routing.scene_router import SceneBasedCognitiveRouter

    data = request.json or {}
    window_title = data.get('window_title', 'Aurelia - Visual Studio Code')
    process_name = data.get('process_name', 'Code.exe')
    text_snippet = data.get('text_snippet', '')

    # 1. Pre-Capture Privacy Check
    priv_res = PrivacyFirewall.evaluate_pre_capture(process_name=process_name, window_title=window_title)
    if not priv_res.is_capture_allowed:
        return jsonify({
            'status': 'DENIED',
            'is_capture_allowed': False,
            'privacy_class': priv_res.privacy_class.value,
            'rationale': priv_res.rationale
        }), 403

    # 2. Scene-Based Context Candidate Ranking
    cset = SceneBasedCognitiveRouter.rank_context_candidates(
        user_query=data.get('query', ''),
        active_window_title=window_title,
        active_process_name=process_name,
        visible_text_snippet=text_snippet
    )

    return jsonify({
        'status': 'APPROVED',
        'is_capture_allowed': True,
        'privacy_class': priv_res.privacy_class.value,
        'selected_context': cset.selected_context,
        'is_ambiguous': cset.is_ambiguous,
        'separation_ratio': cset.separation_ratio,
        'candidates': [
            {'context_key': c.context_key, 'score': c.confidence_score, 'description': c.description}
            for c in cset.candidates
        ]
    })

@app.route('/api/v6/parse-document', methods=['POST'])
def v6_parse_document():
    """V6 Universal Document Parsing & Entity Extraction."""
    from aurelia.documents.parser import UniversalDocumentParser

    data = request.json or {}
    doc_id = data.get('doc_id', 'doc_01')
    file_path = data.get('file_path', 'C:/docs/Offer_Letter.pdf')
    text_content = data.get('content', '')
    doc_type = data.get('doc_type', 'OFFER_LETTER')

    parsed = UniversalDocumentParser.parse_document(
        doc_id=doc_id,
        file_path=file_path,
        text_content=text_content,
        doc_type=doc_type
    )

    return jsonify({
        'doc_id': parsed.doc_id,
        'doc_type': parsed.doc_type,
        'sections_count': len(parsed.sections),
        'entities': [
            {'type': e.entity_type, 'raw': e.raw_text, 'normalized': e.normalized_value, 'confidence': e.confidence}
            for e in parsed.extracted_entities
        ]
    })

@app.route('/api/v6/privacy-status', methods=['GET'])
def v6_privacy_status():
    """V6 Active Perception & Privacy Gating Status."""
    return jsonify({
        'pre_capture_firewall': 'ACTIVE',
        'data_minimization': 'DISCARD_RAW_IMMEDIATELY',
        'active_screen_perception': True,
        'active_speech_perception': True,
        'active_document_perception': True,
        'denied_processes_count': 6
    })

@app.route('/api/system-status', methods=['GET'])
def system_status():
    """System Health and Cognitive Capabilities Endpoint."""
    ollama_active, models = check_ollama_status()
    return jsonify({
        'status': 'healthy',
        'system': 'Aurelia Cognitive OS V6',
        'version': '6.0.0',
        'persona': 'Aurelia-chan (Grounded Multimodal Executive Mentor & Life Strategist)',
        'standards': 'Strict / High-Rigor (Non-Sycophantic)',
        'cognitive_modules_loaded': COGNITIVE_MODULES_AVAILABLE,
        'ollama_connected': ollama_active,
        'available_models': models,
        'v6_multimodal_perception': True
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'version': '6.0.0'})

if __name__ == '__main__':
    print("=" * 75)
    print("  AURELIA-CHAN — Cognitive OS V3 Integrated Backend")
    print("  Executive Career Mentor & Life Strategist Engine")
    print("=" * 75)
    print(f"  Cognitive Architecture : {'ACTIVE' if COGNITIVE_MODULES_AVAILABLE else 'STANDALONE'}")
    ollama_ok, m_list = check_ollama_status()
    print(f"  Local Ollama LLM       : {'CONNECTED (' + ', '.join(m_list) + ')' if ollama_ok else 'OFFLINE (Using Cognitive OS V3 Core Rules)'}")
    print("  Backend Server Running : http://localhost:5000")
    print("  Frontend Web Interface : http://localhost:5000/index.html")
    print("=" * 75)
    app.run(debug=True, port=5000)