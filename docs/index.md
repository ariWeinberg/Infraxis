# Cloudspace Shared Platform

<div class="hero">
  <div>
    <p class="hero-kicker">Shared infrastructure for Cloudspace</p>
    <h1>One stable contract.<br><span>Four replaceable providers.</span></h1>
    <p class="hero-copy">Authentication, authorization, billing, and entitlement state exposed through Cloudspace-owned APIs—ready for local development and designed for GitOps-managed Kubernetes.</p>
    <div class="hero-actions"><a class="md-button md-button--primary" href="architecture/overview/">Explore the architecture</a><a class="md-button" href="development/local/">Run it locally</a></div>
  </div>
  <div class="hero-card"><div class="hero-card-label">Current vertical slice</div><div class="metric"><strong>8</strong><span>API and adapter tests</span></div><div class="metric"><strong>3</strong><span>provider boundaries</span></div><div class="metric"><strong>1</strong><span>canonical OpenAPI contract</span></div></div>
</div>

## What this platform owns

| Capability | Cloudspace contract | Provider implementation |
|---|---|---|
| Authentication | normalized `Principal` | Authentik OIDC/JWKS |
| Authorization | `authorize(principal, action, resource, context)` | OPA, policy/data distributed by OPAL |
| Billing | accounts, plans, subscriptions, entitlements | Stripe |
| Persistence | Cloudspace-owned projections and audit records | PostgreSQL, Redis for operational workloads |

!!! warning "Know the boundary"
    This is not IAM. Cloudspace Shared Platform does not manage arbitrary cloud roles, access keys, Kubernetes identities, or permissions for every service. It provides shared authentication, policy decisions, and billing facts that services consume.

## The request path

```mermaid
flowchart LR
  C[Cloudspace service or console] --> API[Cloudspace API contract]
  API --> A[Authentik OIDC adapter]
  API --> O[OPA authorization adapter]
  API --> S[Stripe billing adapter]
  P[Policy Git and entitlement projection] --> OPAL[OPAL distribution]
  OPAL --> O
```

## Start with the right guide

- **Building a consumer?** Read the [contract guide](contracts/guide.md) and [SDK reference](sdk.md).
- **Adding authentication?** Read [Authentik OIDC](authentication/oidc.md).
- **Writing policy?** Read the [authorization model](authorization/model.md).
- **Deploying the platform?** Read [Kubernetes and Argo CD](deployment/kubernetes.md) and [dependency management](deployment/argocd.md).
- **Responding to an incident?** Open the [operations runbook](operations/runbook.md).

!!! info "Implementation status"
    The repository currently provides an offline runnable slice, a tested OIDC/JWKS adapter, an OPA contract adapter, SDK foundations, and GitOps definitions. Live Authentik, OPA/OPAL, Stripe, PostgreSQL, and Kubernetes verification still requires environment-specific credentials and cluster state.
