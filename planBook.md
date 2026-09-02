# Codex Planning Prompt — Cloudspace Shared Platform Infrastructure

You are acting as a principal platform architect and senior software engineer.

Your task is to DESIGN A COMPLETE IMPLEMENTATION PLAN for a professional-grade shared infrastructure platform that will serve as foundational infrastructure for a larger AWS-like cloud system called **Cloudspace**.

Do not begin implementation yet.

First inspect the existing repository thoroughly, understand its conventions and existing code, and then produce a detailed implementation plan.

The resulting system must be designed as production-quality infrastructure, not as a tutorial, proof of concept, or toy project.

---

# 1. Objective

Build the shared Cloudspace platform responsible for three foundational capabilities:

1. **Authentication**

   * Authentik

2. **Authorization**

   * OPA
   * OPAL

3. **Billing**

   * Stripe

This project is **not IAM**.

Do not turn it into an IAM system.

The platform must provide stable Cloudspace-owned interfaces around these capabilities so that Cloudspace applications and services do not become directly coupled to Authentik, OPA, OPAL, or Stripe implementation details.

The project must include:

* Backend services
* Web frontend
* Cloudspace Design System integration
* API contracts
* Authentication
* Authorization
* Policy management/distribution
* Billing
* Kubernetes manifests through Helm
* Argo CD GitOps configuration
* Bash-based CI
* Automated tests
* Security controls
* Observability
* Local development support
* Documentation

Design the project assuming it will eventually run as real shared infrastructure supporting many independently deployed Cloudspace services.

---

# 2. Fundamental Architecture Rule

External products are implementation details.

Consumers should see:

```text
Cloudspace Service
       |
       v
Cloudspace Contract
       |
       v
Cloudspace Shared Infrastructure
       |
       +---- Authentik
       +---- OPA
       +---- OPAL
       +---- Stripe
```

Avoid architectures like:

```text
compute-service ---> Authentik API
compute-service ---> Stripe API
compute-service ---> arbitrary OPA package path
```

Instead:

```text
compute-service
       |
       v
Cloudspace-owned interface
       |
       v
provider adapter
```

This boundary must be visible in:

* repository structure
* interfaces
* API schemas
* dependency direction
* tests
* documentation

Provider-specific SDKs and models must not leak into domain contracts.

---

# 3. Required Technology Direction

Prefer the following stack unless the existing repository provides a strong reason otherwise.

## Backend

* Python 3.13+
* FastAPI
* Pydantic
* SQLAlchemy
* Alembic
* PostgreSQL
* httpx
* OpenTelemetry
* Prometheus-compatible metrics

Use async APIs where appropriate.

Do not blindly make everything asynchronous where it provides no value.

## Frontend

* React
* TypeScript
* Vite
* Cloudspace Design System
* TanStack Query
* React Router
* generated API client from OpenAPI

The Cloudspace Design System must provide presentation primitives.

Avoid reimplementing generic UI components inside the application when equivalent Cloudspace Design System components exist.

## Authentication

Authentik.

Use standards such as:

* OAuth 2.0
* OpenID Connect

Do not invent a custom authentication protocol.

## Authorization

OPA for policy evaluation.

OPAL for policy and authorization-data distribution.

## Billing

Stripe.

Use Stripe test mode for development/test environments.

## Infrastructure

* Kubernetes
* Helm
* Argo CD

## CI

Portable Bash scripts.

Do NOT introduce:

* Jenkins
* Tekton
* Argo Workflows
* another CI orchestration platform

A hosting provider such as GitLab CI or GitHub Actions may invoke the scripts, but actual CI logic belongs in repository-controlled Bash scripts.

---

# 4. Repository Architecture

Evaluate the existing repository before deciding the exact structure.

A reasonable target is:

```text
/
├── apps/
│   ├── console/
│   └── platform-api/
│
├── services/
│   ├── authn-gateway/
│   ├── authz-gateway/
│   ├── billing-service/
│   └── event-service/
│
├── contracts/
│   ├── openapi/
│   ├── events/
│   └── schemas/
│
├── policies/
│   ├── rego/
│   ├── data/
│   └── tests/
│
├── deploy/
│   ├── helm/
│   ├── argocd/
│   └── environments/
│
├── ci/
│   ├── lib/
│   ├── lint.sh
│   ├── test.sh
│   ├── contract.sh
│   ├── security.sh
│   ├── build.sh
│   ├── package.sh
│   └── verify.sh
│
├── scripts/
├── docs/
│   ├── architecture/
│   ├── adr/
│   ├── contracts/
│   └── operations/
│
└── Makefile
```

