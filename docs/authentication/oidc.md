# Authentication and Authentik OIDC

## Authority

Authentik is the authentication authority. Cloudspace uses OIDC/OAuth standards and does not invent a login protocol. Authentik administration APIs are infrastructure-only and are not part of the consumer contract.

## Token validation requirements

The OIDC adapter MUST:

1. parse the JWT header without trusting it as authenticated data;
2. require a `kid` and permit only the configured signing algorithm (`RS256` in the current adapter);
3. obtain signing keys from the configured JWKS endpoint over TLS;
4. cache keys for a bounded period;
5. refresh immediately when a previously unknown `kid` is received;
6. verify signature, issuer, audience, and expiration;
7. require `sub`, `iss`, `aud`, and `exp` claims;
8. map claims into the Cloudspace `Principal` and discard provider-specific structure.

The current implementation is `OIDCAuthenticationAdapter` in `apps/platform-api/app/adapters.py`. `auth_mode=local` is for offline development only. Production configuration MUST use `auth_mode=oidc` and a real `oidc_jwks_url`.

## Principal mapping

```text
OIDC sub       -> Principal.id
OIDC iss       -> Principal.issuer
OIDC tenant_id -> Principal.tenant_id when configured by the issuer
OIDC roles     -> Principal.attributes.roles
```

The issuer, audience, and claim mapping are configuration/policy decisions, not browser input.

## Browser flow

1. The console redirects the browser to Authentik’s authorization endpoint.
2. Authentik authenticates the user and applies its own MFA/session controls.
3. Authentik redirects back to the configured Cloudspace callback with an authorization code.
4. The code is exchanged using the selected confidential/public-client design.
5. The console calls Cloudspace endpoints with the resulting access token.
6. Logout invalidates the local session and uses the provider logout endpoint when required.

The final production choice between a backend-for-frontend session cookie and browser-held tokens requires an ADR. Until then, no token should be placed in localStorage by default; XSS and CSRF protections must be designed together with the flow.

## Failure behavior

- missing/malformed token: `401 UNAUTHENTICATED`;
- bad signature, issuer, audience, or expiration: `401 UNAUTHENTICATED`;
- unknown signing key: one bounded JWKS refresh, then reject;
- JWKS timeout/unavailability: do not accept an unvalidated token;
- key rotation: accept new keys after refresh while retaining valid cached keys until expiry;
- clock skew: use a small explicitly documented leeway, never an unbounded grace period.

## Operational checklist

- Configure exact issuer and audience, including trailing-slash semantics.
- Configure TLS verification and network egress policy.
- Monitor JWKS fetch failures and validation failures separately.
- Rotate signing keys in Authentik with overlap so old tokens can expire naturally.
- Never log complete tokens or authorization codes.
- Test issuer, audience, expiry, signature, algorithm, missing claims, and rotation before rollout.
