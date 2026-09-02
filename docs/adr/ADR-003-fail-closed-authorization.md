# ADR-003: Authorization failures fail closed

## Status

Accepted.

## Decision

Only an explicit valid allow decision permits an operation. OPA outage, malformed output, stale policy beyond the configured threshold, missing entitlement data, or network timeout is not an allow.

## Consequences

Some legitimate operations may be unavailable during policy incidents. This is intentional for a shared authorization boundary; availability recovery must use health monitoring, rollback, and reconciliation rather than fail-open bypasses.
