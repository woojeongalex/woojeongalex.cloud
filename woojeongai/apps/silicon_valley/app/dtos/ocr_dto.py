from dataclasses import dataclass


@dataclass(frozen=True)
class OcrCommand:
    filename: str
    content_type: str
    data: bytes


@dataclass(frozen=True)
class OcrResult:
    url: str
    key: str
    text: str