This is guidance, not a requirement.

Do not create unnecessary microservices merely because directories were suggested.

Determine sensible process boundaries based on:

* security boundaries
* scaling characteristics
* failure isolation
* ownership
* deployment lifecycle
* data ownership
* operational complexity

Explicitly justify which components should be independent services and which should remain modules.

---

# 5. Contracts Are First-Class

The platform must have an extremely clear contract.

Contracts should be designed BEFORE implementation details.

Use versioned APIs:

```text
/v1/...
```

Maintain the canonical API specification under:

```text
contracts/openapi/
```

The contract should generate or validate:

* frontend TypeScript client
* backend request/response models where practical
* documentation

API changes must be testable for compatibility.

Avoid exposing provider-specific objects.

For example, Cloudspace API consumers should not receive raw Stripe Subscription objects.

Likewise, callers should not need knowledge of:

* Stripe object structures
* Authentik internal models
* Rego package names
* OPAL internals

---

# 6. Canonical Authentication Model

Define a Cloudspace-owned authenticated principal representation.

Conceptually:

```text
Principal
    id
    type
    issuer
    tenant/account context when applicable
    attributes
```

And an authentication context such as:

```text
AuthenticationContext
    principal
    session
    authentication metadata
```

Do not expose raw Authentik objects as the platform contract.

Authentication should ultimately produce a normalized Cloudspace representation.

Clearly document:

* browser authentication flow
* token validation
* service-to-service authentication
* token expiration
* refresh behavior
* logout
* invalid/revoked credentials
* issuer/audience validation
* key rotation
* failure modes

---

# 7. Canonical Authorization Contract

Authorization must have one obvious primitive.

Design around:

```text
authorize(
    principal,
    action,
    resource,
    context
) -> decision
```

Expose an API conceptually equivalent to:

```text
POST /v1/authorization/check
```

The request should contain:

```text
principal
action
resource
context
```

The result should contain at least:

```text
decision
decisionId
reason
policyRevision
obligations
```

Use fail-closed semantics.

If policy evaluation cannot produce a valid decision, access must not silently become allowed.

Actions should follow a consistent grammar:

```text
<service>.<resource>.<action>
```

Examples:

```text
compute.instance.create
compute.instance.read
compute.instance.start
compute.instance.stop
compute.instance.delete

storage.bucket.read
storage.object.write

network.vpc.create
```

Define the grammar formally.

Define resource identity formally.

Define how tenant/account ownership and request context are represented.

---

# 8. OPA Boundary

Consumers must not know OPA package paths.

Do not expose APIs requiring callers to understand:

```text
/v1/data/cloudspace/whatever/package/path
```

OPA is an implementation detail behind the Cloudspace authorization contract.

The authorization adapter/gateway translates the canonical Cloudspace request into the appropriate OPA input.

OPA policy structure may evolve without breaking consumers.

OPA decisions must be observable and auditable.

Capture useful metadata such as:

```text
request_id
decision_id
policy_revision
principal_id
resource
action
result
latency
```

without logging secrets or sensitive token material.

---

# 9. OPAL Architecture

OPAL distributes policy and policy-related data.

Do not place OPAL directly in the synchronous authorization request path.

The conceptual architecture should be:

```text
Policy Git
    |
    v
OPAL Server
    |
    v
OPAL Client
    |
    v
OPA
```

Authorization requests should normally reach an already synchronized OPA instance.

Design:

* policy propagation
* data propagation
* revision tracking
* synchronization health
* stale-policy detection
* rollout behavior
* rollback behavior
* failure handling

Initially centralized OPA evaluation may be acceptable.

However, design the authorization contract so evaluation can later move closer to workloads without changing consumer-facing APIs.

---

# 10. Policy Repository

Treat authorization policy as production code.

Structure policies clearly.

For example:

```text
policies/
├── common/
├── platform/
├── billing/
└── tests/
```

Every meaningful policy must have tests.

Test at least:

* expected allow
* expected deny
* missing input
* malformed input
* cross-account/tenant attempts
* unknown actions
* unavailable contextual data
* boundary cases

