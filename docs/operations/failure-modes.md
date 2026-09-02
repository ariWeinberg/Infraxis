# Failure behavior

| Failure | Behavior | Authorization | Recovery |
|---|---|---|---|
| Authentik unavailable | Existing sessions fail validation when keys cannot be refreshed; no new access | Fail closed | Restore issuer/JWKS reachability and rotate keys safely |
| OPA unavailable | Decision endpoint returns service unavailable | Fail closed | Restore OPA or route to a healthy evaluator |
| OPAL unavailable | Last known policy remains observable with stale status; no synchronous dependency | Fail closed if stale beyond policy threshold | Restore distribution and reconcile revision |
| Stripe unavailable | Local billing state remains intact; webhook/reconciliation retries are bounded | Entitlements use last known state | Retry reconciliation with backoff |
| Duplicate webhook | Provider event ID is idempotency key | No duplicate transition | Replay safely |
