import logging

from fastapi import FastAPI, Request
from fastapi.responses import UJSONResponse

from huuva_backend.exceptions.exceptions import ConflictError, NotFoundError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Registers custom exception handlers for the FastAPI application."""

    @app.exception_handler(NotFoundError)
    async def not_found_exception_handler(
        request: Request,
        exc: NotFoundError,
    ) -> UJSONResponse:
        logger.error(f"NotFoundError: {exc}", exc_info=True)
        return UJSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ConflictError)
    async def conflict_exception_handler(
        request: Request,
        exc: ConflictError,
    ) -> UJSONResponse:
        """Handles ConflictError exceptions, logs them, and returns a 409 response."""
        logger.error(f"ConflictError: {exc}", exc_info=True)
        return UJSONResponse(status_code=409, content={"detail": exc.message})

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception,
    ) -> UJSONResponse:
        """Catches any unhandled exception, logs it, and returns a generic 500 error."""
        logger.error(f"Unhandled exception occurred: {exc}", exc_info=True)
        return UJSONResponse(
            status_code=500,
            content={"detail": "Internal server error. Please try again later."},
        )
