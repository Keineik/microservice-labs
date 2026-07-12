from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration.

    All values come from environment variables (prefix ``APP_``) or a local
    ``.env`` file. This is the 12-factor pattern: config lives in the
    environment, never hardcoded — the same ``Settings`` object is fed by a
    ``.env`` locally and by k8s ConfigMap/Secret env vars in a cluster.
    """

    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")

    # SQLAlchemy async URL (asyncpg driver).
    database_url: str = "postgresql+asyncpg://app:app@localhost:5432/enrollment"
    db_echo: bool = False

    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"
    api_v2_prefix: str = "/api/v2"

    app_name: str = "Enrollment API"
    app_version: str = "0.1.0"


@lru_cache
def get_settings() -> Settings:
    """Cached settings — importable and injectable via ``Depends(get_settings)``."""
    return Settings()
