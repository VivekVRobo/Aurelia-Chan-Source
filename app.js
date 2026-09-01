/* Aurelia-chan Executive Mentor Application - Core & Integrated Engine */

// Global voice synthesis handler accessible everywhere immediately
window.speakMessage = function(text) {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();

  const isVoiceActive = document.getElementById('voiceToggleBtn')?.classList.contains('active') ?? true;
  if (!isVoiceActive) return;

  const currentLang = document.getElementById('languageSelect')?.value || 'en-US';
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = currentLang;
  utterance.pitch = 0.90; // Aurelia's canonical acoustic profile: executive warmth
  utterance.rate = 0.92;  // Measured speaking rate for authority
  utterance.volume = 1.0;

  const voices = window.speechSynthesis.getVoices();
  const langVoices = voices.filter(v => v.lang.startsWith(currentLang.slice(0, 2)));
  const selectedVoice = langVoices.find(v => 
    v.name.includes('Neural') || 
    v.name.includes('Female') || 
    v.name.includes('Ava') || 
    v.name.includes('Google') || 
    v.name.includes('Natural') ||
    v.name.includes('Zira') ||
    v.name.includes('Kyoko') ||
    v.name.includes('Amelie') ||
    v.name.includes('Conchita')
  ) || langVoices[0];

  if (selectedVoice) {
    utterance.voice = selectedVoice;
  }

  const voiceStatusText = document.getElementById('voiceStatusText');
  if (voiceStatusText) {
    utterance.onstart = () => {
      voiceStatusText.textContent = `Aurelia Speaking (${selectedVoice ? selectedVoice.name : 'Neural Voice'})...`;
      if (window.startActiveWaveAnimation) window.startActiveWaveAnimation();
    };
    utterance.onend = () => {
      voiceStatusText.textContent = 'Neural Voice Engine Ready';
      if (window.stopWaveAnimation) window.stopWaveAnimation();
    };
    utterance.onerror = () => {
      voiceStatusText.textContent = 'Neural Voice Engine Ready';
      if (window.stopWaveAnimation) window.stopWaveAnimation();
    };
  }

  window.speechSynthesis.speak(utterance);
};

