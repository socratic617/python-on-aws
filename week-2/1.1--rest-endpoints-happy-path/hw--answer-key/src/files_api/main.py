from typing import (
    List,
    Optional,
)

from fastapi import (
    Depends,
    FastAPI,
    UploadFile,
    status,
)
from fastapi.responses import (
    JSONResponse,
    StreamingResponse,
)
from files_api.s3.delete_objects import delete_s3_object
from files_api.s3.read_objects import (
    fetch_s3_object,
    fetch_s3_objects_metadata,
    fetch_s3_objects_using_page_token,
    object_exists_in_s3,
)
from files_api.s3.write_objects import upload_s3_object
from pydantic import BaseModel

#####################
# --- Constants --- #
#####################


S3_BUCKET_NAME = "your-s3-bucket-name"

app = FastAPI()


####################################
# --- Request/response schemas --- #
####################################


class FileMetadata(BaseModel):
    filePath: str
    last_modified: str
    size_bytes: int


class FileListResponse(BaseModel):
    files: List[FileMetadata]
    next_page_token: Optional[str]


class FileQueryParams(BaseModel):
    page_size: int = 10
    directory: Optional[str] = ""
    page_token: Optional[str] = None


class DeleteFileResponse(BaseModel):
    message: str


@app.get("/files")
async def list_files(
    query_params: FileQueryParams = Depends(),  # noqa: B008
) -> FileListResponse:
    """List files with pagination."""
    if query_params.page_token:
        files, next_page_token = fetch_s3_objects_using_page_token(
            bucket_name=S3_BUCKET_NAME,
            continuation_token=query_params.page_token,
            max_keys=query_params.page_size,
        )
    else:
        files, next_page_token = fetch_s3_objects_metadata(
            bucket_name=S3_BUCKET_NAME,
            prefix=query_params.directory,
            max_keys=query_params.page_size,
        )

    file_metadata_objs = [
        FileMetadata(
            filePath=f"/{item['Key']}",
            last_modified=item["LastModified"],
            size_bytes=item["Size"],
        )
        for item in files
    ]
    return FileListResponse(files=file_metadata_objs, next_page_token=next_page_token if next_page_token else None)


@app.get("/files/{file_path:path}")
async def get_file(
    file_path: str,
):
    """Retrieve a file."""
    if object_exists_in_s3(S3_BUCKET_NAME, file_path):
        get_object_response = fetch_s3_object(S3_BUCKET_NAME, object_key=file_path)
        return StreamingResponse(
            content=get_object_response["Body"],
            media_type=get_object_response["ContentType"],
        )

    # HTTPException will be added later


@app.put("/files/{file_path:path}")
async def upload_file(
    file_path: str,
    file: UploadFile,
):
    """Upload a file."""
    file_bytes = await file.read()

    object_already_exists_at_path = object_exists_in_s3(S3_BUCKET_NAME, object_key=file_path)
    if object_already_exists_at_path:
        response = JSONResponse(
            content={"message": f"File overwritten: /{file_path}"},
            status_code=status.HTTP_200_OK,
        )
    else:
        response = JSONResponse(
            content={"message": f"File uploaded: /{file_path}"},
            status_code=status.HTTP_201_CREATED,
        )

    upload_s3_object(
        bucket_name=S3_BUCKET_NAME,
        object_key=file_path,
        file_content=file_bytes,
        content_type=file.content_type,
    )

    return response


@app.delete("/files/{file_path:path}")
async def delete_file(
    file_path: str,
) -> DeleteFileResponse:
    """Delete a file."""
    if object_exists_in_s3(S3_BUCKET_NAME, object_key=file_path):
        delete_s3_object(S3_BUCKET_NAME, object_key=file_path)
        return DeleteFileResponse(message=f"Deleted file: /{file_path}")

    # HTTPException will be added later


@app.head("/files/{file_path:path}")
async def get_file_metadata(
    file_path: str,
):
    """Retrieve file metadata."""
    if object_exists_in_s3(S3_BUCKET_NAME, file_path):
        get_object_response = fetch_s3_object(S3_BUCKET_NAME, object_key=file_path)
        return JSONResponse(
            headers={
                "Content-Type": get_object_response["ContentType"],
                "Content-Length": str(get_object_response["ContentLength"]),
                "Last-Modified": get_object_response["LastModified"].strftime("%a, %d %b %Y %H:%M:%S GMT"),
            }
        )

    # HTTPException will be added later


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
