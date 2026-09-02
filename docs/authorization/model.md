# Authorization model

## Primitive

Every protected operation reduces to:

```text
authorize(principal, action, resource, context) -> decision
```

The public endpoint is `POST /v1/authorization/check`. Consumers do not know OPA package paths. The platform owns the translation into OPA input and may later move evaluation closer to workloads without changing this contract.

## Actions

Actions have exactly three dot-separated segments:

```text
<service>.<resource>.<action>
```

Each segment begins with a lowercase letter and continues with lowercase letters, digits, or hyphens. Examples: `compute.instance.create`, `storage.object.write`, and `billing.account.read`.

Unknown actions MUST deny. Action names are API-like compatibility identifiers and require review before reuse or semantic changes.

## Resources

Resource strings are opaque to callers but must identify the protected object unambiguously. Policy input should normalize them into structured data before evaluation, for example:

```json
{"type":"billing-account","id":"billacct_123","tenant_id":"tenant_123"}
```

Tenant/account context is authoritative only when derived from the validated principal and server-side resource lookup.

## OPA and OPAL

OPA evaluates a normalized Cloudspace input document. OPAL distributes policy bundles and entitlement data asynchronously:

```text
policy Git + entitlement projection -> OPAL server -> OPAL client -> OPA
```

OPAL MUST NOT be called per authorization request. Each OPA decision should include or be correlated with a policy revision. Stale revision age must be observable; once beyond the service’s maximum tolerated age, the gateway fails closed.

## Decision semantics

- `decision=true` permits only the exact requested operation.
- `decision=false` is a deliberate deny and should be safe to show as a generic authorization error.
- evaluator timeout, malformed output, missing policy data, and unavailable dependencies are not implicit allows.
- obligations are instructions to the caller, not authorization itself; callers must understand them before acting.

## Policy review checklist

- expected allow;
- expected deny;
- missing and malformed input;
- cross-tenant access;
- unknown action;
- unavailable entitlement/context data;
- boundary ownership and empty collections;
- policy revision and rollback behavior.
