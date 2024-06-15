from pydantic import (
    BaseModel,
    ConfigDict,
)


class DeleteFileResponse(BaseModel):
    message: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "message": "File deleted successfully",
                }
            ]
        },
    )
