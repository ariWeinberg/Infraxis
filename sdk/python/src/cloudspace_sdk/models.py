from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Principal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    type: str
    issuer: str
    tenant_id: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class AuthorizationCheckRequest(BaseModel):
    principal: Principal
    action: str
    resource: str
    context: dict[str, Any] = Field(default_factory=dict)


class AuthorizationDecision(BaseModel):
    decision: bool
    decision_id: str
    reason: str
    policy_revision: str
    obligations: list[dict[str, Any]] = Field(default_factory=list)


class BillingAccount(BaseModel):
    id: str
    owner_principal_id: str
    provider: dict[str, str] | None = None


class Subscription(BaseModel):
    id: str
    billing_account_id: str
    plan_id: str
    status: str
    provider: dict[str, str] | None = None


class BillingOverview(BaseModel):
    account: BillingAccount | None
    subscription: Subscription | None


class CloudspaceError(RuntimeError):
    def __init__(self, code: str, message: str, request_id: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.request_id = request_id
        self.status_code = status_code
