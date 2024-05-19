import boto3
import botocore
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from fastapi.responses import StreamingResponse
from files_api.s3.delete_objects import delete_s3_object
from files_api.s3.read_objects import (
    fetch_s3_object,
    fetch_s3_objects_metadata,
    fetch_s3_objects_using_page_token,
    object_exists_in_s3,
)
from files_api.s3.write_objects import upload_s3_object
from files_api.schemas.delete_file import DeleteFileResponse
from files_api.schemas.list_files import (
    FileListResponse,
    FileMetadata,
)
from files_api.schemas.read_files import FileQueryParams
from files_api.schemas.write_file import FileUploadResponse
from files_api.settings import Settings
from pydantic import BaseModel

ROUTER = APIRouter()


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


@ROUTER.get("/files/", response_model=FileListResponse)
async def list_files(
    query_params: FileQueryParams = Depends(),
    settings: Settings = Depends(get_settings),
):
    """
    List files with pagination.
    """
    bucket_name = settings.s3_bucket_name

    if query_params.page_token:
        files, next_page_token = fetch_s3_objects_using_page_token(
            bucket_name=bucket_name,
            continuation_token=query_params.page_token,
            max_keys=query_params.page_size,
        )
    else:
        files, next_page_token = fetch_s3_objects_metadata(
            bucket_name=bucket_name,
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
    return FileListResponse(files=file_metadata_objs, next_page_token=next_page_token if next_page_token else None)


@ROUTER.get("/files/{file_path}")
async def get_file(
    file_path: str,
    settings: Settings = Depends(get_settings),
):
    """Retrieve a file."""
    bucket_name = settings.s3_bucket_name

    if object_exists_in_s3(bucket_name, file_path):
        get_object_response = fetch_s3_object(bucket_name=bucket_name, object_key=file_path)
        return StreamingResponse(
            content=get_object_response["Body"],
            media_type=get_object_response["ContentType"],
        )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found: {file_path}")


@ROUTER.post("/files/{file_path}")
async def upload_file(
    file_path: str,
    file: bytes = Depends(),
    settings: Settings = Depends(get_settings),
) -> FileUploadResponse:
    """Upload a file."""
    upload_s3_object(
        bucket_name=settings.s3_bucket_name,
        object_key=file_path,
        file_content=file,
    )
    return FileUploadResponse(message=f"File uploaded: {file_path}")


@ROUTER.delete("/files/{file_path}")
async def delete_file(
    file_path: str,
    settings: Settings = Depends(get_settings),
) -> DeleteFileResponse:
    """Delete a file."""

    if object_exists_in_s3(bucket_name=settings.s3_bucket_name, object_key=file_path):
        delete_s3_object(bucket_name=settings.s3_bucket_name, object_key=file_path)
        return DeleteFileResponse(message=f"Deleted file: {file_path}")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found: {file_path}")
