from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ErrorBody(BaseModel):
    code: str
    message: str
    request_id: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: ErrorBody


class PrincipalResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    type: str
    issuer: str
    tenant_id: str | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class MeResponse(BaseModel):
    principal: PrincipalResponse


class AuthorizationCheckRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    principal: PrincipalResponse
    action: str = Field(pattern=r"^[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$")
    resource: str = Field(min_length=1, max_length=512)
    context: dict[str, Any] = Field(default_factory=dict)


class AuthorizationDecisionResponse(BaseModel):
    decision: bool
    decision_id: str
    reason: str
    policy_revision: str
    obligations: list[dict[str, Any]] = Field(default_factory=list)


class BillingAccountResponse(BaseModel):
    id: str
    owner_principal_id: str
    provider: dict[str, str] | None = None


class SubscriptionResponse(BaseModel):
    id: str
    billing_account_id: str
    plan_id: str
    status: str
    provider: dict[str, str] | None = None


class BillingOverviewResponse(BaseModel):
    account: BillingAccountResponse | None
    subscription: SubscriptionResponse | None
