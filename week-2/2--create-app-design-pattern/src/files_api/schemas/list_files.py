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

DEFAULT_PAGE_SIZE = 10
DEFAULT_DIRECTORY = ""


class FileMetadata(BaseModel):
    """List item for a file returned by GET /files/."""

    key: str
    last_modified: datetime
    size_bytes: int


class FileListResponse(BaseModel):
    files: List[FileMetadata]
    next_page_token: Optional[str] = None


class FileQueryParams(BaseModel):
    page_size: Optional[int] = Field(
        DEFAULT_PAGE_SIZE,
        json_schema_extra={
            "minimum": 1,
        },
    )
    directory: Optional[str] = Field(
        DEFAULT_DIRECTORY,
    )
    page_token: Optional[str] = Field(None)

    # pylint: disable=no-self-argument
    @model_validator(mode="before")
    def check_mutually_exclusive(cls, values):
        """Validate that page_token and directory are not both set at the same time."""
        page_token = values.get("page_token")
        directory = values.get("directory")
        if page_token:
            directory_is_default = directory == DEFAULT_DIRECTORY
            if not directory_is_default:
                raise ValueError("When page_token is provided, page_size must not be set.")
        return values
