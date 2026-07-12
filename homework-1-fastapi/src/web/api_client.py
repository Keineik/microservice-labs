"""Thin async HTTP client for the JSON API.

Every screen goes through this class, so error translation lives in one place:
the API speaks RFC 7807 ``application/problem+json``, and we turn any 4xx/5xx
into an :class:`ApiError` carrying the human-readable ``title``/``detail`` that
the templates surface as a flash message.
"""

from typing import Any

import httpx


class ApiError(Exception):
    """A non-2xx response from the API, already parsed from problem+json."""

    def __init__(self, status_code: int, title: str, detail: str | None = None) -> None:
        self.status_code = status_code
        self.title = title
        self.detail = detail
        super().__init__(detail or title)

    @property
    def message(self) -> str:
        return self.detail or self.title


class ApiClient:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    def _raise(self, resp: httpx.Response) -> None:
        title, detail = resp.reason_phrase or "Request failed", None
        try:
            body = resp.json()
        except ValueError:
            body = None
        if isinstance(body, dict):
            title = body.get("title", title)
            detail = body.get("detail")
        raise ApiError(resp.status_code, title, detail)

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        # Drop None params so we don't send empty query values to the API.
        clean = {k: v for k, v in (params or {}).items() if v is not None}
        resp = await self._client.get(path, params=clean)
        if resp.is_error:
            self._raise(resp)
        return resp.json()

    async def post(
        self, path: str, json: dict[str, Any], headers: dict[str, str] | None = None
    ) -> Any:
        resp = await self._client.post(path, json=json, headers=headers)
        if resp.is_error:
            self._raise(resp)
        return resp.json() if resp.content else None

    async def delete(self, path: str) -> None:
        resp = await self._client.delete(path)
        if resp.is_error:
            self._raise(resp)
