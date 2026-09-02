# Cloudspace Shared Platform Implementation Checklist

This checklist is the implementation ledger for `planBook.md`. Items are checked only after the corresponding files exist and the applicable verification has passed. The repository started with only the planning document, so the implementation establishes the initial conventions and vertical slice.

## 0. Repository baseline and working rules

- [x] Read `planBook.md` completely.
- [x] Inspect the repository tree and Git status.
- [x] Confirm that no pre-existing application code, CI, Helm, Argo CD, frontend, backend, or test conventions exist.
- [x] Preserve the user-provided untracked `planBook.md` without modifying it.
- [x] Create this checklist before implementation changes.
- [x] Keep provider-specific models behind infrastructure adapters in the initial API slice.
- [x] Keep the implementation Cloudspace-owned and explicitly out of IAM scope.
- [x] Update this checklist after each implementation milestone.

## 1. Repository foundation

- [x] Add top-level README with scope, architecture, quick start, and verification commands.
- [x] Add backend Python project metadata and controlled tool configuration.
- [x] Add frontend TypeScript/Vite project metadata.
- [x] Add shared API contract directory and versioning convention.
- [x] Add policy directory and policy test layout.
- [x] Add documentation directories and initial architecture/security/operations documents.
- [x] Add Makefile targets that delegate to reproducible commands.
- [x] Add safe example environment configuration with no real secrets.
- [x] Add repository ignore rules for local secrets, caches, builds, and generated output.

## 2. Platform API domain and contracts

- [x] Define canonical request/error/health/principal/authorization/billing schemas.
- [ ] Define stable Cloudspace ID formats and validation helpers.
- [x] Define centralized validated settings with secret/non-secret separation.
- [x] Implement structured request identity handling.
- [x] Implement normalized authenticated principal model.
- [x] Implement application ports for authentication, authorization, and billing.
- [x] Implement `/health/live`, `/health/ready`, and `/v1/me`.
- [x] Implement `POST /v1/authorization/check` with fail-closed behavior.
- [x] Implement billing account/subscription read contract.
- [x] Implement deliberate public error mapping without provider leakage.
- [x] Add canonical OpenAPI specification.

## 3. Provider adapters

- [x] Implement Authentik-compatible OIDC/JWKS validation adapter using standards-based JWT validation.
- [x] Validate issuer, audience, signature, expiry, and key rotation behavior with mocked JWKS tests.
- [ ] Implement OPA adapter using the Cloudspace authorization input shape.
- [ ] Ensure callers never provide or depend on OPA package paths.
- [ ] Implement Stripe adapter boundary using Cloudspace billing models only.
- [ ] Implement Stripe signature verification boundary.
- [x] Add bounded JWKS fetch timeout and refresh-on-unknown-key behavior.
- [x] Add deterministic local/dev adapters for development and unit tests.

## 4. Persistence and billing events

- [ ] Add SQLAlchemy/PostgreSQL persistence models owned by the platform API/billing domain.
- [ ] Add Alembic migration configuration and initial migration.
- [ ] Persist provider references separately from Cloudspace IDs.
- [ ] Persist webhook events before applying state transitions.
- [ ] Enforce webhook idempotency with a unique provider event identifier.
- [ ] Handle duplicate, delayed, out-of-order, and failed webhook processing.
- [ ] Add replay/reconciliation command boundary.
- [ ] Add audit-event schema and persistence boundary.
- [ ] Add integration tests against PostgreSQL where available.

## 5. Authorization policy and distribution

- [x] Add initial Rego authorization policy and tests.
- [x] Define action grammar in the OpenAPI contract.
- [ ] Test allow, deny, missing/malformed input, cross-tenant, unknown action, and unavailable context cases.
- [ ] Add OPA test and formatting commands to CI.
- [ ] Add policy revision metadata and stale-policy health model.
- [ ] Add OPAL topology/configuration without placing OPAL in the synchronous request path.
- [ ] Add policy-data publication flow from local billing state to authorization data.
- [ ] Document propagation, rollback, stale-data, and fail-closed behavior.

