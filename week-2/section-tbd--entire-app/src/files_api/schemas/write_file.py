# File: ./src/files_api/schemas/upload_file.py
from pydantic import (
    BaseModel,
    Field,
)


class FileUploadResponse(BaseModel):
    message: str = Field(..., example="File uploaded successfully")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "File uploaded successfully",
                }
            ]
        }
    }
