from pydantic import BaseModel


class DeleteFileResponse(BaseModel):
    message: str
