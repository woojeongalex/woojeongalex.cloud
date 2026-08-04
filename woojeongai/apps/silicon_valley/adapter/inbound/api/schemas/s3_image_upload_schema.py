from pydantic import BaseModel


class S3ImageUploadResponse(BaseModel):
    url: str
    key: str
