import os
from typing import (
    Annotated,
    Optional,
)

import boto3
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
    from mypy_boto3_s3 import S3Client
except ImportError:
    ...


APP = FastAPI(docs_url="/")


BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "unset")


def fetch_s3_objects_using_page_token(
    bucket_name: str,
    continuation_token: str,
    max_keys: Optional[int] = None,
    s3_client: Optional["S3Client"] = None,
) -> tuple[list[FileMetadata], Optional[str]]:
    s3_client = s3_client or boto3.client("s3")
    response = s3_client.list_objects_v2(Bucket=bucket_name, ContinuationToken=continuation_token, MaxKeys=max_keys)
    files = [
        FileMetadata(key=item["Key"], last_modified=item["LastModified"], size_bytes=item["Size"])
        for item in response.get("Contents", [])
    ]
    next_continuation_token: str | None = response.get("NextContinuationToken")

    return files, next_continuation_token


def fetch_s3_objects(
    bucket_name: str,
    prefix: Optional[str] = None,
    max_keys: Optional[int] = None,
    s3_client: Optional["S3Client"] = None,
) -> tuple[list[FileMetadata], Optional[str]]:
    s3_client = s3_client or boto3.client("s3")
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix, MaxKeys=max_keys)
    files = [
        FileMetadata(key=item["Key"], last_modified=item["LastModified"], size_bytes=item["Size"])
        for item in response.get("Contents", [])
    ]
    next_page_token: str | None = response.get("NextContinuationToken")

    return files, next_page_token


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
    """
    # try:
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

    return FileListResponse(
        files=files,
        next_page_token=next_page_token if next_page_token else None,
    )
    # except Exception as err:
    #     # TODO: place request ID in the exception and say "Please contact support with this ID".
    #     # TODO: do not expose the exact underlying error message to the user, to expose as few
    #     #       of the underlying implementation details not relevant to the interface/contract as possible.
    #     raise HTTPException(status_code=500, detail="Internal server error: " + str(err))


@APP.exception_handler(Exception)
async def handle_errors_globally(request: Request, exc: Exception):
    # log the exception
    print("exception:", str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "error",
            "error_type": "500 Internal Server Error",
            "errors": str(exc),
        },
    )


@APP.exception_handler(ValidationError)
async def handle_custom_pydantic_validation_errors(request: Request, exc: ValidationError):
    """"""
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