Use:

```text
opa test
opa fmt
```

in CI.

Policy changes must be reviewable independently from application implementation.

---

# 11. Billing Architecture

Create a Cloudspace billing domain around Stripe.

Stripe is the payment/billing provider.

It is not the Cloudspace domain model.

Define Cloudspace concepts such as:

```text
BillingAccount
Customer
Plan
Subscription
Entitlement
UsageRecord
Invoice
PaymentStatus
```

Determine which belong in the first implementation and which should be deferred.

Cloudspace resources should use Cloudspace identifiers.

Example:

```text
billacct_...
sub_...
plan_...
```

Stripe IDs should be stored as provider references rather than becoming canonical Cloudspace IDs.

Conceptually:

```json
{
  "id": "sub_...",
  "provider": {
    "type": "stripe",
    "externalId": "sub_..."
  }
}
```

Stripe SDK usage should live behind a Stripe infrastructure adapter.

Domain/application code should not directly depend on Stripe SDK types.

---

# 12. Stripe Webhooks

Treat webhook processing as a serious distributed-systems boundary.

Design for:

* signature verification
* idempotency
* replay
* duplicate events
* out-of-order events
* retries
* persistent event records
* transaction boundaries
* dead-letter/failure handling
* observability

Do not assume exactly-once delivery.

Do not perform unsafe state transitions merely because a webhook was received.

Store enough provider metadata to reconcile Cloudspace billing state with Stripe.

Define a reconciliation mechanism.

---

# 13. Entitlements

Billing state should be able to produce platform entitlements.

Keep entitlements separate from authorization decisions.

Conceptually:

```text
billing state
      |
      v
entitlements
      |
      v
authorization policy data
```

Do not synchronously call Stripe for every authorization request.

Relevant billing/entitlement state should be available locally or through distributed policy data.

OPAL may distribute authorization-relevant entitlement data to OPA.

Design how changes such as:

```text
subscription activated
subscription changed
subscription suspended
subscription canceled
payment state changed
```

eventually affect authorization data.

Define consistency expectations explicitly.

---

# 14. Backend Architecture

Use explicit dependency boundaries.

A service should approximately follow:

```text
service/
├── api/
├── application/
├── domain/
├── infrastructure/
└── main.py
```

Dependency direction:

```text
API
 |
 v
Application
 |
 v
Domain

Infrastructure implements ports/interfaces required by application/domain.
```

Provider-specific code belongs under infrastructure.

Examples:

```text
infrastructure/authentik/
infrastructure/opa/
infrastructure/opal/
infrastructure/stripe/
infrastructure/postgres/
```

Avoid unnecessary architecture ceremony, but maintain testable boundaries.

Use dependency injection where useful.

Avoid global mutable provider clients.

---

# 15. API Error Contract

Define one platform-wide error representation.

Conceptually:

```json
{
  "error": {
    "code": "AUTHORIZATION_DENIED",
    "message": "The requested operation is not permitted.",
    "requestId": "req_...",
    "details": {}
  }
}
```

Define stable machine-readable error codes.

At minimum consider:

```text
INVALID_ARGUMENT
UNAUTHENTICATED
AUTHORIZATION_DENIED
RESOURCE_NOT_FOUND
RESOURCE_CONFLICT
VALIDATION_FAILED
RATE_LIMITED
INTERNAL
SERVICE_UNAVAILABLE
```

Map these deliberately to HTTP status codes.

Do not leak:

* stack traces
* database errors
* Stripe internals
* OPA internals
* Authentik internals

through public APIs.

---

# 16. Request Identity and Tracing

Define consistent request metadata.

Support:

```text
Authorization
X-Request-ID
```

and W3C tracing:

```text
traceparent
tracestate
```

Determine whether account/tenant identifiers should be explicit headers, token-derived context, request parameters, or some combination.

Do not trust arbitrary client-provided ownership context without validation.

Logs should be structured.

Useful common fields include:

```text
timestamp
level
service
environment
request_id
trace_id
principal_id
operation
latency
status
authorization_decision_id
```

Never log credentials or complete access tokens.

---

# 17. Frontend

Build a professional Cloudspace platform console.

Use:

```text
React
TypeScript
Vite
Cloudspace Design System
TanStack Query
React Router
generated OpenAPI client
```

The frontend should consume the platform API rather than independently integrating with backend providers except where an authentication protocol explicitly requires browser redirects.

