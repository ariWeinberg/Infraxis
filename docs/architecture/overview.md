# Architecture overview

## Purpose and scope

Cloudspace Shared Platform is the stable boundary used by Cloudspace applications for three shared capabilities:

1. authentication through Authentik and OIDC;
2. authorization decisions through a Cloudspace contract backed by OPA and distributed by OPAL; and
3. billing state and entitlements through a Cloudspace contract backed by Stripe.

It is not an IAM product. It does not define arbitrary organization-wide roles, issue cloud access keys, manage Kubernetes users, or replace the authorization model of each Cloudspace service.

## Dependency direction

```text
Cloudspace consumer service / console
              |
              v
       Cloudspace contract
              |
              v
       platform application layer
        /          |          \
       v           v           v
   AuthN port   AuthZ port   Billing port
       |           |           |
   Authentik      OPA        Stripe
                   ^
                   |
                  OPAL
       (asynchronous policy/data distribution)
```

Consumer code MUST depend on Cloudspace request/response models and ports. It MUST NOT import Stripe SDK models, Authentik administration clients, OPA package paths, or OPAL client internals.

## Process boundaries

The first slice keeps the platform API as one process because there is no existing operational requirement that justifies multiple independently deployed Cloudspace processes. The code still separates domain ports and adapters so a future split is possible without changing the contract.

| Component | Responsibility | State | Initial deployment |
|---|---|---|---|
| `platform-api` | Public Cloudspace API, principal normalization, orchestration | Cloudspace-owned PostgreSQL in target architecture | Kubernetes Deployment |
| `console` | Browser presentation and API consumption | None | Kubernetes Deployment |
| OPA | Policy evaluation | Policy/data cache | Upstream deployment |
| OPAL server/client | Policy and data distribution | Distribution metadata/cache | Upstream deployment |
| Authentik | Authentication authority | Authentik-owned state | Existing/upstream deployment |
| Stripe | Payment provider | Stripe-owned state | External service |

## Request paths

### Authentication

```text
Browser -> Authentik OIDC authorization endpoint
Browser <- authorization code / redirect
Browser -> console session boundary
Console -> platform-api with bearer token
platform-api -> JWKS cache -> normalized Principal
```

### Authorization

```text
Consumer -> POST /v1/authorization/check
         -> Cloudspace input translation
         -> OPA decision endpoint (target)
         <- decision, decision ID, revision, obligations
```

OPAL is never on this synchronous path. It updates OPA policy and authorization data independently.

### Billing

```text
Stripe -> signed webhook -> durable event record -> state transition
                                             -> entitlement projection
                                             -> OPAL data publication (target)
Consumer -> platform billing API -> local Cloudspace billing state
```

The platform MUST NOT call Stripe during every authorization check.

## Implemented versus target

The repository currently includes local adapters for offline execution and a standards-based OIDC/JWKS adapter with cryptographic tests. OPA HTTP, OPAL distribution, Stripe webhooks, durable PostgreSQL state, and live Kubernetes acceptance are target integrations documented here but are not yet implemented or deployed.
