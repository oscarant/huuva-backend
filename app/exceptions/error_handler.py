import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions.exceptions import ConflictError, NotFoundError

logger = logging.getLogger(__name__)


def register_exception_handlers(app) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_exception_handler(request: Request, exc: NotFoundError):
        logger.error(f"NotFoundError: {exc}", exc_info=True)
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ConflictError)
    async def conflict_exception_handler(request: Request, exc: ConflictError):
        logger.error(f"ConflictError: {exc}", exc_info=True)
        return JSONResponse(status_code=409, content={"detail": exc.message})

    # Global handler: catches any unhandled exception, logs it, and returns a generic 500 error response.
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception occurred: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error. Please try again later."},
        )
