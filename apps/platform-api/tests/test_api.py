import json

import httpx
import jwt
import pytest
from app.adapters import OIDCAuthenticationAdapter, OPAAuthorizationAdapter
from app.config import Settings
from app.domain import AuthorizationRequest, Principal, PrincipalType
from app.main import app
from cryptography.hazmat.primitives.asymmetric import rsa
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


def _key_pair(kid: str):
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(private.public_key()))
    public["kid"] = kid
    return private, public


@pytest.mark.asyncio
async def test_oidc_validates_claims_and_normalizes_principal() -> None:
    private, public = _key_pair("key-1")
    settings = Settings(
        auth_mode="oidc",
        oidc_issuer="https://auth.example.test/",
        oidc_audience="cloudspace",
        oidc_jwks_url="https://auth.example.test/jwks",
    )
    transport = httpx.MockTransport(lambda _: httpx.Response(200, json={"keys": [public]}))
    async with httpx.AsyncClient(transport=transport) as client:
        adapter = OIDCAuthenticationAdapter(settings, client)
        token = jwt.encode(
            {
                "sub": "user-1",
                "iss": settings.oidc_issuer,
                "aud": settings.oidc_audience,
                "exp": 4102444800,
                "tenant_id": "tenant-a",
            },
            private,
            algorithm="RS256",
            headers={"kid": "key-1"},
        )
        principal = await adapter.authenticate(token)
    assert principal.id == "user-1"
    assert principal.tenant_id == "tenant-a"


@pytest.mark.asyncio
async def test_oidc_rejects_wrong_audience_and_expired_tokens() -> None:
    private, public = _key_pair("key-1")
    settings = Settings(
        auth_mode="oidc",
        oidc_issuer="https://auth.example.test/",
        oidc_audience="cloudspace",
        oidc_jwks_url="https://auth.example.test/jwks",
    )
    transport = httpx.MockTransport(lambda _: httpx.Response(200, json={"keys": [public]}))
    async with httpx.AsyncClient(transport=transport) as client:
        adapter = OIDCAuthenticationAdapter(settings, client)
        for audience, expiry in (("wrong", 4102444800), ("cloudspace", 1)):
            token = jwt.encode(
                {"sub": "user-1", "iss": settings.oidc_issuer, "aud": audience, "exp": expiry},
                private,
                algorithm="RS256",
                headers={"kid": "key-1"},
            )
            with pytest.raises(ValueError, match="invalid OIDC credentials"):
                await adapter.authenticate(token)


@pytest.mark.asyncio
async def test_oidc_refreshes_jwks_when_a_key_rotates() -> None:
    old_private, old_public = _key_pair("old")
    new_private, new_public = _key_pair("new")
    responses = iter(({"keys": [old_public]}, {"keys": [new_public]}))
    settings = Settings(
        auth_mode="oidc",
        oidc_issuer="https://auth.example.test/",
        oidc_audience="cloudspace",
        oidc_jwks_url="https://auth.example.test/jwks",
    )
    transport = httpx.MockTransport(lambda _: httpx.Response(200, json=next(responses)))
    async with httpx.AsyncClient(transport=transport) as client:
        adapter = OIDCAuthenticationAdapter(settings, client)
        for private, kid in ((old_private, "old"), (new_private, "new")):
            token = jwt.encode(
                {
                    "sub": "user-1",
                    "iss": settings.oidc_issuer,
                    "aud": settings.oidc_audience,
                    "exp": 4102444800,
                },
                private,
                algorithm="RS256",
                headers={"kid": kid},
            )
            assert (await adapter.authenticate(token)).id == "user-1"


@pytest.mark.asyncio
async def test_opa_adapter_translates_cloudspace_contract_and_reads_decision() -> None:
    settings = Settings(
        opa_url="http://opa.test",
        opa_decision_path="v1/data/private/allow",
    )
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured.update(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "result": {
                    "allow": True,
                    "decision_id": "dec_opa",
                    "reason": "entitled",
                    "policy_revision": "git-abc",
                    "obligations": [{"audit": True}],
                }
            },
        )

    principal = Principal("user-1", PrincipalType.USER, "issuer", "tenant-a")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        decision = await OPAAuthorizationAdapter(settings, client).authorize(
            AuthorizationRequest(
                principal,
                "billing.account.read",
                "billing-account:1",
                {"ip": "127.0.0.1"},
            )
        )
    assert decision.decision is True
    assert decision.policy_revision == "git-abc"
    assert captured["input"]["action"] == "billing.account.read"
    assert "private" not in captured["input"]