Use the Cloudspace Design System for:

* typography
* spacing
* buttons
* forms
* cards
* tables
* dialogs
* navigation
* badges
* loading states
* error states
* empty states

Avoid duplicating design-system primitives.

Design initial screens for relevant shared-platform functionality such as:

* account/session information
* billing overview
* current subscription
* invoices where appropriate
* billing management actions
* authentication/session errors

Do not create administrative screens merely to fill space.

---

# 18. Frontend Security

Do not expose:

* Stripe secret keys
* Authentik administrative credentials
* OPA administration
* OPAL administration
* Kubernetes credentials
* internal service tokens

Treat browser input as untrusted.

Authorization must be enforced server-side regardless of UI state.

Hiding a button is not authorization.

Define CSRF/XSS/session/token-storage considerations according to the chosen authentication flow.

---

# 19. Kubernetes Architecture

Deploy onto Kubernetes.

Establish sensible namespace boundaries.

Possible starting point:

```text
cloudspace-system
cloudspace-auth
cloudspace-policy
cloudspace-billing
cloudspace-observability
```

Justify the final namespace architecture.

Use Kubernetes-native:

* Deployments
* Services
* ServiceAccounts
* ConfigMaps
* Secrets
* NetworkPolicies
* PodDisruptionBudgets where appropriate
* probes
* resource requests/limits
* security contexts
* topology spread/anti-affinity where justified

Do not use privileged containers without an explicit unavoidable reason.

Use non-root execution where supported.

Use read-only root filesystems where practical.

Drop unnecessary Linux capabilities.

---

# 20. Secrets

Never commit real secrets.

Design secret injection for:

* Stripe keys
* Stripe webhook secrets
* Authentik secrets
* database credentials
* internal service credentials

Keep secret-management implementation replaceable where possible.

Helm values committed to Git must not contain production secrets.

Document development secret handling separately from production secret handling.

---

# 21. Helm

Package Cloudspace-owned deployable components with Helm.

Do not create one enormous chart unless analysis demonstrates that this is genuinely the best lifecycle boundary.

Prefer charts corresponding to independently deployable components.

Potential layout:

```text
deploy/helm/
├── platform-api/
├── console/
├── authz-gateway/
├── billing-service/
└── supporting-config/
```

External dependencies may use upstream charts where appropriate.

Do not unnecessarily copy upstream Authentik/OPA/OPAL charts into the repository.

Every Cloudspace chart should properly expose:

```text
image.repository
image.tag
imagePullPolicy

replicaCount

resources

service

ingress

probes

securityContext
podSecurityContext

serviceAccount

networkPolicy

podDisruptionBudget

affinity/topology settings

observability configuration
```

Never deploy mutable `latest` images.

---

# 22. Argo CD / GitOps

Argo CD owns Kubernetes reconciliation.

CI must NOT directly deploy production resources using:

```text
kubectl apply
helm upgrade
```

The desired model is:

```text
source
   |
   v
CI
   |
   +--> test
   +--> build
   +--> scan
   +--> push immutable image
   |
   v
GitOps desired state
   |
   v
Argo CD
   |
   v
Kubernetes
```

Design:

* Argo CD Applications/ApplicationSets where appropriate
* environment separation
* sync ordering where dependencies require it
* health checks
* automated sync policy
* pruning policy
* self-heal policy
* rollback strategy

Avoid excessive sync-wave coupling.

Use explicit dependencies only where necessary.

---

# 23. Environments

Support at least:

```text
dev
staging
prod
```

Avoid copying complete manifests three times.

Use Helm values and/or a sensible GitOps overlay mechanism.

Clearly separate:

```text
environment-specific configuration
```

from:

```text
application defaults
```

Production should differ intentionally in areas such as:

* replicas
* resources
* ingress
* security
* observability
* availability
* persistence
* external integrations

---

# 24. Bash CI

CI logic belongs in executable Bash scripts.

Example:

```text
ci/
├── lib/
│   ├── log.sh
│   ├── docker.sh
│   ├── helm.sh
│   └── git.sh
│
├── lint.sh
├── test.sh
├── contract.sh
├── security.sh
├── build.sh
├── package.sh
└── verify.sh
```

Scripts must be production-quality.

