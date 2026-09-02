# Testing strategy

## Test layers

| Layer | Purpose | Examples |
|---|---|---|
| Domain/unit | Deterministic business rules | IDs, action grammar, state transitions |
| API | Contract and HTTP behavior | `/v1/me`, authorization, billing errors |
| Adapter | Provider translation | JWT/JWKS, OPA payload, Stripe signature |
| Database integration | Transactions and constraints | webhook idempotency, migrations |
| Policy | Security decisions | allow/deny, tenant boundary, missing data |
| Frontend | User-visible states | loading, errors, billing rendering |
| Deployment | Packaging correctness | Helm lint/template, schema validation |
| End-to-end | Complete slice | Authentik login through API and console |

## Required security tests

- reject malformed and unsigned JWTs;
- reject wrong issuer, audience, algorithm, signature, and expiry;
- accept rotated JWKS keys after refresh;
- reject unknown authorization actions;
- deny cross-tenant resources;
- fail closed when OPA or policy data is unavailable;
- verify webhook signatures before parsing/applying state;
- process duplicate provider events exactly once;
- prevent provider objects and secrets from appearing in API responses/logs.

## Test evidence

Commands must report the exact layer tested. Passing unit tests does not prove live Authentik, Stripe, OPAL, Kubernetes, or guest readiness. CI should publish reports and retain failed provider payloads only after redaction.
