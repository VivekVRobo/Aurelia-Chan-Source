const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');

function source(path) {
  return fs.readFileSync(path, 'utf8');
}

test('active bootstrap installs contract and integrity overlay around legacy UI', () => {
  const bootstrap = source('app.js');
  const contractIndex = bootstrap.indexOf('frontend/cognitive_contract.js');
  const legacyIndex = bootstrap.indexOf('app_legacy.js');
  const patchIndex = bootstrap.indexOf('frontend/integrity_patch.js');

  assert.ok(contractIndex >= 0, 'active bootstrap must install cognitive contract');
  assert.ok(legacyIndex > contractIndex, 'legacy UI must load after the cognitive contract');
  assert.ok(patchIndex > legacyIndex, 'integrity overlay must load after legacy UI registration');
});

test('active interaction layer contains no fabricated cognitive evidence or confidence constants', () => {
  const bootstrap = source('app.js');
  const patch = source('frontend/integrity_patch.js');
  const active = `${bootstrap}\n${patch}`;

  for (const forbidden of [
    'memories_count: 4',
    'graph_facts_count: 8',
    'Confidence: 92',
    'Confidence: 88',
    'DeterministicCareerRules',
    'ExecutiveFormulaEvaluator',
  ]) {
    assert.equal(active.includes(forbidden), false, `active frontend must not contain ${forbidden}`);
  }

  assert.match(active, /No fallback response, confidence, or evidence was generated/);
  assert.match(active, /No local heuristic score was generated/);
});

test('unmeasured dashboard claims are neutralized before user interaction', () => {
  const patch = source('frontend/integrity_patch.js');
  assert.match(patch, /v5-metric-box \.v5-box-val/);
  assert.match(patch, /Not measured/);
  assert.match(patch, /Awaiting forecast/);
  assert.match(patch, /No live scene captured/);
});

test('strict chat, resume, and interview handlers replace legacy listeners', () => {
  const patch = source('frontend/integrity_patch.js');
  assert.match(patch, /cloneWithoutListeners\(document\.getElementById\('chatForm'\)\)/);
  assert.match(patch, /cloneWithoutListeners\(document\.getElementById\('auditBtn'\)\)/);
  assert.match(patch, /cloneWithoutListeners\(document\.getElementById\('evaluateAnswerBtn'\)\)/);
});
