# Operations runbook

## First response

1. Record the alert, UTC time, environment, request ID, trace ID, and affected tenant if known.
2. Check liveness, readiness, recent deployment, and dependency health.
3. Determine whether the issue is authentication, authorization, billing, persistence, or delivery.
4. Avoid changing policy or billing state manually until the audit trail and blast radius are understood.
5. Prefer rollback/restart/reconciliation over destructive data changes.

## Authentication incident

Symptoms: widespread `401`, JWKS fetch errors, signing-key mismatch, or redirect failures.

Checks: verify issuer URL, audience, TLS/DNS, JWKS response, Authentik key rotation timeline, and clock synchronization. Do not disable signature validation or switch production to local mode. If a key was compromised, rotate it through Authentik and invalidate affected sessions according to the incident plan.

## Authorization incident

Symptoms: `403`, evaluator timeout, stale policy, or unexpected decision changes.

Checks: compare `decision_id`, policy revision, OPA health, OPAL sync age, entitlement revision, and the exact normalized input. Fail closed while investigating. Roll back policy through Git/Argo CD, then reconcile OPA data. Do not “fix” a denial by bypassing the gateway.

## Billing incident

Symptoms: missing subscription, delayed entitlement, duplicate transition, webhook failures.

Checks: signature verification result, provider event ID, local event status, transition version, Stripe dashboard event, and reconciliation age. Replay only through an idempotent operator command. Never delete event history to clear a queue.

## Database incident

Checks: connection pool saturation, migration status, locks, replication/backup health, and error rate. Preserve local billing state during provider outages. Stop rollout if migrations are not compatible with the previous version.

## Recovery objectives

The deployment owner must set concrete RTO/RPO values per environment. Until those are agreed, the platform should document measured values rather than inventing guarantees. Backups, restore drills, webhook replay, and policy rollback are separate recovery capabilities and must each be tested.
