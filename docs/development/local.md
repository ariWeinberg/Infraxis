# Local development

## Prerequisites

- Python 3.13 or newer;
- Node.js 22 or newer;
- Docker and Docker Compose for dependency testing;
- optional: `opa`, `helm`, `shellcheck`, and a Kubernetes cluster for extended gates.

## API setup

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --app-dir apps/platform-api --reload
```

The local adapter accepts `Bearer dev-user-alice`. This is a test convenience, not an authentication mechanism. Never use local mode in staging or production.

## Console setup

```bash
cd apps/console
npm install
npm run dev
```

The current console calls the API with a development token and should be replaced with the Authentik browser flow before production use.

## Compose

```bash
docker compose up --build
```

Compose currently starts the platform API and OPA. It does not provision Authentik, OPAL, Stripe, or PostgreSQL. Add those dependencies only with explicit local configuration and disposable credentials.

## Test commands

```bash
./ci/verify.sh
cd apps/console && npm run build
```

Optional checks run when tools are installed. The scripts must fail clearly when a required tool is required by a CI job, rather than silently treating an unavailable production check as passed.

## Change workflow

1. Update the canonical contract or domain port first.
2. Add a focused test that demonstrates the intended behavior.
3. Implement the adapter/application change.
4. Run the smallest relevant test, then `./ci/verify.sh`.
5. Update documentation and checklist status.
6. Make one focused commit.