## 6. Frontend console

- [x] Create React + TypeScript + Vite console shell.
- [x] Add React Router routes for account and billing states.
- [x] Add TanStack Query data access.
- [x] Add frontend API client boundary (generation tooling remains to be added).
- [x] Document the explicit Cloudspace Design System integration seam; the package is not present in this empty repository.
- [ ] Implement loading, empty, API-error, authentication-error, and billing-state views.
- [ ] Keep authorization server-side; UI state only reflects API results.
- [ ] Document browser authentication redirect/session/token-storage decisions.
- [ ] Add ESLint, TypeScript, Vitest, and frontend integration checks.

## 7. Kubernetes, Helm, and GitOps

- [ ] Add charts for `platform-api`, `console`, `authz-gateway` responsibility, and supporting configuration as justified by process boundaries.
- [ ] Add secure defaults: non-root, dropped capabilities, read-only filesystem where practical, probes, resources, and immutable image references.
- [ ] Add Services, ServiceAccounts, NetworkPolicies, PDBs, and observability annotations/configuration where applicable.
- [ ] Add dev/staging/prod values without duplicating complete manifests.
- [ ] Add Argo CD Applications/ApplicationSet strategy and sync/health policy.
- [ ] Keep CI free of direct production `kubectl apply` and `helm upgrade` deployment behavior.
- [x] Add local dependency Compose path; live Kubernetes integration remains environment-dependent.
- [ ] Validate charts with `helm lint`, `helm template`, and Kubernetes schema validation when tools are installed.

## 8. Bash CI and quality gates

- [ ] Add executable `ci/lint.sh` with reliable repository-root resolution.
- [ ] Add executable `ci/test.sh`.
- [ ] Add executable `ci/contract.sh`.
- [ ] Add executable `ci/security.sh`.
- [ ] Add executable `ci/build.sh`.
- [ ] Add executable `ci/package.sh`.
- [ ] Add executable `ci/verify.sh`.
- [ ] Add reusable checked Bash helpers and clear missing-tool failures.
- [ ] Add ShellCheck/shfmt checks where installed.
- [ ] Add Ruff, mypy, pytest, ESLint, tsc, Vitest, contract, Rego, image, Helm, and manifest gates.
- [ ] Add CI-provider-neutral pipeline documentation/configuration.

## 9. Verification and handoff

- [x] Run backend unit/API/domain tests: 5 passed in `.venv`.
- [x] Run frontend production build: `npm run build` passed.
- [ ] Run frontend lint/unit tests: scripts exist but ESLint/Vitest configuration is deferred.
- [x] Run OpenAPI/schema validation: YAML parse passed.
- [ ] Run Rego tests/format checks: OPA is not installed.
- [ ] Run webhook idempotency/signature tests.
- [ ] Run Helm rendering and Kubernetes validation.
- [ ] Run shell syntax/style checks.
- [ ] Run local startup smoke test for the platform API.
- [x] Review `git diff --check`.
- [x] Update this checklist with exact completed checks, limitations, and deferred external-system verification.

## 10. Current implementation boundary

- [x] Implemented runnable offline vertical slice with explicit local adapters.
- [x] Add Authentik OIDC/JWKS validation; live Authentik issuer verification remains environment-dependent.
- [ ] Replace local authorization with an OPA HTTP adapter and configure OPAL distribution.
- [ ] Replace local billing with Stripe adapter, signed webhook persistence, and reconciliation.
- [ ] Add PostgreSQL/Alembic migrations and durable audit/event storage.
- [ ] Add generated TypeScript client from the canonical OpenAPI document.
- [ ] Add real Cloudspace Design System package integration when the package/source is provided.
- [ ] Add frontend lint/typecheck/unit test configuration and lockfile.
- [ ] Add container scanning, Kubernetes schema validation, and immutable registry promotion.
- [ ] Validate Helm charts and Argo CD resources against a real cluster/toolchain.
- [ ] Add staging/prod values, secret injection, ingress, and environment-specific observability.
- [ ] Provide final file map and honest verification status.
