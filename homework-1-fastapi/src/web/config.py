from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class WebSettings(BaseSettings):
    """Web-client configuration (env prefix ``WEB_``).

    ``api_base_url`` points at the JSON API's versioned prefix. Locally that is
    ``http://localhost:8000/api/v1``; in docker-compose the ``web`` service sets
    ``WEB_API_BASE_URL=http://api:8000/api/v1`` (service-to-service over the
    compose network).
    """

    model_config = SettingsConfigDict(env_prefix="WEB_", env_file=".env", extra="ignore")

    api_base_url: str = "http://localhost:8000/api/v1"
    request_timeout: float = 10.0

    # Auth is out of scope for this exercise, so "who is logged in" is simulated
    # by a cookie. This is the student shown until you switch via the profile
    # menu (top-right).
    default_student_id: int = 1

    app_name: str = "UniReg"
    # Offerings page size on the registration screen (server-side pagination).
    offerings_page_size: int = 10


@lru_cache
def get_web_settings() -> WebSettings:
    return WebSettings()
