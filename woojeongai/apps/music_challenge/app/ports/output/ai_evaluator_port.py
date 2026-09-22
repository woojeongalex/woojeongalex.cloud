from abc import ABC, abstractmethod

from music_challenge.app.ports.output.audio_analysis_port import AudioMetrics
from music_challenge.domain.services.karaoke_scoring import KaraokeScore
from music_challenge.domain.value_objects.music_challenge_vo import (
    ChallengeType,
    MediaType,
)


class AIEvaluatorPort(ABC):
    @abstractmethod
    async def evaluate(
        self,
        challenge_title: str,
        challenge_description: str,
        challenge_type: ChallengeType,
        media_bytes: bytes,
        media_type: MediaType,
        content_type: str,
        metrics: AudioMetrics | None,
        karaoke: KaraokeScore | None = None,
    ) -> tuple[int, str]:
        """종합 점수와 코칭 피드백을 돌려준다.

        karaoke 는 노래방·연주 모드에서 정답 음표와 맞춰 본 결과다. 주어지면
        점수는 호출 측이 이 값으로 덮어쓰므로, AI 는 코칭 피드백에 집중하면 된다.

        metrics 는 librosa 가 뽑은 객관 지표다. 주어지면 AI 가 그 수치를
        근거로 판단하게 해서 점수 편차를 줄인다. 영상 제출 등으로 분석이
        불가능하면 None 이며, 그 경우 오디오만으로 판단한다.
        """
