from pydantic import (
    BaseModel,
    Field,
)


class FileUploadResponse(BaseModel):
    message: str = Field(...)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "File uploaded successfully",
                }
            ]
        }
    }
