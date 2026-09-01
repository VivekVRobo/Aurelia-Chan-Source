/* Integrity overlay for the existing Aurelia UI.
 *
 * This file removes safety-sensitive legacy event handlers before interaction and
 * replaces them with fail-closed API consumers. No synthetic cognition, confidence,
 * trace evidence, resume score, or interview score is generated when the backend is
 * unavailable.
 */
(function installIntegrityOverlay() {
  'use strict';

  const contract = globalThis.AureliaFrontendContract;
  if (!contract) {
    throw new Error('AureliaFrontendContract must load before the integrity overlay');
  }

  const EXPRESSIONS = {
    neutral: ['01. Neutral / Observing', 'Calm executive evaluation and structured focus.'],
    confident: ['02. Subtle Confident Smile', 'Refined assurance in strategic direction.'],
    approval: ['03. Soft Approval', 'Restrained praise for high-value achievements.'],
    focused: ['04. Focused Listening', 'Deep analytical attention to career details.'],
    analyzing: ['05. Analyzing (Raised Brow)', 'Critical inspection of plans or resume metrics.'],
    serious: ['06. Serious', 'Uncompromising clarity on high-stakes decisions.'],
    warning: ['07. Strict Warning', 'Firm correction against strategic mistakes.'],
    disappointed: ['08. Disappointed', 'Measured disappointment in lack of preparation.'],
    skeptical: ['09. Skeptical', 'Questioning unsubstantiated or vague claims.'],
    concerned: ['10. Concerned', 'Strategic empathy for burn-out or toxic environments.'],
    empathetic: ['11. Empathetic', 'Warm executive mentorship during challenging pivots.'],
  };

  function apiBase() {
    const direct = window.location.protocol.startsWith('http')
      && (window.location.port === '5000' || window.location.pathname.includes('/api'));
    return direct ? '/api' : 'http://localhost:5000/api';
  }

  function cloneWithoutListeners(element) {
    if (!element) return null;
    const clone = element.cloneNode(true);
    element.replaceWith(clone);
    return clone;
  }

  function setExpression(expression) {
    const safeExpression = contract.VALID_EXPRESSIONS.has(expression) ? expression : 'neutral';
    document.querySelectorAll('.avatar-img').forEach(image => {
      image.classList.toggle('active', image.getAttribute('data-expression') === safeExpression);
    });
    document.querySelectorAll('.exp-btn').forEach(button => {
      button.classList.toggle('active', button.getAttribute('data-exp') === safeExpression);
    });
    const [title, subtitle] = EXPRESSIONS[safeExpression];
    const titleNode = document.getElementById('expTitle');
    const subtitleNode = document.getElementById('expSubtitle');
    if (titleNode) titleNode.textContent = title;
    if (subtitleNode) subtitleNode.textContent = subtitle;
  }

  function appendTextElement(parent, tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    node.textContent = text;
    parent.appendChild(node);
    return node;
  }

  function appendUserBubble(history, text) {
    appendTextElement(history, 'div', 'chat-bubble user', text);
    history.scrollTop = history.scrollHeight;
  }

  function appendUnavailableBubble(history, message) {
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble aurelia unavailable';
    appendTextElement(bubble, 'div', 'speaker-header', 'Aurelia-chan — Cognitive service unavailable');
    appendTextElement(bubble, 'div', 'prose-content', message);
    history.appendChild(bubble);
    history.scrollTop = history.scrollHeight;
  }

  function traceRow(parent, label, value, warning = false) {
    const row = document.createElement('div');
    row.className = warning ? 'trace-row warning' : 'trace-row';
    appendTextElement(row, 'span', 'trace-lbl', `${label}: `);
    row.appendChild(document.createTextNode(value));
    parent.appendChild(row);
  }

  function appendVerifiedBubble(history, result) {
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble aurelia';

    const header = document.createElement('div');
    header.className = 'speaker-header';
    appendTextElement(header, 'span', '', 'Aurelia-chan — Verified Cognitive Runtime');
    const speak = appendTextElement(header, 'button', 'speak-icon-btn', '🔊');
    speak.type = 'button';
    speak.addEventListener('click', () => window.speakMessage?.(result.response));
    bubble.appendChild(header);

    const details = document.createElement('details');
    details.className = 'cognitive-trace-card';
    const summary = document.createElement('summary');
    summary.className = 'trace-summary-header';
    appendTextElement(summary, 'span', 'trace-badge', '🧠 Aurelia Analysis');
    appendTextElement(
      summary,
      'span',
      'trace-meta',
      `Confidence: ${result.confidence}% (${result.trace.confidenceLevel})`,
    );
    details.appendChild(summary);

    const traceBody = document.createElement('div');
    traceBody.className = 'trace-body';
    traceRow(traceBody, 'Understood', result.trace.understood);
    traceRow(
      traceBody,
      'Evidence Used',
      `${result.trace.memoriesCount} memories, ${result.trace.graphFactsCount} graph facts`,
    );
    traceRow(
      traceBody,
      'Specialists Invoked',
      result.trace.specialistsInvoked.length > 0
        ? result.trace.specialistsInvoked.join(', ')
        : 'None reported',
    );
    if (result.trace.numericalChecks.length > 0) {
      traceRow(traceBody, 'Verification', result.trace.numericalChecks.join('; '));
    }
    if (result.trace.unresolvedUnknowns.length > 0) {
      traceRow(traceBody, 'Unresolved', result.trace.unresolvedUnknowns.join(', '), true);
    }
    details.appendChild(traceBody);
    bubble.appendChild(details);

    appendTextElement(bubble, 'div', 'prose-content', result.response);

    for (const artifact of result.artifacts) {
      const card = document.createElement('div');
      card.className = 'artifact-card-preview';
      appendTextElement(
        card,
        'div',
        'artifact-hdr',
        `📋 ${artifact.title} — ${artifact.type} (v${String(artifact.version)})`,
      );
      bubble.appendChild(card);
    }

    history.appendChild(bubble);
    history.scrollTop = history.scrollHeight;
  }

  async function fetchJson(url, options, timeoutMs) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(url, { ...options, signal: controller.signal });
      let body = null;
      try {
        body = await response.json();
      } catch (_error) {
        throw new contract.FrontendContractError('server returned non-JSON response');
      }
      if (!response.ok) {
        const detail = body && typeof body.error === 'string' ? body.error : `HTTP ${response.status}`;
        throw new contract.FrontendContractError(`server rejected request: ${detail}`, 'server_rejected');
      }
      return body;
    } finally {
      clearTimeout(timeout);
    }
  }

  function setBusy(button, busy) {
    if (!button) return;
    button.disabled = busy;
    button.classList.toggle('loading', busy);
  }

  function installStrictChat() {
    const form = cloneWithoutListeners(document.getElementById('chatForm'));
    if (!form) return;
    const input = form.querySelector('#chatInput');
    const submit = form.querySelector('#chatSubmitBtn');
    const history = document.getElementById('chatHistory');
    if (!input || !submit || !history) return;

    if (!Array.isArray(window.conversationSessionHistory)) {
      window.conversationSessionHistory = [];
    }

    form.addEventListener('submit', async event => {
      event.preventDefault();
      const userText = input.value.trim();
      if (!userText || submit.disabled) return;

      appendUserBubble(history, userText);
      input.value = '';
      window.conversationSessionHistory.push({ role: 'user', content: userText });
      setBusy(submit, true);

      try {
        const raw = await fetchJson(
          `${apiBase()}/cognitive-cycle`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              message: userText,
              user_role: 'Senior Engineering Manager',
              target_role: 'Director of Engineering',
              history: window.conversationSessionHistory,
            }),
          },
          25000,
        );
        const result = contract.normalizeCognitiveCycle(raw);
        window.conversationSessionHistory.push({ role: 'assistant', content: result.response });
        setExpression(result.expression);
        appendVerifiedBubble(history, result);
        window.speakMessage?.(result.response);
      } catch (error) {
        console.error('Aurelia cognitive request failed closed:', error);
        setExpression('neutral');
        appendUnavailableBubble(
          history,
          'Aurelia cognitive service is unavailable. No fallback response, confidence, or evidence was generated.',
        );
      } finally {
        setBusy(submit, false);
      }
    });
  }

  function renderAuditUnavailable(card, score, strengths, improvements, recommendation) {
    if (score) score.textContent = '—';
    if (strengths) strengths.replaceChildren();
    if (improvements) {
      improvements.replaceChildren();
      appendTextElement(
        improvements,
        'li',
        '',
        'Audit unavailable. No local heuristic score was generated.',
      );
    }
    if (recommendation) recommendation.textContent = 'Connect the verified Aurelia runtime and retry.';
    card?.classList.add('active');
  }

  function installStrictResumeAudit() {
    const button = cloneWithoutListeners(document.getElementById('auditBtn'));
    const textArea = document.getElementById('resumeText');
    const card = document.getElementById('auditResultCard');
    const scoreNode = document.getElementById('auditScore');
    const strengthsNode = document.getElementById('auditStrengths');
    const improvementsNode = document.getElementById('auditImprovements');
    const recommendationNode = document.getElementById('auditRecommendation');
    if (!button || !textArea) return;

    button.addEventListener('click', async () => {
      const text = textArea.value.trim();
      if (!text || button.disabled) return;
      setBusy(button, true);
      setExpression('analyzing');
      try {
        const data = await fetchJson(
          `${apiBase()}/resume-audit`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ resume: text }),
          },
          10000,
        );
        if (typeof data.score !== 'number' || !Number.isFinite(data.score) || data.score < 0 || data.score > 100) {
          throw new contract.FrontendContractError('resume score must be a finite percentage');
        }
        const strengths = Array.isArray(data.strengths) && data.strengths.every(item => typeof item === 'string')
          ? data.strengths
          : [];
        const improvements = Array.isArray(data.improvements) && data.improvements.every(item => typeof item === 'string')
          ? data.improvements
          : [];
        const recommendation = typeof data.recommendation === 'string'
          ? data.recommendation
          : typeof data.feedback === 'string' ? data.feedback : '';
        if (!recommendation) {
          throw new contract.FrontendContractError('resume recommendation is missing');
        }
        if (scoreNode) scoreNode.textContent = `${data.score}%`;
        strengthsNode?.replaceChildren(...strengths.map(item => {
          const li = document.createElement('li');
          li.textContent = item;
          return li;
        }));
        improvementsNode?.replaceChildren(...improvements.map(item => {
          const li = document.createElement('li');
          li.textContent = item;
          return li;
        }));
        if (recommendationNode) recommendationNode.textContent = recommendation;
        card?.classList.add('active');
        const expression = contract.VALID_EXPRESSIONS.has(data.expression) ? data.expression : 'analyzing';
        setExpression(expression);
      } catch (error) {
        console.error('Aurelia resume audit failed closed:', error);
        setExpression('neutral');
        renderAuditUnavailable(card, scoreNode, strengthsNode, improvementsNode, recommendationNode);
      } finally {
        setBusy(button, false);
      }
    });
  }

  function installStrictInterviewEvaluation() {
    const button = cloneWithoutListeners(document.getElementById('evaluateAnswerBtn'));
    const input = document.getElementById('interviewResponse');
    const card = document.getElementById('interviewFeedbackCard');
    const scoreNode = document.getElementById('interviewScore');
    const feedbackNode = document.getElementById('interviewFeedbackText');
    if (!button || !input) return;

    button.addEventListener('click', async () => {
      const answer = input.value.trim();
      if (!answer || button.disabled) return;
      setBusy(button, true);
      setExpression('focused');
      try {
        const data = await fetchJson(
          `${apiBase()}/interview-evaluate`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answer }),
          },
          10000,
        );
        if (typeof data.score !== 'number' || !Number.isFinite(data.score) || data.score < 0 || data.score > 100) {
          throw new contract.FrontendContractError('interview score must be a finite percentage');
        }
        if (typeof data.feedback !== 'string' || data.feedback.trim() === '') {
          throw new contract.FrontendContractError('interview feedback is missing');
        }
        if (scoreNode) scoreNode.textContent = String(data.score);
        if (feedbackNode) feedbackNode.textContent = data.feedback;
        card?.classList.add('active');
        const expression = contract.VALID_EXPRESSIONS.has(data.expression) ? data.expression : 'focused';
        setExpression(expression);
      } catch (error) {
        console.error('Aurelia interview evaluation failed closed:', error);
        if (scoreNode) scoreNode.textContent = '—';
        if (feedbackNode) {
          feedbackNode.textContent = 'Evaluation unavailable. No local heuristic score was generated.';
        }
        card?.classList.add('active');
        setExpression('neutral');
      } finally {
        setBusy(button, false);
      }
    });
  }

  function neutralizeUnmeasuredDashboardClaims() {
    document.querySelectorAll('.v5-metric-box .v5-box-val').forEach(node => {
      node.textContent = 'Not measured';
    });
    const projected = document.getElementById('v5ProjectedWindow');
    const bottleneck = document.getElementById('v5Bottleneck');
    const goalBadge = document.getElementById('v5GoalBadge');
    const blockers = document.getElementById('v5BlockersList');
    if (projected) projected.textContent = 'Not measured';
    if (bottleneck) bottleneck.textContent = 'Not measured';
    if (goalBadge) goalBadge.textContent = 'Awaiting forecast';
    if (blockers) {
      blockers.replaceChildren();
      appendTextElement(blockers, 'li', '', 'Run Recalculate Forecast to load runtime-derived data.');
    }

    const v6App = document.getElementById('v6AppBadge');
    const v6Window = document.getElementById('v6WinTitle');
    const v6Tier = document.getElementById('v6PerceptionTier');
    if (v6App) v6App.textContent = 'No live scene captured';
    if (v6Window) v6Window.textContent = 'Not measured';
    if (v6Tier) v6Tier.textContent = 'Not measured';
  }

  function installAuthoritativeRuntimeBadge() {
    const badge = document.querySelector('.stage-badge span');
    if (!badge) return;
    let authoritativeText = 'Checking cognitive runtime…';
    badge.textContent = authoritativeText;
    const observer = new MutationObserver(() => {
      if (badge.textContent !== authoritativeText) badge.textContent = authoritativeText;
    });
    observer.observe(badge, { childList: true, characterData: true, subtree: true });

    fetchJson(`${apiBase()}/runtime-status`, { method: 'GET' }, 5000)
      .then(data => {
        if (data.runtime_configured !== true || data.persona_renderer !== true) {
          throw new contract.FrontendContractError('runtime status is not fully configured');
        }
        authoritativeText = data.persistence?.durable === true
          ? 'Cognitive runtime verified — durable persistence'
          : 'Cognitive runtime verified — non-durable session';
        badge.textContent = authoritativeText;
      })
      .catch(error => {
        console.error('Aurelia runtime status unavailable:', error);
        authoritativeText = 'Cognitive runtime unavailable — UI only';
        badge.textContent = authoritativeText;
      });
  }

  document.addEventListener('DOMContentLoaded', () => {
    installStrictChat();
    installStrictResumeAudit();
    installStrictInterviewEvaluation();
    neutralizeUnmeasuredDashboardClaims();
    installAuthoritativeRuntimeBadge();
  });
})();