Use:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
```

where appropriate.

Scripts should:

* resolve repository root reliably
* validate required tools
* fail clearly
* produce useful errors
* avoid duplicated logic
* use functions
* quote variables correctly
* clean temporary resources
* support local execution
* behave consistently in CI

Run:

```text
shellcheck
shfmt
```

against CI scripts.

The CI provider configuration should mostly orchestrate these scripts.

---

# 25. CI Pipeline

Design a pipeline approximately equivalent to:

```text
commit
   |
   +------------------+
   |                  |
   v                  v
backend lint       frontend lint
   |                  |
backend tests      frontend tests
   |                  |
   +---------+--------+
             |
             v
       contract checks
             |
             v
         OPA tests
             |
             v
       security checks
             |
             v
         build images
             |
             v
     vulnerability scan
             |
             v
       push immutable images
             |
             v
          helm lint
             |
             v
        helm template
             |
             v
    Kubernetes validation
             |
             v
      update GitOps state
```

Parallelize independent jobs where the CI provider allows it.

Do not rebuild an image separately for every deployment stage.

Promote immutable artifacts.

Prefer digest or immutable commit-derived image references.

---

# 26. Backend Quality Gates

Include at minimum:

```text
ruff
mypy
pytest
```

Tests should include:

* unit tests
* API tests
* domain tests
* adapter tests
* database integration tests
* authorization integration tests
* billing webhook tests

Use realistic integration tests where mocks would hide important behavior.

---

# 27. Frontend Quality Gates

Include:

```text
eslint
tsc
vitest
```

Add component/integration testing where valuable.

Test:

* authentication state
* API error rendering
* billing state rendering
* loading states
* authorization-related UI behavior
* generated API integration

Do not make snapshot tests the primary testing strategy.

---

# 28. Contract Testing

The API contract is a first-class artifact.

CI should detect accidental breaking changes.

Validate that:

* OpenAPI is valid
* generated clients are current
* backend behavior conforms to the contract
* required error responses exist
* examples validate against schemas

Define an explicit API compatibility/versioning policy.

---

# 29. Security Scanning

Plan reasonable automated checks for:

* dependencies
* containers
* secrets
* Kubernetes manifests
* Helm rendering

Do not add ten overlapping scanners merely for appearances.

Select a small, maintainable toolset and explain why each tool exists.

Security checks should fail builds for appropriately severe findings.

Document suppression/exception procedures.

---

# 30. Observability

Every Cloudspace service must expose useful observability.

Provide:

## Logs

Structured logs.

## Metrics

Prometheus-compatible metrics.

At minimum:

```text
request count
request latency
error count
dependency latency/errors
authorization decision counts
authorization decision latency
billing webhook processing
billing webhook failures
policy synchronization health
```

Avoid unbounded metric labels.

## Tracing

OpenTelemetry.

Propagate trace context across internal HTTP requests.

## Health

Differentiate:

```text
liveness
readiness
startup
```

Do not make liveness depend unnecessarily on every downstream dependency.

---

# 31. Auditability

Security-sensitive operations need audit records.

Examples:

```text
authentication events
authorization decisions where appropriate
billing state transitions
provider webhook processing
policy updates
administrative configuration changes
```

Audit events should have stable schemas.

They should contain enough information for investigation without storing unnecessary secrets.

---

# 32. Reliability

Identify failure modes explicitly.

At minimum analyze:

* Authentik unavailable
* OPA unavailable
* OPAL unavailable
* stale authorization data
* Stripe unavailable
* Stripe webhook delayed
* PostgreSQL unavailable
* malformed provider responses
* expired signing keys
* network partition
* partial Kubernetes rollout
* duplicate webhook delivery

For each important dependency define:

```text
timeout
retry policy
backoff
circuit behavior if appropriate
fail-open vs fail-closed behavior
observability
recovery
```

Authorization should normally fail closed.

Billing provider temporary unavailability should not automatically destroy known local billing state.

---

# 33. Database

Use PostgreSQL for Cloudspace-owned persistent state where needed.

Clearly define which service owns each table/domain.

Do not create an undisciplined shared database that every service accesses directly.

Use Alembic migrations.

Migrations must be:

* version controlled
* tested
* safe for deployment
* compatible with rolling upgrades where possible

Document migration and rollback strategy.

---

# 34. Events

Determine whether an internal event mechanism is actually required.

Do not introduce Kafka, RabbitMQ, NATS, etc. merely because this is a distributed platform.

If reliable asynchronous processing is required, first identify the concrete requirements.

Consider patterns such as:

* transactional outbox
* persistent jobs
* webhook event queue

before introducing large infrastructure dependencies.

If a message broker is justified, document why.

---

# 35. IDs

Establish consistent Cloudspace resource IDs.

Prefer opaque IDs with recognizable resource prefixes.

Examples:

```text
req_...
dec_...
billacct_...
sub_...
plan_...
```

Do not expose sequential database IDs.

Centralize ID creation/validation behavior.

Document uniqueness and ordering characteristics.

---

# 36. Configuration

Follow twelve-factor-style configuration principles where appropriate.

Configuration should have:

* explicit schema
* validation at startup
* safe defaults
* environment overrides
* clear secret/non-secret distinction

A service should fail early when required configuration is invalid.

Avoid reading arbitrary environment variables throughout business logic.

Centralize configuration loading.

---

# 37. Local Development

Provide a reasonable developer workflow.

A new developer should be able to:

```text
clone
configure local secrets
start dependencies
run migrations
start backend
start frontend
run tests
```

without reverse-engineering Kubernetes.

Docker Compose may be used for local dependencies if appropriate.

Do not make a full Kubernetes cluster mandatory for every unit-development cycle.

Also provide a Kubernetes-based integration path for testing actual deployment behavior.

---

# 38. Documentation

Create documentation for:

```text
architecture
contracts
local development
deployment
operations
security model
authorization model
billing model
troubleshooting
```

Use ADRs for significant decisions.

Initial ADR candidates:

```text
ADR-001 service boundaries
ADR-002 authentication architecture
ADR-003 authorization contract
ADR-004 OPA/OPAL architecture
ADR-005 billing provider abstraction
ADR-006 API contract/versioning
ADR-007 GitOps deployment model
ADR-008 CI architecture
```

Documentation must explain WHY important decisions exist, not merely repeat configuration.

---

# 39. Professional Engineering Expectations

Avoid:

* placeholder architecture
* TODO-driven core functionality
* fake production abstractions
* unnecessary microservices
* massive god services
* provider SDK leakage
* duplicated schemas
* mutable production images
* secrets in Git
* manual production deployment
* undocumented API behavior
* authorization enforced only by the frontend
* arbitrary retries
* unbounded timeouts
* swallowing exceptions
* logging tokens
* wildcard Kubernetes RBAC
* unnecessary cluster-admin
* containers running as root without reason
* tests that only mock everything
* circular service dependencies

Prefer:

* explicit contracts
* small interfaces
* boring predictable architecture
* immutable artifacts
* deterministic builds
* least privilege
* fail-fast configuration
* fail-closed authorization
* structured errors
* structured logging
* reproducible development
* automated validation
* clear ownership boundaries

---

# 40. First Vertical Slice

Design the implementation so the first milestone proves the complete architecture vertically.

The first working milestone should include:

```text
Cloudspace Console
        |
        v
