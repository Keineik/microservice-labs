"""RFC 7807 (Problem Details) error handling.

Every error leaves the API as ``application/problem+json`` with the standard
members: ``type``, ``title``, ``status``, ``detail``, ``instance``. Raise a
``ProblemException`` (or a subclass) from the service layer; the registered
handlers turn it — and FastAPI's own validation/HTTP errors — into that shape.
"""

from __future__ import annotations

from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

PROBLEM_MEDIA_TYPE = "application/problem+json"


class ProblemException(Exception):
    """Base application error rendered as an RFC 7807 document."""

    def __init__(
        self,
        *,
        status_code: int,
        title: str,
        detail: str | None = None,
        type_: str = "about:blank",
        **extra: Any,
    ) -> None:
        self.status_code = status_code
        self.title = title
        self.detail = detail
        self.type = type_
        self.extra = extra
        super().__init__(detail or title)


class NotFoundError(ProblemException):
    def __init__(self, detail: str, **extra: Any) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Resource not found",
            detail=detail,
            type_="https://httpstatuses.io/404",
            **extra,
        )


class ConflictError(ProblemException):
    def __init__(self, detail: str, **extra: Any) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title="Conflict",
            detail=detail,
            type_="https://httpstatuses.io/409",
            **extra,
        )


def _problem(
    request: Request,
    status_code: int,
    title: str,
    detail: str | None = None,
    type_: str = "about:blank",
    **extra: Any,
) -> JSONResponse:
    body: dict[str, Any] = {
        "type": type_,
        "title": title,
        "status": status_code,
        "instance": request.url.path,
    }
    if detail:
        body["detail"] = detail
    body.update(extra)
    return JSONResponse(status_code=status_code, content=body, media_type=PROBLEM_MEDIA_TYPE)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ProblemException)
    async def _handle_problem(request: Request, exc: ProblemException) -> JSONResponse:
        return _problem(request, exc.status_code, exc.title, exc.detail, exc.type, **exc.extra)

    @app.exception_handler(RequestValidationError)
    async def _handle_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _problem(
            request,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Validation failed",
            detail="The request did not pass validation.",
            type_="https://httpstatuses.io/422",
            errors=jsonable_encoder(exc.errors()),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _handle_http(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        phrase = (
            HTTPStatus(exc.status_code).phrase
            if exc.status_code in HTTPStatus._value2member_map_
            else "Error"
        )
        return _problem(request, exc.status_code, title=phrase, detail=str(exc.detail))

    @app.exception_handler(Exception)
    async def _handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        return _problem(
            request,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            title="Internal Server Error",
            detail="An unexpected error occurred.",
        )
