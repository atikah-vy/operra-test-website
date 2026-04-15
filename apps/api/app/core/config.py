"""Environment configuration (Pydantic Settings)."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core
    environment: str = Field(default="development")
    api_prefix: str = Field(default="/api/v1")
    cors_origins: str = Field(default="http://localhost:3000")

    # Database (Neon Postgres, async driver)
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/operra",
        description="SQLAlchemy async URL (postgresql+asyncpg://…).",
    )

    # Redis / ARQ
    redis_url: str = Field(default="redis://localhost:6379/0")

    # Clerk
    clerk_secret_key: str = Field(default="")
    clerk_publishable_key: str = Field(default="")
    clerk_jwks_url: str = Field(
        default="",
        description="https://<frontend-api>/.well-known/jwks.json",
    )
    clerk_issuer: str = Field(
        default="",
        description="Usually https://<frontend-api>",
    )
    clerk_webhook_signing_secret: str = Field(default="")

    # Default org for public lead submissions (marketing site)
    public_lead_org_slug: str = Field(default="default")

    # Integrations (optional — adapters no-op when absent)
    attio_api_key: str = Field(default="")
    attio_webhook_secret: str = Field(default="")
    attio_workspace_id: str = Field(default="")
    apollo_api_key: str = Field(default="")
    metricool_api_token: str = Field(default="")
    metricool_user_id: str = Field(default="")
    bukku_api_key: str = Field(default="")
    bukku_company_id: str = Field(default="")
    calcom_api_key: str = Field(default="")
    calcom_webhook_secret: str = Field(default="")
    meta_app_secret: str = Field(default="")
    meta_verify_token: str = Field(default="")
    meta_page_access_token: str = Field(default="")
    meta_ig_business_id: str = Field(default="")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_prod(self) -> bool:
        return self.environment == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
