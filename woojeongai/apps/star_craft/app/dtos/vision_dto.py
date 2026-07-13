from dataclasses import dataclass


@dataclass(frozen=True) # 생성 후 수정 불가하도록 설정
class VisionQuery:

    id: int   # 직관적인 타입 변경
    name: str

@dataclass(frozen=True) # 생성 후 수정 불가하도록 설정
class VisionResponse:

    id: int   # 직관적인 타입 변경
    name: str

@dataclass(frozen=True)
class VisionImageQuery:

    filename: str
    content_type: str
    size: int
    data: bytes

@dataclass(frozen=True)
class VisionImageResponse:

    filename: str
    content_type: str
    size: int
    message: str
    url: str
