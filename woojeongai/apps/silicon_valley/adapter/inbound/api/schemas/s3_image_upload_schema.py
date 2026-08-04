from pydantic import BaseModel


class S3ImageUploadResponse(BaseModel):
    url: str
    key: str


class OcrResponse(BaseModel):
    url: str
    key: str
    text: str
