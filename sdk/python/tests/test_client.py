import httpx
import pytest
from cloudspace_sdk import (
    AsyncCloudspaceClient,
    AuthorizationCheckRequest,
    CloudspaceClient,
    Principal,
)


def transport(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/v1/me":
        return httpx.Response(200, json={"principal": {"id": "u1", "type": "user", "issuer": "issuer"}})
    return httpx.Response(403, json={"error": {"code": "AUTHORIZATION_DENIED", "message": "No", "request_id": "req_1"}})


def test_sync_client_uses_contract_models() -> None:
    with httpx.Client(base_url="https://cloudspace.test", transport=httpx.MockTransport(transport)) as http:
        client = CloudspaceClient("https://cloudspace.test", "token", http)
        assert client.me() == Principal(id="u1", type="user", issuer="issuer")


@pytest.mark.asyncio
async def test_async_client_surfaces_structured_errors() -> None:
    async with httpx.AsyncClient(base_url="https://cloudspace.test", transport=httpx.MockTransport(transport)) as http:
        client = AsyncCloudspaceClient("https://cloudspace.test", "token", http)
        with pytest.raises(Exception, match="No"):
            await client.authorize(
                AuthorizationCheckRequest(
                    principal=Principal(id="u1", type="user", issuer="issuer"),
                    action="billing.account.read",
                    resource="billing-account:1",
                )
            )
