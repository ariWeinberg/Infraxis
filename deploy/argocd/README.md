# Argo CD dependency management

`dependencies.yaml` is the GitOps dependency graph for PostgreSQL, Redis, Authentik, OPA, and OPAL. It uses sync waves for data services, Authentik, and policy services. The Cloudspace API and console Applications remain in `platform-applications.yaml`.

## Before reconciliation

1. Replace example repository URLs.
2. Review and pin chart revisions against upstream release notes.
3. Create `cloudspace-postgresql`, `cloudspace-redis`, and `cloudspace-authentik` through the cluster secret manager.
4. Configure Authentik’s OIDC issuer, audience, redirect URIs, and JWKS URL.
5. Configure OPAL’s policy repository, data sources, and credentials.
6. Configure storage classes, backups, TLS, ingress, and NetworkPolicies.
7. Render and validate every Application and chart in CI.

The PostgreSQL and Redis charts provide a managed-in-cluster path for development and controlled environments. For production, prefer an externally managed PostgreSQL service or operator with tested backup/restore. Redis persistence and HA should be selected according to actual queue/cache requirements.

## Day-2 operations

- Upgrade one dependency at a time through a reviewed version change.
- Read upstream chart/application release notes.
- Render dev, staging, and production values before promotion.
- Observe migrations, readiness, policy revision, webhook queues, and error rates.
- Roll back the Git desired-state commit rather than editing live resources.
- Keep pruning disabled until ownership and recovery are proven.
