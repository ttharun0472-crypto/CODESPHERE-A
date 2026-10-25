import logging
import traceback

from fastapi.exceptions import RequestValidationError
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
):
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "success": False,
            "message": exc.detail
        }
    )


async def request_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = [
        {
            "type": error.get("type"),
            "loc": error.get("loc"),
            "msg": error.get("msg"),
        }
        for error in exc.errors()
    ]
    logger.warning(
        "Request validation failed; path=%s error_types=%s",
        request.url.path,
        ",".join(str(error["type"]) for error in errors),
    )
    return JSONResponse(
        status_code=422,
        content={"detail": errors},
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
):
    logger.error(
        "Unhandled request error; path=%s error_type=%s\n%s",
        request.url.path,
        type(exc).__name__,
        "".join(traceback.format_tb(exc.__traceback__)),
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error"
        }
    )