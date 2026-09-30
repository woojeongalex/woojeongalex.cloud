from pydantic import BaseModel


class OcrResponse(BaseModel):
    url: str
    key: str
    text: str
