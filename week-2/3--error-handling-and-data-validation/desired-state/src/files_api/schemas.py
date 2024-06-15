####################################
# --- Request/response schemas --- #
####################################

from datetime import datetime
from typing import (
    List,
    Optional,
)

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)

DEFAULT_GET_FILES_DIRECTORY = ""


# read (cRud)
class FileMetadata(BaseModel):
    file_path: str
    last_modified: datetime
    size_bytes: int


# read (cRud)
class GetFilesResponse(BaseModel):
    files: List[FileMetadata]
    next_page_token: Optional[str]


# read (cRud)
class GetFilesQueryParams(BaseModel):
    page_size: int = Field(
        10,
        description="Number of files to return per page",
        gt=1,
        json_schema_extra={
            "example": 10,
        },
    )
    directory: Optional[str] = DEFAULT_GET_FILES_DIRECTORY
    page_token: Optional[str] = Field(
        None,
        description="Token for fetching the next page of results",
        json_schema_extra={
            "example": "some_token",
        },
    )

    # pylint: disable=no-self-argument
    @model_validator(mode="before")
    def check_mutually_exclusive(cls, values):
        page_token = values.get("page_token")
        directory = values.get("directory")
        if page_token:
            directory_is_default = directory == DEFAULT_GET_FILES_DIRECTORY
            if not directory_is_default:
                raise ValueError("When page_token is provided, page_size must not be set.")
        return values


# delete (cruD)
class DeleteFileResponse(BaseModel):
    message: str


# create/update (CrUd)
class PutFileResponse(BaseModel):
    """Response model for `PUT /files/:filePath`."""

    file_path: str
    """Docstring"""
    message: str = Field(..., description="A message describing the operation.")
