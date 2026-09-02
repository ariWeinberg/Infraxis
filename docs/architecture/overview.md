# Architecture overview

The platform API owns Cloudspace contracts and application orchestration. Provider adapters implement ports behind that API. Browser consumers use OIDC redirects for Authentik and then call Cloudspace endpoints; they do not call provider administration APIs. Authorization is synchronous through the Cloudspace decision endpoint, with OPA as an adapter and OPAL as an asynchronous policy/data distribution path. Stripe webhooks update local billing state; authorization reads local entitlement data rather than calling Stripe.

The first implementation uses local adapters so contract and boundary tests run offline. Replacing an adapter must not change `contracts/openapi/cloudspace-v1.yaml`.
