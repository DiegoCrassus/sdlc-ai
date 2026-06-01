"""Alert API error responses (ADR-008 / alerts.schema.json)."""

from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse


class AlertApiError(Exception):
    """Raised for alert endpoints; handled by register_alert_exception_handler."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        body: dict[str, Any] = {"error": {"code": code, "message": message}}
        if details is not None:
            body["error"]["details"] = details
        self.body = body
        super().__init__(message)


def register_alert_exception_handler(app) -> None:
    """Register AlertApiError handler on FastAPI app."""

    @app.exception_handler(AlertApiError)
    async def _handle_alert_api_error(_request, exc: AlertApiError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=exc.body)
