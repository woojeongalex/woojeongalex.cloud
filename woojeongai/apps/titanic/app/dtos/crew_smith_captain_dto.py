from dataclasses import dataclass


@dataclass(frozen=True)
class SmithCaptainQuery:
    id: int
    name: str


@dataclass(frozen=True)
class SmithCaptainResponse:
    """
    [유형 A] 통계 조회 → type="STATISTICS", accuracy=None
    [유형 B] ML 예측   → type="PREDICTION", accuracy=검증세트_실측값
    """
    status: str                 # "success" | "error"
    type: str                   # "STATISTICS" | "PREDICTION"
    message: str                # 사용자에게 전달할 답변 텍스트
    accuracy: float | None = None   # [유형 B]에만 채워짐
    graph: str | None = None        # [유형 B] base64 PNG, [유형 A]는 None
