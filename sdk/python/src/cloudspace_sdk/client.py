from typing import Any

import httpx

from .models import (
    AuthorizationCheckRequest,
    AuthorizationDecision,
    BillingOverview,
    CloudspaceError,
    Principal,
)


def _raise_for_error(response: httpx.Response) -> None:
    if response.is_success:
        return
    payload = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
    error = payload.get("error", {})
    raise CloudspaceError(
        code=error.get("code", "INTERNAL"),
        message=error.get("message", "Cloudspace request failed"),
        request_id=error.get("request_id", response.headers.get("x-request-id", "unknown")),
        status_code=response.status_code,
    )


class CloudspaceClient:
    """Synchronous client for Cloudspace-owned API contracts."""

    def __init__(self, base_url: str, access_token: str, client: httpx.Client | None = None) -> None:
        self._client = client or httpx.Client(base_url=base_url.rstrip("/"), timeout=5.0)
        self._client.headers["Authorization"] = f"Bearer {access_token}"

    def me(self) -> Principal:
        response = self._client.get("/v1/me")
        _raise_for_error(response)
        return Principal.model_validate(response.json()["principal"])

    def authorize(self, request: AuthorizationCheckRequest) -> AuthorizationDecision:
        response = self._client.post("/v1/authorization/check", json=request.model_dump())
        _raise_for_error(response)
        return AuthorizationDecision.model_validate(response.json())

    def billing_overview(self) -> BillingOverview:
        response = self._client.get("/v1/billing/overview")
        _raise_for_error(response)
        return BillingOverview.model_validate(response.json())

    def close(self) -> None:
        self._client.close()


class AsyncCloudspaceClient:
    """Async client for Cloudspace-owned API contracts."""

    def __init__(self, base_url: str, access_token: str, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(base_url=base_url.rstrip("/"), timeout=5.0)
        self._client.headers["Authorization"] = f"Bearer {access_token}"

    async def me(self) -> Principal:
        response = await self._client.get("/v1/me")
        _raise_for_error(response)
        return Principal.model_validate(response.json()["principal"])

    async def authorize(self, request: AuthorizationCheckRequest) -> AuthorizationDecision:
        response = await self._client.post("/v1/authorization/check", json=request.model_dump())
        _raise_for_error(response)
        return AuthorizationDecision.model_validate(response.json())

    async def billing_overview(self) -> BillingOverview:
        response = await self._client.get("/v1/billing/overview")
        _raise_for_error(response)
        return BillingOverview.model_validate(response.json())

    async def aclose(self) -> None:
        await self._client.aclose()
