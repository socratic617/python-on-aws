import os
from typing import Annotated

from fastapi import (
    Depends,
    FastAPI,
    Request,
    status,
)
from fastapi.responses import JSONResponse
from files_api.schemas import (
    FileListResponse,
    FileMetadata,
    FileQueryParams,
)
from pydantic import ValidationError

try:
    pass
except ImportError:
    ...


APP = FastAPI(docs_url="/")


BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "unset")


@APP.get("/errors/")
async def raise_error():
    raise Exception("This is a test error.")


@APP.get("/files/")
async def list_files(query_params: Annotated[FileQueryParams, Depends()]) -> FileListResponse:
    """
    List files with pagination.

    - **page_size**: Number of files to return per page. Ignored if `page_token` is provided.
    - **directory**: Directory to list files from. Ignored if `page_token` is provided.
    - **page_token**: Token for fetching the next page of results where the last page left off.
      Respects `page_size`. Mutually exclusive with `directory`.

    Each request will return a pagination token that can be used to fetch the next page of results.
    """
    if query_params.page_token:
        files, next_page_token = fetch_s3_objects_using_page_token(
            bucket_name=BUCKET_NAME,
            continuation_token=query_params.page_token,
            max_keys=query_params.page_size,
        )
    else:
        files, next_page_token = fetch_s3_objects(
            bucket_name=BUCKET_NAME,
            prefix=query_params.directory,
            max_keys=query_params.page_size,
        )

    file_metadata_objs = [
        FileMetadata(
            key=item["Key"],
            last_modified=item["LastModified"],
            size_bytes=item["Size"],
        )
        for item in files
    ]
    return FileListResponse(
        files=file_metadata_objs,
        next_page_token=next_page_token if next_page_token else None,
    )


# pylint: disable=unused-argument
@APP.exception_handler(Exception)
async def handle_errors_globally(request: Request, exc: Exception):
    """Handle any raised exceptions that were not handled by a more specific exception handler."""
    # TODO: log level with trace ID
    print("exception:", str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "error",
            "error_type": "500 Internal Server Error",
            "errors": str(exc),
        },
    )


# pylint: disable=unused-argument
@APP.exception_handler(ValidationError)
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(APP, host="0.0.0.0", port=3000)
