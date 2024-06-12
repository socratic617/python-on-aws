"""Entrypoint for this project."""

from fastapi import FastAPI
from files_api.errors import (
    handle_custom_pydantic_validation_errors,
    handle_errors_globally,
)
from files_api.routes import ROUTER
from files_api.settings import Settings
from pydantic import ValidationError


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()

    app = FastAPI(
        docs_url="/",
        title="Files API",
        version="v1",
        summary="API for storing and retrieving files of arbitrary types.",
    )

    # Store settings in the app instance for access in routes
    app.state.settings = settings

    app.include_router(ROUTER)

    app.add_exception_handler(
        exc_class_or_status_code=Exception,
        handler=handle_errors_globally,
    )
    app.add_exception_handler(
        exc_class_or_status_code=ValidationError,
        handler=handle_custom_pydantic_validation_errors,
    )

    return app


if __name__ == "__main__":
    import uvicorn

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=3000)
