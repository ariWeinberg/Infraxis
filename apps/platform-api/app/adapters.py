from uuid import uuid4

from .config import Settings
from .domain import (
    AuthenticationPort,
    AuthorizationDecision,
    AuthorizationPort,
    AuthorizationRequest,
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