Authentik Login
        |
        v
Cloudspace Platform API
        |
        +--> GET /v1/me
        |
        +--> POST /v1/authorization/check
        |           |
        |           v
        |          OPA
        |           ^
        |           |
        |          OPAL
        |
        +--> Billing API
                    |
                    v
                  Stripe
```

It should demonstrate:

1. User authenticates through Authentik.

2. Frontend obtains valid authenticated state.

3. Platform API validates authentication.

4. `/v1/me` returns normalized Cloudspace identity information.

5. An authorization request is evaluated using the canonical authorization contract.

6. OPA evaluates a tested policy.

7. OPAL can propagate a policy or authorization-data change.

8. Stripe test-mode customer/subscription state can be represented through the Cloudspace billing API.

9. Stripe webhook signatures are validated.

10. Duplicate webhook processing is idempotent.

11. Billing/entitlement state can influence authorization data without synchronous Stripe calls during authorization.

12. Backend/frontend/policy tests run.

13. Images are built immutably.

14. Helm charts validate.

15. Argo CD can deploy the complete slice.

16. Metrics, logs, tracing, readiness and liveness are functional.

Do not expand into unrelated cloud services until this slice is solid.

---

# 41. Planning Task

DO NOT immediately generate hundreds of files.

First perform repository reconnaissance.

Inspect:

* current directory structure
* existing README/documentation
* package files
* Python configuration
* frontend configuration
* existing Cloudspace Design System
* Docker files
* Kubernetes resources
* Helm charts
* Argo CD resources
* existing CI
* Git conventions
* environment configuration
* tests
* naming conventions

Then produce a complete implementation plan.

The plan must contain:

## A. Current-State Assessment

What exists already?

What should be reused?

What conflicts with the target architecture?

What is missing?

## B. Proposed Architecture

Show component boundaries and communication paths.

Include ASCII diagrams where useful.

## C. Repository Structure

Give the proposed final repository tree.

Explain important directories.

## D. Service Boundaries

For every process/service explain:

* responsibility
* API
* dependencies
* persistence
* deployment
* scaling
* failure behavior

## E. Contract Design

Define the initial:

* authentication contract
* authorization contract
* billing contract
* error contract
* event/audit contract

Show representative schemas.

## F. Data Model

Define important entities and ownership.

Do not prematurely design every possible future table.

## G. Security Model

Explain:

* trust boundaries
* credentials
* token validation
* service authentication
* authorization
* secret handling
* network policy
* Kubernetes RBAC

## H. Deployment Architecture

Explain:

* Kubernetes topology
* namespaces
* Helm
* Authentik deployment
* OPA/OPAL deployment
* PostgreSQL
* Stripe external integration
* ingress
* Argo CD

## I. CI/CD

Describe every stage and its purpose.

Show which Bash script owns each operation.

## J. Testing Strategy

Cover:

* backend
* frontend
* contracts
* Rego
* integrations
* webhooks
* Helm
* Kubernetes
* end-to-end tests

## K. Observability

Define:

* logs
* metrics
* traces
* health checks
* audit events

## L. Failure Analysis

Create a table containing:

```text
Failure
Expected behavior
User-visible impact
Retry?
Fail-open/fail-closed
Alert?
Recovery
```

## M. Implementation Phases

Break implementation into small reviewable phases.

Each phase must specify:

* objective
* files/components affected
* dependencies
* tests
* completion criteria

## N. First Vertical Slice

Give particularly detailed implementation steps for the first complete end-to-end slice.

## O. Open Questions

Only include questions that represent genuine architectural ambiguity that cannot reasonably be resolved from repository context.

Prefer making and documenting reasonable engineering decisions rather than asking unnecessary questions.

---

# 42. Planning Quality

The plan should be detailed enough that another senior engineer could implement it without inventing major architectural decisions along the way.

At the same time, do not over-engineer speculative requirements.

For every significant new abstraction or infrastructure dependency ask:

```text
What concrete problem does this solve today?
```

If there is no strong answer, defer it.

When multiple approaches are possible:

1. identify the alternatives,
2. state the trade-offs,
3. select one,
4. explain why.

Favor simplicity until actual requirements justify complexity.

---

# 43. Final Deliverable

After repository inspection, return the plan in this order:

```text
1. Executive Summary
2. Current Repository Assessment
3. Architectural Principles
4. Target Architecture
5. Component Responsibilities
6. Repository Structure
7. API and Contract Design
8. Authentication Architecture
9. Authorization / OPA / OPAL Architecture
10. Billing / Stripe Architecture
11. Data Ownership and Persistence
12. Frontend Architecture
13. Security Architecture
14. Kubernetes Architecture
15. Helm Strategy
16. Argo CD / GitOps Strategy
17. Bash CI Architecture
18. Testing Strategy
19. Observability and Auditability
20. Reliability and Failure Modes
21. Local Development Workflow
22. Implementation Phases
23. Detailed First Vertical Slice
24. Acceptance Criteria
25. ADRs to Create
26. Open Questions
```

Be specific.

Use concrete paths, API signatures, component names, dependency directions, and deployment boundaries.

Challenge architectural choices that would create unnecessary coupling.

Do not simply agree with assumptions in this prompt if repository evidence demonstrates a better implementation.

However, preserve the non-negotiable requirements:

* Authentik for authentication
* OPA + OPAL for authorization
* Stripe for billing
* Cloudspace Design System for frontend presentation
* explicit Cloudspace-owned contracts
* frontend and backend
* Kubernetes
* Helm
* Argo CD
* Bash-owned CI logic
* production-grade security/testing/observability
* this project is not IAM

Your immediate task is PLANNING, not bulk implementation.
