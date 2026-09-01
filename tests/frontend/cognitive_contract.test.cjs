const test = require('node:test');
const assert = require('node:assert/strict');

const contract = require('../../frontend/cognitive_contract.js');

function validCycle() {
  return {
    response: 'Use verified market evidence and define your walk-away constraints.',
    expression: 'confident',
    portrait: 'aurelia-expressions/02-subtle-confident-smile.png',
    confidence: 87,
    persona: {
      emotion: 'neutral',
      emotion_intensity: 'low',
      expression_style: 'direct',
      mode: 'executive',
      traits: ['precise'],
      expression: 'confident',
      portrait: 'aurelia-expressions/02-subtle-confident-smile.png',
    },
    character_response: {
      schema_version: 'rci.character_response.v1',
      interaction_id: 'interaction-1',
      decision_id: 'decision-1',
      source_character: 'aurelia',
      speech: {
        text: 'Use verified market evidence and define your walk-away constraints.',
        delivery: 'confident',
        interruptible: true,
      },
      expression: { expression: 'confident', strength: 'subtle' },
      motion: { cue: 'present', style: 'restrained', disposition: 'optional' },
      verified: true,
      persistence_committed: true,
      persistence_durable: true,
    },
    trace: {
      understood: 'Prepare a grounded negotiation strategy',
      memories_count: 0,
      graph_facts_count: 0,
      specialists_invoked: [],
      alternatives_evaluated: [],
      numerical_checks: [],
      unresolved_unknowns: ['market band not provided'],
      confidence_level: 'High',
    },
    verification: {
      passed: true,
      severity: 'info',
      safe_to_publish: true,
      issues: [],
    },
    persistence: {
      committed: true,
      durable: true,
      approved_memory_ids: [],
      rejected_memory: [],
    },
    artifacts: [],
    decision_id: 'decision-1',
  };
}

test('accepts a verified committed cycle with truthful zero evidence counts', () => {
  const result = contract.normalizeCognitiveCycle(validCycle());
  assert.equal(result.status, 'verified');
  assert.equal(result.confidence, 87);
  assert.equal(result.trace.memoriesCount, 0);
  assert.equal(result.trace.graphFactsCount, 0);
  assert.equal(result.expression, 'confident');
});

test('rejects a response that verification did not approve for publication', () => {
  const cycle = validCycle();
  cycle.verification.safe_to_publish = false;
  assert.throws(
    () => contract.normalizeCognitiveCycle(cycle),
    error => error instanceof contract.FrontendContractError && error.code === 'not_publishable',
  );
});

test('rejects a response that was not committed by the runtime', () => {
  const cycle = validCycle();
  cycle.persistence.committed = false;
  assert.throws(() => contract.normalizeCognitiveCycle(cycle), /persistence\.committed must be true/);
});

test('rejects a CharacterResponse whose speech diverges from final prose', () => {
  const cycle = validCycle();
  cycle.character_response.speech.text = 'Different text';
  assert.throws(() => contract.normalizeCognitiveCycle(cycle), /speech must match final response/);
});

test('rejects a CharacterResponse whose expression diverges from persona', () => {
  const cycle = validCycle();
  cycle.character_response.expression.expression = 'serious';
  assert.throws(() => contract.normalizeCognitiveCycle(cycle), /expression must match persona expression/);
});

test('rejects fabricated or malformed confidence instead of inventing a replacement', () => {
  const cycle = validCycle();
  cycle.confidence = Number.NaN;
  assert.throws(() => contract.normalizeCognitiveCycle(cycle), /confidence must be a finite percentage/);
});

test('unavailable state contains no confidence, trace, artifacts, or CharacterResponse', () => {
  const result = contract.unavailable('Runtime unavailable');
  assert.equal(result.status, 'unavailable');
  assert.equal(result.confidence, null);
  assert.equal(result.trace, null);
  assert.deepEqual(result.artifacts, []);
  assert.equal(result.characterResponse, null);
});
