from fastapi import (
    Request,
    status,
)
from fastapi.responses import JSONResponse
from pydantic import ValidationError


# pylint: disable=unused-argument
async def handle_errors_globally(request: Request, exc: Exception):
    """Handle any raised exceptions that were not handled by a more specific exception handler."""
    print("exception stack trace:", str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "error",
            "error_type": "500 Internal Server Error",
            "errors": str(exc),
        },
    )


# pylint: disable=unused-argument
async def handle_custom_pydantic_validation_errors(request: Request, exc: ValidationError):
    """Handle pydantic validation Errors that come from custom validators because FastAPI does not by default."""
    errors = exc.errors()
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "error",
            "error_type": "422 Unprocessable Entity",
            "errors": [err["msg"] for err in errors],
        },
    )
