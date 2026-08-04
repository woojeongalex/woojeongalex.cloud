from dataclasses import dataclass


@dataclass(frozen=True)
class S3ImageUploadCommand:
    filename: str
    content_type: str
    data: bytes


@dataclass(frozen=True)
class S3ImageUploadResult:
    url: str
    key: str
