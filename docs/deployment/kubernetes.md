# Kubernetes deployment

## Namespaces

The target separation is:

- `cloudspace-system`: platform API, console, ingress-facing services;
- `cloudspace-policy`: OPA and OPAL components;
- `cloudspace-auth`: Authentik only when Cloudspace operates it;
- `cloudspace-billing`: billing workers/storage if split into a separate process;
- `cloudspace-observability`: shared telemetry resources.

Namespace boundaries are security and ownership boundaries, not cosmetic folders. A deployment should start with the smallest number of namespaces that maps to real access-control and lifecycle requirements.

## Workload defaults

Every Cloudspace chart should define:

- immutable image repository/tag or digest;
- replica count and resource requests/limits;
- startup, readiness, and liveness probes;
- non-root security context;
- dropped Linux capabilities and disabled privilege escalation;
- read-only root filesystem where compatible;
- dedicated ServiceAccount with token automount disabled unless needed;
- NetworkPolicy for ingress and egress;
- PodDisruptionBudget for multi-replica services;
- structured environment configuration and secret references.

Liveness must answer “is the process alive?” and should not fail because Stripe or OPA is temporarily unavailable. Readiness may include dependencies required to serve safely. Startup probes protect slow initialization from premature restarts.

## Secrets

Production values in Git contain references, not values. Inject Authentik client secrets, Stripe keys, webhook secrets, database credentials, and internal credentials through the selected secret manager. Local `.env` files are ignored and must never be committed.

## Argo CD

CI builds and scans immutable artifacts, updates GitOps desired state, and stops. Argo CD reconciles that state. CI MUST NOT use `kubectl apply` or `helm upgrade` as the production deployment mechanism. Automated pruning should remain disabled until resource ownership and rollback behavior are proven.

## Rollout and rollback

1. Render the exact chart and values.
2. Validate manifests against Kubernetes schemas.
3. Deploy to dev and observe startup/readiness/metrics.
4. Promote the same image digest to staging.
5. Run contract and smoke tests.
6. Promote to production through a reviewed GitOps change.
7. Roll back by reverting the desired-state commit or selecting a known-good immutable image.

Database migrations must be backward-compatible with the previous application version during rolling updates.
