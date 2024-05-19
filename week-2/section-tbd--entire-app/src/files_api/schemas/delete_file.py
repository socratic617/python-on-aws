from pydantic import (
    BaseModel,
    Field,
)


class DeleteFileResponse(BaseModel):
    message: str = Field(..., example="File deleted successfully")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "File deleted successfully",
                }
            ]
        }
    }
