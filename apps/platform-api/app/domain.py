from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol


class PrincipalType(StrEnum):
    USER = "user"
    SERVICE = "service"


@dataclass(frozen=True)
class Principal:
    id: str
    type: PrincipalType
    issuer: str
    tenant_id: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AuthorizationRequest:
    principal: Principal
    action: str
    resource: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AuthorizationDecision:
    decision: bool
    decision_id: str
    reason: str
    policy_revision: str
    obligations: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class BillingAccount:
    id: str
    owner_principal_id: str
    provider_type: str | None = None
    provider_external_id: str | None = None


@dataclass(frozen=True)
class Subscription:
    id: str
    billing_account_id: str
    plan_id: str
    status: str
    provider_type: str | None = None
    provider_external_id: str | None = None


class AuthenticationPort(Protocol):
    async def authenticate(self, token: str) -> Principal: ...


class AuthorizationPort(Protocol):
    async def authorize(self, request: AuthorizationRequest) -> AuthorizationDecision: ...


class BillingPort(Protocol):
    async def get_account(self, principal: Principal) -> BillingAccount | None: ...

    async def get_subscription(self, account_id: str) -> Subscription | None: ...
