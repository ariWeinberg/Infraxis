import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as value:
        yield value


@pytest.mark.asyncio
async def test_liveness(client: AsyncClient) -> None:
    assert (await client.get("/health/live")).status_code == 200


@pytest.mark.asyncio
async def test_me_normalizes_identity(client: AsyncClient) -> None:
    response = await client.get("/v1/me", headers={"Authorization": "Bearer dev-user-alice"})
    assert response.status_code == 200
    assert response.json()["principal"]["id"] == "alice"
    assert "provider" not in response.json()["principal"]


@pytest.mark.asyncio
async def test_me_rejects_missing_credentials(client: AsyncClient) -> None:
    response = await client.get("/v1/me")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


@pytest.mark.asyncio
async def test_authorization_is_fail_closed_for_wrong_resource(client: AsyncClient) -> None:
    headers = {"Authorization": "Bearer dev-user-alice"}
    payload = {
        "principal": {
            "id": "alice",
            "type": "user",
            "issuer": "https://authentik.example.invalid/application/o/cloudspace/",
            "tenant_id": "tenant-dev",
        },
        "action": "billing.account.read",
        "resource": "billing-account:other-tenant",
    }
    response = await client.post("/v1/authorization/check", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["decision"] is False


@pytest.mark.asyncio
async def test_billing_does_not_expose_provider_objects(client: AsyncClient) -> None:
    response = await client.get(
        "/v1/billing/overview", headers={"Authorization": "Bearer dev-user-alice"}
    )
    assert response.status_code == 200
    assert response.json()["account"]["id"].startswith("billacct_")
