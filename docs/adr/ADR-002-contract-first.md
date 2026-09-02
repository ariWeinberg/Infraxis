# ADR-002: OpenAPI is the canonical consumer contract

## Status

Accepted.

## Decision

Maintain versioned OpenAPI under `contracts/openapi/`. Backend models and frontend clients may be generated or checked against it, but provider SDK models never become public schemas.

## Consequences

Contract changes become reviewable and compatibility-testable. The repository must add generation and drift checks before claiming the frontend client is generated.
