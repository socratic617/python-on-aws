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

    filePath: str
    last_modified: datetime
    size_bytes: int


class FileListResponse(BaseModel):
    files: List[FileMetadata]
    next_page_token: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "files": [
                        {"key": "file1.txt", "last_modified": "2023-01-01T00:00:00Z", "size_bytes": 12345},
                        {"key": "file2.txt", "last_modified": "2023-01-02T00:00:00Z", "size_bytes": 67890},
                    ],
                    "next_page_token": "some_token",
                }
            ]
        }
    }


class FileQueryParams(BaseModel):
    page_size: Optional[int] = Field(
        DEFAULT_PAGE_SIZE,
        json_schema_extra={
            "description": "Number of files to return per page",
            "minimum": 1,
            "example": 5,
        },
    )
    directory: Optional[str] = Field(
        DEFAULT_DIRECTORY,
        json_schema_extra={
            "description": "Directory to list files from",
            "example": "myfolder",
        },
    )
    page_token: Optional[str] = Field(
        None,
        json_schema_extra={
            "description": "Token for fetching the next page of results",
            "example": "some_token",
        },
    )

    # pylint: disable=no-self-argument
    @model_validator(mode="before")
    def check_mutually_exclusive(cls, values):
        page_token = values.get("page_token")
        directory = values.get("directory")
        if page_token:
            directory_is_default = directory == DEFAULT_DIRECTORY
            if not directory_is_default:
                raise ValueError("When page_token is provided, page_size must not be set.")
        return values

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "With page_token",
                    "description": "Fetches the next page using page_token.",
                    "value": {"page_token": "some_token"},
                },
                {
                    "summary": "With page_size only",
                    "description": "Fetches files with specified page_size.",
                    "value": {"page_size": 5},
                },
                {
                    "summary": "With directory only",
                    "description": "Fetches files from a specific directory.",
                    "value": {"directory": "my/folder"},
                },
                {
                    "summary": "With directory and page_size",
                    "description": "Fetches files from a specific directory with specified page_size.",
                    "value": {"directory": "my/folder", "page_size": 5},
                },
            ]
        }
    }
