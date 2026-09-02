# Contract guide

The canonical API is [`contracts/openapi/cloudspace-v1.yaml`](https://github.com/ariWeinberg/Infraxis/blob/main/contracts/openapi/cloudspace-v1.yaml). The URL namespace is versioned as `/v1`. Provider details are intentionally absent from public models.

## Compatibility rules

### Allowed non-breaking changes

- adding an optional response property;
- adding a new endpoint;
- adding a new documented error detail that clients can ignore;
- adding a new enum value only when consumers are required to handle unknown values safely.

### Breaking changes

- removing or renaming a property;
- changing a property type or meaning;
- making an optional request property required;
- changing authorization from deny to allow for an existing request without policy review;
- exposing provider IDs as Cloudspace canonical IDs;
- changing an HTTP status or stable error code without a versioning decision.

Breaking changes require a new API version or an approved migration plan. Every contract change MUST update the OpenAPI document, server tests, examples, and consumer client generation.

## Request metadata

- `Authorization: Bearer <access-token>` carries the validated credential.
- `X-Request-ID` MAY be supplied by a trusted upstream and MUST be returned unchanged when valid; otherwise the platform generates a `req_...` ID.
- `traceparent` and `tracestate` carry W3C trace context in the target observability implementation.
- Tenant/account ownership MUST come from validated principal claims or server-side lookup. A client-supplied tenant header is not authoritative.

## Error contract

```json
{
  "error": {
    "code": "AUTHORIZATION_DENIED",
    "message": "The requested operation is not permitted.",
    "request_id": "req_01H...",
    "details": {}
  }
}
```

Stable codes: `INVALID_ARGUMENT`, `UNAUTHENTICATED`, `AUTHORIZATION_DENIED`, `RESOURCE_NOT_FOUND`, `RESOURCE_CONFLICT`, `VALIDATION_FAILED`, `RATE_LIMITED`, `INTERNAL`, and `SERVICE_UNAVAILABLE`.

Public messages MUST be safe for end users. Stack traces, SQL text, access tokens, Stripe payloads, Authentik responses, and OPA internals MUST remain server-side.

## Authorization request

```json
{
  "principal": {
    "id": "user_123",
    "type": "user",
    "issuer": "https://auth.example.com/application/o/cloudspace/",
    "tenant_id": "tenant_123",
    "attributes": {"roles": ["member"]}
  },
  "action": "billing.account.read",
  "resource": "billing-account:billacct_123",
  "context": {"request_ip": "203.0.113.10"}
}
```

The decision response contains `decision`, `decision_id`, `reason`, `policy_revision`, and `obligations`. A false decision is a normal business result; inability to evaluate is an operational failure and MUST fail closed.

## IDs

IDs are opaque and prefixed: `req_`, `dec_`, `billacct_`, `sub_`, and `plan_`. Database sequence values MUST NOT be public identifiers. Provider IDs belong in a provider-reference object and are never used as the Cloudspace resource identity.
