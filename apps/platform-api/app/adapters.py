import asyncio
import json
import time
from uuid import uuid4

import httpx
import jwt

from .config import Settings
from .domain import (
    AuthenticationPort,
    AuthorizationDecision,
    AuthorizationPort,
    AuthorizationRequest,
    AuthorizationUnavailable,
    BillingAccount,
    BillingPort,
    Principal,
    PrincipalType,
    Subscription,
)


class LocalAuthenticationAdapter(AuthenticationPort):
    """Explicit local adapter; production uses OIDC/JWKS validation."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def authenticate(self, token: str) -> Principal:
        if not token or token == "invalid":
            raise ValueError("invalid credentials")
        return Principal(
            id=token.removeprefix("dev-user-") or "dev-user",
            type=PrincipalType.USER,
            issuer=self.settings.oidc_issuer,
            tenant_id="tenant-dev",
            attributes={"roles": ["member"]},
        )


class OIDCAuthenticationAdapter(AuthenticationPort):
    """Validates Authentik-issued OIDC JWTs using the issuer's rotating JWKS."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        if not settings.oidc_jwks_url:
            raise ValueError("OIDC_JWKS_URL is required when OIDC authentication is enabled")
        self.settings = settings
        self._client = client
        self._keys: dict[str, object] = {}
        self._keys_expire_at = 0.0
        self._refresh_lock = asyncio.Lock()

    async def _load_keys(self, force: bool = False) -> None:
        if not force and self._keys and time.monotonic() < self._keys_expire_at:
            return
        async with self._refresh_lock:
            if not force and self._keys and time.monotonic() < self._keys_expire_at:
                return
            own_client = self._client is None
            client = self._client or httpx.AsyncClient(
                timeout=self.settings.request_timeout_seconds
            )
            try:
                response = await client.get(self.settings.oidc_jwks_url)
                response.raise_for_status()
                document = response.json()
                self._keys = {
                    key["kid"]: jwt.PyJWK.from_json(json.dumps(key)).key
                    for key in document.get("keys", [])
                    if key.get("kid")
                }
                if not self._keys:
                    raise ValueError("OIDC JWKS contained no usable keys")
                self._keys_expire_at = time.monotonic() + 300
            except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
                raise ValueError("OIDC signing keys are unavailable") from exc
            finally:
                if own_client:
                    await client.aclose()

    async def authenticate(self, token: str) -> Principal:
        if not token:
            raise ValueError("missing credentials")
        try:
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")
            algorithm = header.get("alg")
            if algorithm != "RS256" or not kid:
                raise ValueError("unsupported token header")
            await self._load_keys()
            if kid not in self._keys:
                await self._load_keys(force=True)
            key = self._keys.get(kid)
            if key is None:
                raise ValueError("unknown signing key")
            claims = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=self.settings.oidc_audience,
                issuer=self.settings.oidc_issuer,
                options={"require": ["sub", "iss", "aud", "exp"]},
            )
        except (jwt.PyJWTError, ValueError) as exc:
            raise ValueError("invalid OIDC credentials") from exc
        return Principal(
            id=str(claims["sub"]),
            type=PrincipalType.SERVICE if claims.get("typ") == "service" else PrincipalType.USER,
            issuer=str(claims["iss"]),
            tenant_id=claims.get("tenant_id"),
            attributes={"roles": claims.get("roles", [])},
        )


class LocalAuthorizationAdapter(AuthorizationPort):
    async def authorize(self, request: AuthorizationRequest) -> AuthorizationDecision:
        allowed = (
            request.action == "billing.account.read"
            and request.resource == f"billing-account:{request.principal.tenant_id}"
        )
        return AuthorizationDecision(
            decision=allowed,
            decision_id=f"dec_{uuid4().hex}",
            reason="policy_allow" if allowed else "policy_deny",
            policy_revision="local-dev-1",
        )


class OPAAuthorizationAdapter(AuthorizationPort):
    """Translates the Cloudspace decision contract to OPA's private data API."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self._client = client

    async def authorize(self, request: AuthorizationRequest) -> AuthorizationDecision:
        payload = {
            "input": {
                "principal": {
                    "id": request.principal.id,
                    "type": request.principal.type.value,
                    "issuer": request.principal.issuer,
                    "tenant_id": request.principal.tenant_id,
                    "attributes": request.principal.attributes,
                },
                "action": request.action,
                "resource": request.resource,
                "context": request.context,
            }
        }
        own_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=self.settings.request_timeout_seconds)
        try:
            response = await client.post(
                f"{self.settings.opa_url.rstrip('/')}/{self.settings.opa_decision_path.lstrip('/')}",
                json=payload,
            )
            response.raise_for_status()
            raw = response.json().get("result")
            result = raw if isinstance(raw, dict) else {"allow": raw}
            if not isinstance(result.get("allow"), bool):
                raise AuthorizationUnavailable("OPA response did not contain a boolean decision")
            return AuthorizationDecision(
                decision=result["allow"],
                decision_id=str(result.get("decision_id", f"dec_{uuid4().hex}")),
                reason=str(
                    result.get("reason", "policy_allow" if result["allow"] else "policy_deny")
                ),
                policy_revision=str(result.get("policy_revision", "unknown")),
                obligations=result.get("obligations", []),
            )
        except (httpx.HTTPError, ValueError, TypeError, AuthorizationUnavailable) as exc:
            raise AuthorizationUnavailable("OPA did not return a valid decision") from exc
        finally:
            if own_client:
                await client.aclose()
class LocalBillingAdapter(BillingPort):
    async def get_account(self, principal: Principal) -> BillingAccount | None:
        if principal.tenant_id is None:
            return None
        return BillingAccount(id=f"billacct_{principal.tenant_id}", owner_principal_id=principal.id)

    async def get_subscription(self, account_id: str) -> Subscription | None:
        return Subscription(
            id="sub_local_dev",
            billing_account_id=account_id,
            plan_id="plan_free",
            status="active",
        )
