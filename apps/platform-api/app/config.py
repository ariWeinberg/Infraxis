from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CLOUDSPACE_", env_file=".env", extra="ignore")

    environment: str = "dev"
    service_name: str = "platform-api"
    auth_mode: str = "local"
    authorization_mode: str = "local"
    database_url: str = "sqlite+aiosqlite:///./cloudspace.db"
    oidc_issuer: str = "https://authentik.example.invalid/application/o/cloudspace/"
    oidc_audience: str = "cloudspace-platform"
    oidc_jwks_url: str | None = None
    opa_url: str = "http://opa:8181"
    opa_decision_path: str = "v1/data/cloudspace/authorization/allow"
    stripe_secret_key: str | None = Field(default=None, repr=False)
    stripe_webhook_secret: str | None = Field(default=None, repr=False)
    request_timeout_seconds: float = 3.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
