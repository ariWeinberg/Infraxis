# ADR-001: Start with one platform API process and explicit provider ports

## Status

Accepted for the initial implementation.

## Decision

Keep the public Cloudspace API, application orchestration, and initial billing/authentication/authorization modules in one deployable platform API. Keep provider integrations behind explicit ports and adapters.

## Reasoning

The repository began empty and has no measured scaling or ownership boundaries that justify multiple services. Independent processes would add deployment, authentication, observability, and data-ownership complexity before the first vertical slice proves value. Ports preserve a future extraction seam without leaking provider types.

## Consequences

The process is simpler to run but requires discipline to prevent a god module. A service split becomes justified when a domain has materially different scaling, security, release ownership, or failure-isolation requirements.
