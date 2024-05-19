from typing import Optional

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)

DEFAULT_PAGE_SIZE = 10
DEFAULT_DIRECTORY = ""


# pylint: disable=missing-class-docstring
class FileQueryParams(BaseModel):  # noqa: D101
    page_size: Optional[int] = Field(DEFAULT_PAGE_SIZE, description="Number of files to return per page", example=5)
    directory: Optional[str] = Field(DEFAULT_DIRECTORY, description="Directory to list files from", example="myfolder")
    page_token: Optional[str] = Field(
        None, description="Token for fetching the next page of results", example="some_token"
    )

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
                    "value": {"directory": "myfolder"},
                },
                {
                    "summary": "With directory and page_size",
                    "description": "Fetches files from a specific directory with specified page_size.",
                    "value": {"directory": "myfolder", "page_size": 5},
                },
            ]
        }
    }
