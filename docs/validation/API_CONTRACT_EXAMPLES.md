# Aurelia HTTP API Contract Examples

This document shows the canonical HTTP contract exposed by `aurelia-server`. The examples are intentionally scoped to observable software behavior; they do not imply model quality, production safety certification, AGI, or physical-robot validation.

## Success: `POST /api/cognitive-cycle`

Request:

```json
{
  "message": "How should I evaluate an executive compensation offer?",
  "user_role": "Senior Engineering Manager",
  "target_role": "Director of Engineering"
}
```

Expected response class:

- HTTP **200**
- `response` contains the generated response text.
- `decision_id` identifies the persisted decision receipt.
- `verification.safe_to_publish` reports the publication gate.
- `persistence.committed` reports whether the cycle was committed.
- `persistence.durable` reports whether the canonical server persisted the cycle durably.
- `character_response.schema_version` identifies the typed embodiment contract.
- `character_response.verified` and `character_response.persistence_committed` preserve the downstream eligibility state.

The exact response payload should be inspected from the running server or the integration tests rather than copied as a permanently frozen example.

## Invalid request: missing message

Request:

```json
{
  "message": "   "
}
```

Expected behavior:

- HTTP **400**
- `error` is `No message provided`.
- `safe_to_publish` is `false`.
- No cognitive-cycle result is returned.

This is a request-validation failure, not a successful fallback response.

## Runtime unavailable

If the canonical cognitive runtime is unavailable:

- HTTP **503**
- `safe_to_publish` is `false`.
- The API returns an explicit unavailable-runtime error.
- No legacy success-looking response is synthesized.

## Cognitive execution failure

If a known cognitive execution or persistence failure occurs:

- HTTP **500**
- `safe_to_publish` is `false`.
- `error_type` identifies the controlled exception class.
- No successful `response` field is returned.

## Unexpected runtime failure

Unexpected exceptions are intentionally sanitized at the HTTP boundary:

- HTTP **500**
- `error_type` is `RuntimeError`.
- `error` is the generic message `Aurelia cognitive cycle failed unexpectedly.`.
- Internal exception details are not exposed through the API response.
- `safe_to_publish` is `false`.

## Contract source of truth

The serialization implementation lives in:

- `aurelia/runtime/api_contract.py`

The hardened Flask boundary is installed by:

- `aurelia/runtime/app_bootstrap.py`

Regression coverage lives in:

- `tests/stabilization/test_integration_hardening.py`

These examples document the current contract; they do not create a second runtime source of truth.
