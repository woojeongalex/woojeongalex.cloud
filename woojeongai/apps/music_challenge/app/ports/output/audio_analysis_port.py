from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class AudioMetrics:
    """오디오에서 기계적으로 뽑아낸 객관 지표.

    같은 파일이면 항상 같은 값이 나온다. Gemini 단독 채점이 동일 입력에
    0~70점으로 흔들리던 문제를 잡기 위한 기준점이다.
    """

    pitch_score: int  # 음정 안정성 0~100 (변동계수 기반)
    rhythm_score: int  # 박자 일관성 0~100 (비트 간격 편차 기반)
    tempo: float  # BPM
    mean_hz: float
    std_hz: float
    duration: float


class AudioAnalysisPort(ABC):
    @abstractmethod
    def analyze(self, audio_bytes: bytes, content_type: str) -> AudioMetrics | None:
        """CPU-bound 동기 분석. 호출 측에서 asyncio.to_thread 로 위임한다.

        디코딩할 수 없는 입력(영상 등)이면 None 을 돌려준다 — 분석 실패가
        제출 자체를 막아서는 안 된다.
        """
