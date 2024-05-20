from pydantic import BaseModel


class DeleteFileResponse(BaseModel):
    message: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "File deleted successfully",
                }
            ]
        }
    }
