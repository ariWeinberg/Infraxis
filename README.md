# Cloudspace Shared Platform

Cloudspace-owned interfaces for authentication, authorization, and billing. The project is deliberately not IAM: it normalizes identity, evaluates policy, and represents billing state for Cloudspace services without exposing Authentik, OPA/OPAL, or Stripe models.

## Current vertical slice

The runnable slice provides a FastAPI platform API with local development adapters, a React console, a canonical OpenAPI contract, tested Rego policy, Docker Compose wiring, Helm charts, and Argo CD desired state. Local adapters make the slice runnable without external credentials; production adapters are explicit follow-up work tracked in `checklist.md`.

```text
Console -> Platform API -> Cloudspace contracts -> Authentik / OPA / OPAL / Stripe adapters
                                      ^
                                      +-- local adapters for development and tests
```

## Local development

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --app-dir apps/platform-api --reload
```

Then open the console through Vite (`npm install && npm run dev` in `apps/console`) or call `GET /v1/me` with `Authorization: Bearer dev-user-alice`.

## Verification

```bash
./ci/verify.sh
```

The complete documentation index is in [`docs/README.md`](docs/README.md). It includes the contract, authentication, authorization, billing, security, development, deployment, operations, and testing guides.

The repository does not commit real credentials. Authentik OIDC, Stripe, OPAL synchronization, PostgreSQL migrations, image publishing, and live-cluster checks require environment-specific infrastructure and remain explicit checklist items.
