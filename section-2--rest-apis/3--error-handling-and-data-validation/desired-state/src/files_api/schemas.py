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
DEFAULT_GET_FILES_PAGE_SIZE = 10


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
    page_size: int = Field(DEFAULT_GET_FILES_PAGE_SIZE, gt=1)
    directory: Optional[str] = DEFAULT_GET_FILES_DIRECTORY
    page_token: Optional[str] = None

    # pylint: disable=no-self-argument
    @model_validator(mode="before")
    def check_mutually_exclusive(cls, values):
        page_token = values.get("page_token")
        if page_token:
            directory_and_page_size_are_set_to_default = (
                values["directory"] == DEFAULT_GET_FILES_DIRECTORY
                and values["page_size"] == DEFAULT_GET_FILES_PAGE_SIZE
            )
            if not directory_and_page_size_are_set_to_default:
                raise ValueError("When page_token is provided, page_size and directory must not be set.")
        return values


# delete (cruD)
class DeleteFileResponse(BaseModel):
    message: str


# create/update (CrUd)
class PutFileResponse(BaseModel):
    """Response model for `PUT /files/:filePath`."""

    file_path: str
    message: str
