"""BT3 web client entrypoint.

A separate FastAPI app (from the JSON API) that renders HTML with Jinja2 +
HTMX and calls the API over HTTP. Run locally with:

    uv run --extra web uvicorn web.main:app --reload --app-dir src

or as the ``web`` service in docker-compose.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from web.api_client import ApiClient
from web.config import get_web_settings
from web.routes import actions, pages


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_web_settings()
    async with httpx.AsyncClient(
        base_url=settings.api_base_url, timeout=settings.request_timeout
    ) as client:
        app.state.api = ApiClient(client)
        yield


def create_app() -> FastAPI:
    settings = get_web_settings()
    app = FastAPI(
        title=f"{settings.app_name} — web client",
        lifespan=lifespan,
        # This is a UI, not an API — no OpenAPI docs.
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    app.include_router(pages.router)
    app.include_router(actions.router)
    return app


app = create_app()