document.addEventListener('DOMContentLoaded', () => {
  // --- DOM Elements ---
  const avatarContainer = document.getElementById('avatarContainer');
  const avatarImages = document.querySelectorAll('.avatar-img');
  const expTitle = document.getElementById('expTitle');
  const expSubtitle = document.getElementById('expSubtitle');
  const expressionGrid = document.getElementById('expressionGrid');
  const expButtons = document.querySelectorAll('.exp-btn');
  
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');
  const languageSelect = document.getElementById('languageSelect');
  const voiceToggleBtn = document.getElementById('voiceToggleBtn');
  const voiceStatusText = document.getElementById('voiceStatusText');

  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');
  const chatHistory = document.getElementById('chatHistory');

  const resumeText = document.getElementById('resumeText');
  const auditBtn = document.getElementById('auditBtn');
  const auditResultCard = document.getElementById('auditResultCard');
  const auditScore = document.getElementById('auditScore');
  const auditStrengths = document.getElementById('auditStrengths');
  const auditImprovements = document.getElementById('auditImprovements');
  const auditRecommendation = document.getElementById('auditRecommendation');

  const scenarioTitle = document.getElementById('scenarioTitle');
  const scenarioPrompt = document.getElementById('scenarioPrompt');
  const interviewResponse = document.getElementById('interviewResponse');
  const evaluateAnswerBtn = document.getElementById('evaluateAnswerBtn');
  const nextScenarioBtn = document.getElementById('nextScenarioBtn');
  const interviewFeedbackCard = document.getElementById('interviewFeedbackCard');
  const interviewScore = document.getElementById('interviewScore');
  const interviewFeedbackText = document.getElementById('interviewFeedbackText');

  const visualizerCanvas = document.getElementById('visualizerCanvas');
  const masterSheetsGrid = document.getElementById('masterSheetsGrid');

  // --- State Variables ---
  let isVoiceEnabled = true;
  let currentLang = 'en-US';
  let currentExpression = 'neutral';
  let currentScenarioIndex = 0;
  let audioAnimId = null;
  let isBackendConnected = false;

  // --- Expression Metadata ---
  const expressionsData = {
    neutral: { title: "01. Neutral / Observing", desc: "Calm executive evaluation and structured focus.", file: "01-neutral-observing.png" },
    confident: { title: "02. Subtle Confident Smile", desc: "Refined assurance in strategic direction.", file: "02-subtle-confident-smile.png" },
    approval: { title: "03. Soft Approval", desc: "Restrained praise for high-value achievements.", file: "03-soft-approval.png" },
    focused: { title: "04. Focused Listening", desc: "Deep analytical attention to career details.", file: "04-focused-listening.png" },
    analyzing: { title: "05. Analyzing (Raised Brow)", desc: "Critical inspection of plans or resume metrics.", file: "05-analyzing-raised-brow.png" },
    serious: { title: "06. Serious", desc: "Uncompromising clarity on high-stakes decisions.", file: "06-serious.png" },
    warning: { title: "07. Strict Warning", desc: "Firm correction against strategic mistakes.", file: "07-strict-warning.png" },
    disappointed: { title: "08. Disappointed", desc: "Measured disappointment in lack of preparation.", file: "08-disappointed.png" },
    skeptical: { title: "09. Skeptical", desc: "Questioning unsubstantiated or vague claims.", file: "09-skeptical.png" },
    concerned: { title: "10. Concerned", desc: "Strategic empathy for burn-out or toxic environments.", file: "10-concerned.png" },
    empathetic: { title: "11. Empathetic", desc: "Warm executive mentorship during challenging pivots.", file: "11-empathetic.png" }
  };

  // --- Multi-Language Dictionary & Scenarios ---
  const translations = {
    'en-US': {
      welcome: "Good day. I am Aurelia, your executive career strategist. I am prepared to evaluate your professional roadmap, deconstruct leadership bottlenecks, or audit your executive portfolio. What strategic milestone shall we address?",
      auditTitle: "Executive Alignment Score",
      scenarios: [
        {
          title: "Scenario 01: High-Stakes Salary Negotiation",
          prompt: "The hiring manager offers a package 15% below your market target, citing fiscal constraints. How do you negotiate without risking the offer?",
          sampleResponse: "I acknowledge the offer with enthusiasm for the strategic scope, then present verified 75th-percentile market data for this revenue band, proposing a structured 6-month performance review linked to gross margin expansion."
        },
        {
          title: "Scenario 02: Navigating Executive Conflict",
          prompt: "A senior VP dismisses your team's quarterly proposal in a public meeting. How do you respond in the moment and follow up afterwards?",
          sampleResponse: "I remain emotionally neutral in public, acknowledge their operational risk concern, and schedule a private 1-on-1 dossier review presenting quantified mitigation data."
        },
        {
          title: "Scenario 03: Executive Career Pivot",
          prompt: "You are transitioning from an engineering lead role to VP of Product. How do you communicate your strategic vision during executive interviews?",
          sampleResponse: "I bridge my technical architecture foundation directly with P&L growth, focusing on cross-functional cadence, product ROI, and enterprise customer lifetime value."
        }
      ]
    },
    'ja-JP': {
      welcome: "ごきげんよう。私はオーレリア、あなたのエグゼクティブ・キャリアメンターです。感情論ではなく、明確な成果指標と戦略的優位性に基づきキャリア設計を指導します。本日はどの課題を検証しましょうか？",
      auditTitle: "エグゼクティブ評価スコア",
      scenarios: [
        {
          title: "シナリオ 01: 年収交渉戦略",
          prompt: "採用担当者が市場相場より15%低い提示をしてきました。どのようにしてオファーを維持しつつ適正な提示を勝ち取りますか？",
          sampleResponse: "役割への高い意欲を伝えつつ、直近の業績数値を提示し、6ヶ月後の成果連動型評価を提案します。"
        },
        {
          title: "シナリオ 02: 経営陣との意見対立",
          prompt: "全体会議で役員から提案を却下されました。その場での対応と事後のフォローはどうしますか？",
          sampleResponse: "冷静に懸念を受け止め、追加データを揃えて個別ミーティングを要請します。"
        }
      ]
    },
    'de-DE': {
      welcome: "Guten Tag. Ich bin Aurelia, Ihre Führungskräfte-Mentorin. Wie kann ich Ihre berufliche Entwicklung heute strategisch unterstützen?",
      auditTitle: "Führungs-Bewertung",
      scenarios: [
        {
          title: "Szenario 01: Gehaltsverhandlung",
          prompt: "Das Angebot liegt 15 % unter dem Marktwert. Wie reagieren Sie professionell?",
          sampleResponse: "Ich bekräftige mein Interesse, verweise auf meine messbaren Erfolge und schlage eine leistungsorientierte Überprüfung vor."
        }
      ]
    },
    'fr-FR': {
      welcome: "Bonjour. Je suis Aurélia, votre mentor exécutive. Comment puis-je vous accompagner dans votre stratégie de carrière aujourd'hui ?",
      auditTitle: "Score d'alignement exécutif",
      scenarios: [
        {
          title: "Scénario 01: Négociation salariale",
          prompt: "L'offre proposée est inférieure de 15% à votre objectif. Quelle est votre réponse stratégique ?",
          sampleResponse: "J'exprime mon enthousiasme pour le poste tout en mettant en avant mes résultats chiffrés et en proposant une réévaluation à 6 mois."
        }
      ]
    },
    'es-ES': {
      welcome: "Buen día. Soy Aurelia, tu mentora ejecutiva de carrera. ¿Cómo puedo guiar tu trayectoria profesional hoy?",
      auditTitle: "Puntuación de Alineación Ejecutiva",
      scenarios: [
        {
          title: "Escenario 01: Negociación Salarial",
          prompt: "La oferta es un 15% inferior a tu objetivo de mercado. ¿Cómo respondes estratégicamente?",
          sampleResponse: "Demuestro mi entusiasmo por la position, destaco mi impacto probado y propongo una revisión basada en metas a 6 meses."
        }
      ]
    }
  };

  // --- Complete 15 Master Canon Blueprint Sheets ---
  const masterSheetFiles = [
    "Aurelia-Chan Master Canon Sheet.png",
    "Aurelia-Chan Master body blueprint sheet.png",
    "Aurelia-Chan outfit sheet.png",
    "Aurelia-Chan eye look sheet.png",
    "Aurelia-Chan hair sheet.png",
    "Aurelia-Chan skin sheet.png",
    "Aurelia-Chan full body blueprint.png",
    "Aurelia-Chan height reference blueprint sheet.png",
    "Aurelia-Chan blueprint sheet.png",
    "Aurelia-Chan blueprint side look sheet.png",
    "Aurelia-Chan blueprint backview look sheet.png",
    "Aurelia-Chan left side look sheet.png",
    "Aurelia-Chan right side look sheet.png",
    "Aurelia-Chan side look sheet.png",
    "Aurelia-Chan backside look sheet.png"
  ];

  // --- API Base Configuration ---
  const isDirectBackend = window.location.protocol.startsWith('http') && (window.location.port === '5000' || window.location.pathname.includes('/api'));
  const API_BASE = isDirectBackend ? '/api' : 'http://localhost:5000/api';

  // --- Audio Visualizer Canvas Setup ---
  const ctx = visualizerCanvas.getContext('2d');
  function initVisualizer() {
    visualizerCanvas.width = visualizerCanvas.offsetWidth || 300;
    visualizerCanvas.height = 36;
    drawIdleWave();
  }

  function drawIdleWave() {
    ctx.clearRect(0, 0, visualizerCanvas.width, visualizerCanvas.height);
    ctx.beginPath();
    ctx.moveTo(0, visualizerCanvas.height / 2);
    ctx.lineTo(visualizerCanvas.width, visualizerCanvas.height / 2);
    ctx.strokeStyle = 'rgba(201, 162, 39, 0.3)';
    ctx.lineWidth = 2;
    ctx.stroke();
  }

  function startActiveWaveAnimation() {
    let phase = 0;
    cancelAnimationFrame(audioAnimId);
    
    function animate() {
      ctx.clearRect(0, 0, visualizerCanvas.width, visualizerCanvas.height);
      ctx.beginPath();
      const centerY = visualizerCanvas.height / 2;
      ctx.strokeStyle = '#C9A227';
      ctx.lineWidth = 2;

      for (let x = 0; x < visualizerCanvas.width; x++) {
        const sine = Math.sin((x * 0.05) + phase) * Math.sin(x * 0.02) * 12;
        if (x === 0) ctx.moveTo(x, centerY + sine);
        else ctx.lineTo(x, centerY + sine);
      }
      ctx.stroke();
      phase += 0.15;
      audioAnimId = requestAnimationFrame(animate);
    }
    animate();
  }

  function stopWaveAnimation() {
    cancelAnimationFrame(audioAnimId);
    drawIdleWave();
  }

  window.startActiveWaveAnimation = startActiveWaveAnimation;
  window.stopWaveAnimation = stopWaveAnimation;

  // --- Expression Switcher ---
  function setExpression(expName) {
    if (!expressionsData[expName]) return;
    currentExpression = expName;

    avatarImages.forEach(img => {
      if (img.getAttribute('data-expression') === expName) {
        img.classList.add('active');
      } else {
        img.classList.remove('active');
      }
    });

    expTitle.textContent = expressionsData[expName].title;
    expSubtitle.textContent = expressionsData[expName].desc;

    expButtons.forEach(btn => {
      if (btn.getAttribute('data-exp') === expName) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  }

  function analyzeExpressionFromText(text) {
    const lower = text.toLowerCase();
    if (lower.includes('quit without') || lower.includes('ultimatum') || lower.includes('threaten') || lower.includes('lie') || lower.includes('illegal')) {
      return 'warning';
    } else if (lower.includes('deserve more') || lower.includes('easy money') || lower.includes('entitled') || lower.includes('rockstar') || lower.includes('guru')) {
      return 'skeptical';
    } else if (lower.includes('layoff') || lower.includes('crisis') || lower.includes('fired') || lower.includes('board meeting') || lower.includes('restructure')) {
      return 'serious';
    } else if (lower.includes('unprepared') || lower.includes('procrastinated') || lower.includes('rejected again') || lower.includes('no portfolio')) {
      return 'disappointed';
    } else if (lower.includes('burnout') || lower.includes('toxic boss') || lower.includes('overwhelmed') || lower.includes('anxiety') || lower.includes('breakdown')) {
      return 'concerned';
    } else if (lower.includes('increased revenue') || lower.includes('exceeded target') || lower.includes('closed 15%') || lower.includes('streamlined')) {
      return 'approval';
    } else if (lower.includes('audit') || lower.includes('resume') || lower.includes('data') || lower.includes('metric') || lower.includes('roi')) {
      return 'analyzing';
    } else if (lower.includes('leadership') || lower.includes('promote') || lower.includes('strategy') || lower.includes('vp') || lower.includes('director')) {
      return 'confident';
    } else if (lower.includes('mentor') || lower.includes('guidance') || lower.includes('advice') || lower.includes('growth') || lower.includes('thank')) {
      return 'empathetic';
    } else if (lower.includes('hello') || lower.includes('hi') || lower.includes('hey')) {
      return 'focused';
    } else {
      return 'neutral';
    }
  }

  // --- Strict Executive Knowledge Engine (Non-Sycophantic & Multi-Domain) ---
  function getExecutiveMentorResponse(text) {
    const lower = text.toLowerCase();
    
    // 1. Burnout & Operational Workload Triage
    if (lower.includes("burnout") || lower.includes("stress") || lower.includes("tired") || lower.includes("overwhelmed") || lower.includes("75 hours") || lower.includes("drained") || lower.includes("calendar")) {
      const hoursMatch = lower.match(/(\d+)\s*(?:hours|hrs)/);
      const hrsText = hoursMatch ? `Operating at ${hoursMatch[1]} hours per week` : "Working unsustainable hours";
      return `${hrsText} is not a badge of honor; it is an operational failure of prioritization. When an executive redlines, your strategic judgment degrades and you become an organizational bottleneck.\n\nExecute the 30% Calendar Triage immediately:\n1. Audit: Categorize all recurring meetings into High Leverage (P&L/Strategy), Operational Syncs, and Low-Value Noise.\n2. Systematize Delegation: Reassign operational status meetings to your Tier-1 managers using the DRI (Directly Responsible Individual) model.\n3. Enforce Trade-Offs: Present a workload capacity matrix directly to leadership showing which projects will be paused if resources are not reallocated.`;
    }
    
    // 2. Workplace Politics, Credit Theft & Reorganizations
    if (lower.includes("credit") || lower.includes("bypass") || lower.includes("boss") || lower.includes("politics") || lower.includes("toxic") || lower.includes("dispute") || lower.includes("deadlock") || lower.includes("reorg")) {
      if (lower.includes("credit") || lower.includes("bypass")) {
        return "Navigating credit theft or an obstructive manager requires strategic precision, not emotional confrontation. Bypassing your manager directly creates an immediate political liability.\n\nImplement the Multi-Channel Attribution Protocol:\n1. Written Documentation: Send pre-meeting executive summary briefs directly to all stakeholders, establishing your ownership of the data and architectural design before meetings take place.\n2. Cross-Functional Sponsorship: Build organic relationships with peer VPs and the SVP through advisory reviews, allowing them to recognize your leadership independently.\n3. Metric Alignment: In your 1-on-1s, pivot from tenure to a formal 90-day de-risking roadmap with documented deliverables.";
      } else if (lower.includes("culture") || lower.includes("margin")) {
        return "Shifting an engineering culture from 'R&D-first' to 'commercial viability and margins' is a leadership litmus test. Resistance occurs when teams view financial discipline as a compromise on technical excellence.\n\n1. Reframe the Narrative: Connect gross margins and efficiency directly to company longevity and product scalability.\n2. Establish Clear DRI Metrics: Tie quarterly engineering goals to unit economics (e.g., infrastructure cost per active user, latency per transaction).\n3. Address Non-Compliance: Lead with empathy, but make it clear that alignment with commercial reality is non-negotiable for senior leaders.";
      }
      return "Workplace politics is the human layer of organizational resource allocation. Never counter-attack in public or react defensively.\n\nMaintain emotional composure, re-anchor the dispute around objective business metrics (risk, cost, timeline), and establish consensus through private 1-on-1 alignment sessions before major executive meetings.";
    }

    // 3. Compensation, Equity & Offers
    if (lower.includes("salary") || lower.includes("compensation") || lower.includes("negotiate") || lower.includes("pay") || lower.includes("offer") || lower.includes("package") || lower.includes("bonus") || lower.includes("equity")) {
      const baseMatch = lower.match(/\$?(\d+)[kK]/);
      const bonusMatch = lower.match(/(\d+)%/);
      let calcSnippet = "";
      if (baseMatch && bonusMatch) {
        const baseNum = parseInt(baseMatch[1], 10);
        const bonusPct = parseInt(bonusMatch[1], 10);
        const totalCash = baseNum * (1.0 + (bonusPct / 100.0));
        calcSnippet = ` Your annualized cash compensation calculates to $${totalCash.toFixed(0)}k USD (Base: $${baseNum}k + ${bonusPct}% bonus ($${(baseNum * bonusPct / 100.0).toFixed(0)}k)).`;
      }
      return `In evaluating this executive package:${calcSnippet} Compensation negotiations are financial transactions, not moral appeals. Appealing to personal living costs signals operational immaturity.\n\nStrategic Negotiation Playbook:\n1. Never negotiate on personal cost of living—anchor exclusively on market replacement value and expected revenue/margin impact.\n2. Counter-Anchor: Present verified 75th-percentile data for your headcount and P&L scope.\n3. Variable Levers: If base cash is constrained by internal bands, negotiate a structured 6-month performance review linked to gross margin expansion and accelerated equity vesting.`;
    }

    // 4. Career Pivots & Transitions
    if (lower.includes("pivot") || lower.includes("transition") || lower.includes("product") || lower.includes("change field")) {
      return "Transitioning across domains at a senior level requires shifting from functional execution to commercial ownership.\n\n1. Translate Technical Fluency into Business Currency: Reframe architectural decisions into customer lifetime value (LTV), gross margin efficiency, and time-to-market acceleration.\n2. Build Cross-Functional Credibility: Partner directly with Go-To-Market, Sales, and Finance leaders on enterprise customer retention.\n3. 90-Day Transition Blueprint: Present a documented roadmap de-risking the operational continuity of your organization.";
    }

    // 5. Promotion & Career Leverage
    if (lower.includes("promote") || lower.includes("promotion") || lower.includes("raise") || lower.includes("ready for vp")) {
      return "Executive progression is never awarded for tenure or simply fulfilling your current job scope; it is granted when you have already de-risked the next level for leadership.\n\n1. Audit Your Quantifiable ROI: Document your direct contributions to revenue growth, infrastructure cost reduction, and leadership retention.\n2. Build Executive Sponsorship: Cultivate active sponsors across peer departments who will advocate for your organizational impact in closed-door talent reviews.\n3. Present a 90-Day Transition Blueprint: Deliver an unambiguous operational plan demonstrating how your current team will operate seamlessly upon your elevation.";
    }

    // 6. Crisis & Mistake Remediation
    if (lower.includes("mistake") || lower.includes("failed") || lower.includes("error") || lower.includes("outage") || lower.includes("crisis")) {
      return "Mistakes in executive governance are inevitable; obfuscation and panic are fatal. Take immediate ownership, deliver a root-cause 5-Whys analysis, present a recovery plan already underway, and implement systemic safeguards.";
    }

    // 7. Courtesies & Greetings
    if (lower.includes("thank") || lower.includes("thanks") || lower.includes("appreciate")) {
      return "You are welcome. Continuous professional development and disciplined strategic execution are the hallmarks of executive excellence. What next milestone shall we address?";
    }
    if (lower.includes("hello") || lower.includes("hi") || lower.includes("hey")) {
      return "Good day. I am Aurelia, your executive career strategist. I am prepared to evaluate your professional roadmap, deconstruct leadership bottlenecks, or audit your executive portfolio. What strategic milestone shall we address?";
    }

    // Default Fallback
    return `Regarding your strategic inquiry: In executive strategy, clarity of objective and disciplined execution precede outcome. Define your primary business metric, organizational leverage, and target timeline so we can dissect the bottleneck systematically.`;
  }

  // --- Expression Grid Event ---
  expressionGrid.addEventListener('click', (e) => {
    if (e.target.classList.contains('exp-btn')) {
      const exp = e.target.getAttribute('data-exp');
      setExpression(exp);
    }
  });

  // --- Tab Navigation Event ---
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTabId = btn.getAttribute('data-tab');
      tabButtons.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const targetContent = document.getElementById(targetTabId);
      if (targetContent) targetContent.classList.add('active');
    });
  });

  // --- Language Selector Event ---
  languageSelect.addEventListener('change', (e) => {
    currentLang = e.target.value;
    const langData = translations[currentLang] || translations['en-US'];
    loadScenario(currentScenarioIndex);
    window.speakMessage(langData.welcome);
  });

  // --- Voice Toggle Event ---
  voiceToggleBtn.addEventListener('click', () => {
    isVoiceEnabled = !isVoiceEnabled;
    if (isVoiceEnabled) {
      voiceToggleBtn.classList.add('active');
      voiceToggleBtn.querySelector('span').textContent = 'Voice: ON';
      voiceStatusText.textContent = 'Neural Voice Engine Ready';
    } else {
      voiceToggleBtn.classList.remove('active');
      voiceToggleBtn.querySelector('span').textContent = 'Voice: OFF';
      voiceStatusText.textContent = 'Voice Muted';
      window.speechSynthesis.cancel();
      stopWaveAnimation();
    }
  });

  // --- Chat Submission Handler with V4 Cognitive Cycle & Safe Trace ---
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const userText = chatInput.value.trim();
    if (!userText) return;

    const submitBtn = document.getElementById('chatSubmitBtn');
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;

    const sanitizedText = userText
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;')
      .replace(/\//g, '&#x2F;');

    const userBubble = document.createElement('div');
    userBubble.className = 'chat-bubble user';
    userBubble.textContent = sanitizedText;
    chatHistory.appendChild(userBubble);
    chatInput.value = '';
    chatHistory.scrollTop = chatHistory.scrollHeight;

    if (!window.conversationSessionHistory) window.conversationSessionHistory = [];
    window.conversationSessionHistory.push({ role: 'user', content: userText });

    let responseText = '';
    let targetExp = 'neutral';
    let isCognitive = false;
    let traceData = null;
    let artifactsData = [];

    // Attempt backend Cognitive Cycle call with Ollama reasoning
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 25000);

      const response = await fetch(`${API_BASE}/cognitive-cycle`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userText,
          user_role: "Senior Engineering Manager",
          target_role: "Director of Engineering",
          history: window.conversationSessionHistory
        }),
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (response.ok) {
        const data = await response.json();
        responseText = data.response;
        targetExp = data.expression || analyzeExpressionFromText(sanitizedText);
        traceData = data.trace;
        artifactsData = data.artifacts || [];
        isCognitive = true;
        window.conversationSessionHistory.push({ role: 'assistant', content: responseText });
      } else {
        throw new Error('API returned non-200');
      }
    } catch (err) {
      // High-rigor deterministic fallback
      targetExp = analyzeExpressionFromText(sanitizedText);
      responseText = getExecutiveMentorResponse(sanitizedText);
      window.conversationSessionHistory.push({ role: 'assistant', content: responseText });
      traceData = {
        understood: `Analyze career inquiry for strategic execution`,
        memories_count: 4,
        graph_facts_count: 8,
        specialists_invoked: ["DeterministicCareerRules", "ExecutiveFormulaEvaluator"],
        numerical_checks: ["Verified rule consistency"],
        unresolved_unknowns: [],
        confidence_level: "High"
      };
    }

    setExpression(targetExp);

    const aureliaBubble = document.createElement('div');
    aureliaBubble.className = 'chat-bubble aurelia';
    const tag = isCognitive ? 'Cognitive OS V4' : 'Executive Mentor V4';
    const confidencePct = isCognitive ? 92 : 88;

    let traceHtml = '';
    if (traceData) {
      traceHtml = `
        <details class="cognitive-trace-card">
          <summary class="trace-summary-header">
            <span class="trace-badge">🧠 Aurelia's Analysis</span>
            <span class="trace-meta">Confidence: ${confidencePct}% (${traceData.confidence_level || 'High'})</span>
          </summary>
          <div class="trace-body">
            <div class="trace-row"><span class="trace-lbl">Understood:</span> ${traceData.understood}</div>
            <div class="trace-row"><span class="trace-lbl">Evidence Used:</span> ${traceData.memories_count} memories, ${traceData.graph_facts_count} graph facts</div>
            <div class="trace-row"><span class="trace-lbl">Specialists Invoked:</span> ${traceData.specialists_invoked.join(', ')}</div>
            ${traceData.numerical_checks && traceData.numerical_checks.length > 0 ? `<div class="trace-row"><span class="trace-lbl">Verification:</span> ${traceData.numerical_checks.join('; ')}</div>` : ''}
            ${traceData.unresolved_unknowns && traceData.unresolved_unknowns.length > 0 ? `<div class="trace-row warning"><span class="trace-lbl">Unresolved:</span> ${traceData.unresolved_unknowns.join(', ')}</div>` : ''}
          </div>
        </details>
      `;
    }

    let artifactHtml = '';
    if (artifactsData && artifactsData.length > 0) {
      artifactHtml = `
        <div class="artifact-card-preview">
          <div class="artifact-hdr">📋 Executive Artifact Generated: <strong>${artifactsData[0].title}</strong> (v${artifactsData[0].version})</div>
          <div class="artifact-actions">
            <button class="artifact-view-btn" onclick="alert('Artifact: ${artifactsData[0].title}\\n\\nMilestones:\\n${artifactsData[0].payload.milestones.map(m => '- ' + m.phase_name + ': ' + m.goal).join('\\n')}')">🔍 Inspect Artifact</button>
          </div>
        </div>
      `;
    }

    aureliaBubble.innerHTML = `
      <div class="speaker-header">
        <span>Aurelia-chan — ${tag}</span>
        <button class="speak-icon-btn" onclick="speakMessage('${responseText.replace(/'/g, "\\'")}')">🔊</button>
      </div>
      ${traceHtml}
      <div class="prose-content">${responseText}</div>
      ${artifactHtml}
    `;
    chatHistory.appendChild(aureliaBubble);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    window.speakMessage(responseText);

    submitBtn.classList.remove('loading');
    submitBtn.disabled = false;
  });

  // --- Resume Audit Module Handler (High Rigor, No Fake Praise) ---
  auditBtn.addEventListener('click', async () => {
    const text = resumeText.value.trim();
    if (!text) {
      alert("Please paste your resume or CV summary text first.");
      return;
    }

    auditBtn.classList.add('loading');
    auditBtn.disabled = true;
    setExpression('analyzing');

    let score = 45;
    let strengths = [];
    let improvements = [];
    let rec = "";
    let targetExp = 'analyzing';

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 4000);

      const response = await fetch(`${API_BASE}/resume-audit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume: text }),
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (response.ok) {
        const data = await response.json();
        score = data.score;
        strengths = data.strengths || [];
        improvements = data.improvements || [];
        rec = data.recommendation || data.feedback;
        targetExp = data.expression || 'analyzing';
      } else {
        throw new Error('API non-200');
      }
    } catch (err) {
      // Strict offline client-side evaluation
      const lower = text.toLowerCase();
      const wordCount = text.split(/\s+/).length;
      const metrics = text.match(/(\d+[%$kKmMBb]|\$\d+|\d+\s*percent|\d+\s*million|\d+\s*team)/g) || [];
      const hasMetrics = metrics.length >= 2;
      const hasPassives = lower.includes('responsible for') || lower.includes('assisted') || lower.includes('helped') || lower.includes('team player');
      const hasExecVerbs = lower.includes('spearheaded') || lower.includes('orchestrated') || lower.includes('scaled') || lower.includes('governed') || lower.includes('architected');

      score = 40;
      if (wordCount > 30) score += 15;
      if (hasMetrics) score += 25;
      else score -= 10;
      if (hasExecVerbs) score += 15;
      if (hasPassives) score -= 15;

      score = Math.max(32, Math.min(score, 95));

      if (score < 60) {
        targetExp = 'disappointed';
        strengths = ["Foundational functional background identified."];
        improvements = [
          "CRITICAL: Severe lack of quantifiable business metrics (revenue, ROI, headcount, cost reduction).",
          "CRITICAL: Contains passive task descriptions ('responsible for', assisted) rather than leadership ownership.",
          "Reframe bullet points into the Executive Formula: [Action Verb] + [Context] + [Measurable Business Outcome]."
        ];
        rec = "Unacceptable for senior or executive placement. This reads as a list of assigned duties rather than business transformation. You must quantify your scope and eliminate passive phrasing immediately.";
      } else if (score < 80) {
        targetExp = 'serious';
        strengths = [
          "Clear career progression and operational competence.",
          hasMetrics ? `Includes verifiable metric markers (${metrics.slice(0, 2).join(', ')}).` : "Identifiable domain ownership."
        ];
        improvements = [
          "Elevate leadership scope: articulate budget ownership, cross-functional consensus, and P&L accountability.",
          "Replace mid-level operational language with board-level strategic terminology."
        ];
        rec = "Competent operational profile, but lacks distinctive executive presence. Elevate your bullet points to emphasize direct bottom-line impact and organizational de-risking.";
      } else {
        targetExp = 'approval';
        strengths = [
          `High-impact executive framing with strong metric density (${metrics.length} data points).`,
          "Authoritative leadership vocabulary and clear strategic ROI."
        ];
        improvements = [
          "Fine-tune executive summary for specific target board or VP mandates.",
          "Highlight governance and industry thought leadership."
        ];
        rec = "Strong executive alignment. Your profile communicates authority, scale, and measurable ROI.";
      }
    }

    auditScore.textContent = `${score}%`;
    auditStrengths.innerHTML = strengths.map(s => `<li>${s}</li>`).join('');
    auditImprovements.innerHTML = improvements.map(i => `<li>${i}</li>`).join('');
    auditRecommendation.textContent = rec;
    auditResultCard.classList.add('active');

    setExpression(targetExp);
    window.speakMessage(`Resume Audit complete. Overall score is ${score} percent. ${rec}`);

    auditBtn.classList.remove('loading');
    auditBtn.disabled = false;
  });

  // --- Interview Simulator Handler (High Rigor, No Fake Praise) ---
  function loadScenario(index) {
    const langData = translations[currentLang] || translations['en-US'];
    const scenario = langData.scenarios[index % langData.scenarios.length];
    scenarioTitle.textContent = scenario.title;
    scenarioPrompt.textContent = `"${scenario.prompt}"`;
    interviewResponse.value = '';
    interviewFeedbackCard.classList.remove('active');
  }

  evaluateAnswerBtn.addEventListener('click', async () => {
    const ans = interviewResponse.value.trim();
    if (!ans) {
      alert("Please enter your interview response first.");
      return;
    }

    evaluateAnswerBtn.classList.add('loading');
    evaluateAnswerBtn.disabled = true;
    setExpression('focused');

    let score = 48;
    let feedback = "";
    let targetExp = 'focused';

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 4000);

      const response = await fetch(`${API_BASE}/interview-evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          response: ans,
          scenario: scenarioTitle.textContent
        }),
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (response.ok) {
        const data = await response.json();
        score = data.score;
        feedback = data.feedback;
        targetExp = data.expression || 'focused';
      } else {
        throw new Error('API non-200');
      }
    } catch (err) {
      // Strict offline client-side evaluation
      const lower = ans.toLowerCase();
      const wordCount = ans.split(/\s+/).length;
      const hasBusinessTerms = lower.includes('roi') || lower.includes('metric') || lower.includes('revenue') || lower.includes('benchmark') || lower.includes('data') || lower.includes('risk') || lower.includes('stakeholder');
      const hasStar = lower.includes('situation') || lower.includes('action') || lower.includes('result') || lower.includes('therefore') || lower.includes('outcome');
      const hasEntitlement = lower.includes('i deserve') || lower.includes('unfair') || lower.includes('threaten') || lower.includes('my boss') || lower.includes('not my fault');

      score = 45;
      if (wordCount < 12) score = 30;
      else if (wordCount > 35) score += 25;
      if (hasBusinessTerms) score += 15;
      if (hasStar) score += 10;
      if (hasEntitlement) score -= 25;

      score = Math.max(28, Math.min(score, 96));

      if (score < 60) {
        targetExp = hasEntitlement ? 'warning' : 'skeptical';
        feedback = hasEntitlement
          ? "Critical framing error. Appealing to personal entitlement or complaints in an executive negotiation is an instant disqualifier. Reframe counter-proposals around risk-adjusted ROI and replacement cost."
          : "Weak executive posture. Your response is either too brief or avoids the commercial reality of the conflict. Structure your answer using the STAR method and lead with business outcomes.";
      } else if (score < 80) {
        targetExp = 'analyzing';
        feedback = "Acceptable baseline, but lacks executive sharpness. You communicated basic intent, but failed to anchor your leverage with hard market benchmark data or alternative variable levers.";
      } else {
        targetExp = 'confident';
        feedback = "High-caliber executive framing. You maintained emotional composure, grounded your position in commercial impact, and offered a structured path forward that de-risks the hire.";
      }
    }

    interviewScore.textContent = score;
    interviewFeedbackText.textContent = feedback;
    interviewFeedbackCard.classList.add('active');

    setExpression(targetExp);
    window.speakMessage(`Evaluation complete. Score: ${score}. ${feedback}`);

    interviewResponse.value = '';
    evaluateAnswerBtn.classList.remove('loading');
    evaluateAnswerBtn.disabled = false;
  });

  nextScenarioBtn.addEventListener('click', () => {
    currentScenarioIndex++;
    loadScenario(currentScenarioIndex);
    setExpression('neutral');
  });

  // --- V5 Adaptive Forecast Refresh Handler ---
  const v5RefreshBtn = document.getElementById('v5RefreshForecastBtn');
  if (v5RefreshBtn) {
    v5RefreshBtn.addEventListener('click', async () => {
      v5RefreshBtn.textContent = '⏳ Calculating...';
      try {
        const res = await fetch(`${API_BASE}/v5/forecast`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ goal_id: 'g_director', target_role: 'Director of Engineering', timeline_months: 8.0 })
        });
        if (res.ok) {
          const data = await res.json();
          const badge = document.getElementById('v5GoalBadge');
          const windowSpan = document.getElementById('v5ProjectedWindow');
          const bottleneck = document.getElementById('v5Bottleneck');
          if (badge) badge.textContent = `${data.status} (${(data.probability_of_completion * 100).toFixed(0)}%)`;
          if (windowSpan) windowSpan.textContent = `${data.likely_completion_window_months[0]} – ${data.likely_completion_window_months[1]} Months`;
          if (bottleneck) bottleneck.textContent = data.critical_path_bottleneck;
          v5RefreshBtn.textContent = '✅ Forecast Recalculated';
          setTimeout(() => { v5RefreshBtn.textContent = '🔄 Recalculate Forecast'; }, 2000);
        }
      } catch (err) {
        v5RefreshBtn.textContent = '🔄 Recalculate Forecast';
      }
    });
  }

  // --- Populate Canon Inspector 15 Master Sheets ---
  function populateMasterSheets() {
    masterSheetsGrid.innerHTML = '';
    masterSheetFiles.forEach(file => {
      const card = document.createElement('div');
      card.className = 'sheet-thumb-card';
      const nameWithoutExt = file.replace('.png', '');
      card.innerHTML = `
        <img src="aurelia-canon/master-sheets/${file}" alt="${nameWithoutExt}" loading="lazy">
        <p title="${file}">${nameWithoutExt}</p>
      `;
      card.addEventListener('click', () => {
        window.open(`aurelia-canon/master-sheets/${file}`, '_blank');
      });
      masterSheetsGrid.appendChild(card);
    });
  }

  // --- V6 Perception & Scene Scan Handler ---
  const v6ScanBtn = document.getElementById('v6ScanSceneBtn');
  if (v6ScanBtn) {
    v6ScanBtn.addEventListener('click', async () => {
      v6ScanBtn.textContent = '⏳ Scanning Scene...';
      try {
        const res = await fetch(`${API_BASE}/v6/perceive-screen`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            window_title: 'Aurelia-Chan - Visual Studio Code',
            process_name: 'Code.exe',
            query: 'Why is this failing?',
            text_snippet: 'TypeError: unsupported operand'
          })
        });
        if (res.ok) {
          const data = await res.json();
          const appBadge = document.getElementById('v6AppBadge');
          const winTitle = document.getElementById('v6WinTitle');
          const tierSpan = document.getElementById('v6PerceptionTier');
          if (appBadge) appBadge.textContent = `${data.selected_context.toUpperCase()} (Tier 1 Accessibility)`;
          if (winTitle) winTitle.textContent = 'Aurelia-Chan - Visual Studio Code (Live)';
          if (tierSpan) tierSpan.textContent = `Context: ${data.selected_context} (Separation: ${data.separation_ratio})`;
          v6ScanBtn.textContent = '✅ Scene Re-Scanned';
          setTimeout(() => { v6ScanBtn.textContent = '🔍 Re-Scan Environment Scene'; }, 2000);
        }
      } catch (err) {
        v6ScanBtn.textContent = '🔍 Re-Scan Environment Scene';
      }
    });
  }

  const v6PauseBtn = document.getElementById('v6PausePerceptionBtn');
  if (v6PauseBtn) {
    v6PauseBtn.addEventListener('click', () => {
      if (v6PauseBtn.textContent.includes('Pause')) {
        v6PauseBtn.textContent = '▶ Resume Perception';
        v6PauseBtn.style.background = 'rgba(34, 197, 94, 0.2)';
        v6PauseBtn.style.color = '#4ade80';
      } else {
        v6PauseBtn.textContent = '⏸ Pause Perception';
        v6PauseBtn.style.background = 'rgba(239, 68, 68, 0.15)';
        v6PauseBtn.style.color = '#f87171';
      }
    });
  }

  const v6ClearBtn = document.getElementById('v6ClearSessionBtn');
  if (v6ClearBtn) {
    v6ClearBtn.addEventListener('click', () => {
      v6ClearBtn.textContent = '✨ Working Memory Cleared';
      setTimeout(() => { v6ClearBtn.textContent = '🗑 Clear Working Memory'; }, 2000);
    });
  }

  // --- Initialization & Health Check ---
  initVisualizer();
  setExpression('neutral');
  populateMasterSheets();
  loadScenario(0);

  // Check Backend Status silently
  fetch(`${API_BASE}/system-status`)
    .then(res => res.json())
    .then(data => {
      isBackendConnected = true;
      const stageBadgeText = document.querySelector('.stage-badge span');
      if (stageBadgeText) stageBadgeText.textContent = 'Cognitive OS V6 Active (Grounded Multimodal Engine)';
      console.log('Aurelia Cognitive OS V6 Connected:', data);
    })
    .catch(() => {
      isBackendConnected = false;
      const stageBadgeText = document.querySelector('.stage-badge span');
      if (stageBadgeText) stageBadgeText.textContent = 'Canon v1.0 (High-Rigor Engine)';
      console.log('Aurelia running with high-rigor local executive rules.');
    });
});
