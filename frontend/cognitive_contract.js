/* Stable, dependency-free browser contract for Aurelia's canonical cognitive API. */
(function installAureliaFrontendContract(root, factory) {
  const api = factory();
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
  if (root) {
    root.AureliaFrontendContract = api;
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function buildContract() {
  'use strict';

  const CHARACTER_RESPONSE_SCHEMA = 'rci.character_response.v1';
  const VALID_EXPRESSIONS = new Set([
    'neutral',
    'confident',
    'approval',
    'focused',
    'analyzing',
    'serious',
    'warning',
    'disappointed',
    'skeptical',
    'concerned',
    'empathetic',
  ]);

  class FrontendContractError extends Error {
    constructor(message, code = 'invalid_response') {
      super(message);
      this.name = 'FrontendContractError';
      this.code = code;
    }
  }

  function object(value, name) {
    if (!value || typeof value !== 'object' || Array.isArray(value)) {
      throw new FrontendContractError(`${name} must be an object`);
    }
    return value;
  }

  function nonEmptyString(value, name) {
    if (typeof value !== 'string' || value.trim() === '') {
      throw new FrontendContractError(`${name} must be a non-empty string`);
    }
    return value;
  }

  function booleanTrue(value, name) {
    if (value !== true) {
      throw new FrontendContractError(`${name} must be true`, 'not_publishable');
    }
  }

  function finitePercentage(value) {
    if (typeof value !== 'number' || !Number.isFinite(value) || value < 0 || value > 100) {
      throw new FrontendContractError('confidence must be a finite percentage in [0, 100]');
    }
    return value;
  }

  function nonNegativeInteger(value, name) {
    if (!Number.isInteger(value) || value < 0) {
      throw new FrontendContractError(`${name} must be a non-negative integer`);
    }
    return value;
  }

  function stringArray(value, name) {
    if (!Array.isArray(value) || value.some(item => typeof item !== 'string')) {
      throw new FrontendContractError(`${name} must be an array of strings`);
    }
    return [...value];
  }

  function normalizeTrace(value) {
    const trace = object(value, 'trace');
    return Object.freeze({
      understood: nonEmptyString(trace.understood, 'trace.understood'),
      memoriesCount: nonNegativeInteger(trace.memories_count, 'trace.memories_count'),
      graphFactsCount: nonNegativeInteger(trace.graph_facts_count, 'trace.graph_facts_count'),
      specialistsInvoked: stringArray(trace.specialists_invoked, 'trace.specialists_invoked'),
      alternativesEvaluated: stringArray(trace.alternatives_evaluated || [], 'trace.alternatives_evaluated'),
      numericalChecks: stringArray(trace.numerical_checks || [], 'trace.numerical_checks'),
      unresolvedUnknowns: stringArray(trace.unresolved_unknowns || [], 'trace.unresolved_unknowns'),
      confidenceLevel: nonEmptyString(trace.confidence_level, 'trace.confidence_level'),
    });
  }

  function normalizeArtifact(value, index) {
    const artifact = object(value, `artifacts[${index}]`);
    return Object.freeze({
      id: nonEmptyString(artifact.id, `artifacts[${index}].id`),
      type: nonEmptyString(artifact.type, `artifacts[${index}].type`),
      title: nonEmptyString(artifact.title, `artifacts[${index}].title`),
      version: artifact.version,
      payload: artifact.payload && typeof artifact.payload === 'object' ? artifact.payload : {},
    });
  }

  function normalizeCognitiveCycle(value) {
    const data = object(value, 'cognitive response');
    const response = nonEmptyString(data.response, 'response');
    const verification = object(data.verification, 'verification');
    const persistence = object(data.persistence, 'persistence');
    const persona = object(data.persona, 'persona');
    const character = object(data.character_response, 'character_response');
    const speech = object(character.speech, 'character_response.speech');
    const characterExpression = object(character.expression, 'character_response.expression');

    booleanTrue(verification.passed, 'verification.passed');
    booleanTrue(verification.safe_to_publish, 'verification.safe_to_publish');
    booleanTrue(persistence.committed, 'persistence.committed');
    booleanTrue(character.verified, 'character_response.verified');
    booleanTrue(character.persistence_committed, 'character_response.persistence_committed');

    if (character.schema_version !== CHARACTER_RESPONSE_SCHEMA) {
      throw new FrontendContractError('unsupported character_response schema version');
    }
    if (character.source_character !== 'aurelia') {
      throw new FrontendContractError('character_response source must be aurelia');
    }
    if (speech.text !== response) {
      throw new FrontendContractError('character_response speech must match final response');
    }

    const expression = nonEmptyString(persona.expression, 'persona.expression');
    if (!VALID_EXPRESSIONS.has(expression)) {
      throw new FrontendContractError(`unsupported persona expression: ${expression}`);
    }
    if (characterExpression.expression !== expression) {
      throw new FrontendContractError('character_response expression must match persona expression');
    }

    const artifacts = Array.isArray(data.artifacts)
      ? data.artifacts.map((artifact, index) => normalizeArtifact(artifact, index))
      : [];

    return Object.freeze({
      status: 'verified',
      response,
      expression,
      portrait: nonEmptyString(persona.portrait, 'persona.portrait'),
      confidence: finitePercentage(data.confidence),
      trace: normalizeTrace(data.trace),
      artifacts,
      decisionId: nonEmptyString(data.decision_id, 'decision_id'),
      characterResponse: character,
      persistence: Object.freeze({
        committed: true,
        durable: persistence.durable === true,
      }),
    });
  }

  function unavailable(message = 'Aurelia cognitive service is unavailable.') {
    return Object.freeze({
      status: 'unavailable',
      response: nonEmptyString(message, 'unavailable message'),
      expression: 'neutral',
      confidence: null,
      trace: null,
      artifacts: [],
      characterResponse: null,
    });
  }

  return Object.freeze({
    CHARACTER_RESPONSE_SCHEMA,
    VALID_EXPRESSIONS,
    FrontendContractError,
    normalizeCognitiveCycle,
    unavailable,
  });
});
