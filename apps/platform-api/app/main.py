from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse

from .adapters import (
    LocalAuthenticationAdapter,
    LocalAuthorizationAdapter,
    LocalBillingAdapter,
    OIDCAuthenticationAdapter,
)
from .config import get_settings
from .contracts import (
    AuthorizationCheckRequest,
    AuthorizationDecisionResponse,
    BillingAccountResponse,
    BillingOverviewResponse,
    ErrorResponse,
    MeResponse,
    PrincipalResponse,
    SubscriptionResponse,
)
from .domain import AuthorizationRequest, Principal

app = FastAPI(title="Cloudspace Platform API", version="1.0.0")


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, _: ValueError):
    body = ErrorResponse(
        error={
            "code": "UNAUTHENTICATED",
            "message": "Valid authentication is required.",
            "request_id": getattr(request.state, "request_id", f"req_{uuid4().hex}"),
        }
    )
    return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=body.model_dump())


async def current_principal(
    authorization: str | None = Header(default=None),
) -> Principal:
    if not authorization or not authorization.startswith("Bearer "):
        raise ValueError("missing bearer token")
    config = get_settings()
    adapter = (
        OIDCAuthenticationAdapter(config)
        if config.auth_mode == "oidc"
        else LocalAuthenticationAdapter(config)
    )
    return await adapter.authenticate(authorization[7:])


@app.get("/health/live")
async def live() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready")
async def ready() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/me", response_model=MeResponse, responses={401: {"model": ErrorResponse}})
async def me(principal: Principal = Depends(current_principal)) -> MeResponse:  # noqa: B008
    return MeResponse(principal=PrincipalResponse(**principal.__dict__))


@app.post(
    "/v1/authorization/check",
    response_model=AuthorizationDecisionResponse,
    responses={401: {"model": ErrorResponse}},
)
async def authorization_check(
    request: AuthorizationCheckRequest,
    principal: Principal = Depends(current_principal),  # noqa: B008
) -> AuthorizationDecisionResponse:
    if request.principal.id != principal.id:
        raise HTTPException(status_code=403, detail="principal mismatch")
    decision = await LocalAuthorizationAdapter().authorize(
        AuthorizationRequest(
            principal=principal,
            action=request.action,
            resource=request.resource,
            context=request.context,
        )
    )
    return AuthorizationDecisionResponse(
        decision=decision.decision,
        decision_id=decision.decision_id,
        reason=decision.reason,
        policy_revision=decision.policy_revision,
        obligations=decision.obligations,
    )


@app.get("/v1/billing/overview", response_model=BillingOverviewResponse)
async def billing_overview(  # noqa: B008
    principal: Principal = Depends(current_principal),  # noqa: B008
) -> BillingOverviewResponse:
    adapter = LocalBillingAdapter()
    account = await adapter.get_account(principal)
    subscription = await adapter.get_subscription(account.id) if account else None
    return BillingOverviewResponse(
        account=BillingAccountResponse(
            id=account.id, owner_principal_id=account.owner_principal_id, provider=None
        )
        if account
        else None,
        subscription=SubscriptionResponse(
            id=subscription.id,
            billing_account_id=subscription.billing_account_id,
            plan_id=subscription.plan_id,
            status=subscription.status,
            provider=None,
        )
        if subscription
        else None,
    )
