import asyncio
import logging
from dataclasses import replace
from datetime import datetime

from music_challenge.app.ports.input.chart_use_case import BuildChartUseCase
from music_challenge.app.ports.output.chart_repository_port import ChartRepositoryPort
from music_challenge.app.ports.output.melody_extractor_port import MelodyExtractorPort
from music_challenge.domain.entities.chart_entity import ChartStatus
from music_challenge.domain.value_objects.chart_vo import Note

logger = logging.getLogger(__name__)

# 이보다 음표가 적으면 보컬 스템이 아니거나 거의 무음인 파일로 본다.
_MIN_NOTES = 5


class BuildChartInteractor(BuildChartUseCase):
    def __init__(
        self,
        chart_repo: ChartRepositoryPort,
        extractor: MelodyExtractorPort,
    ) -> None:
        self._chart_repo = chart_repo
        self._extractor = extractor

    async def build(
        self, challenge_id: int, vocal_key: str, vocal_bytes: bytes
    ) -> None:
        notes: list[Note] = []
        duration: float | None = None
        error: str | None = None
        try:
            # pyin 은 3분 곡에 수십 초가 걸리는 CPU 작업이라 이벤트 루프를 막지 않게 한다.
            melody = await asyncio.to_thread(self._extractor.extract, vocal_bytes)
            notes, duration = melody.notes, melody.duration
            if len(notes) < _MIN_NOTES:
                error = (
                    "보컬에서 음정을 거의 찾지 못했습니다. 완성곡이 아니라 "
                    "보컬만 있는 스템 파일인지 확인해 주세요."
                )
        except Exception:
            logger.exception("정답 멜로디 추출 실패 (challenge=%s)", challenge_id)
            error = "오디오를 읽지 못했습니다. WAV 또는 MP3 파일인지 확인해 주세요."

        current = await self._chart_repo.find(challenge_id)
        if current is None or current.vocal_s3_key != vocal_key:
            logger.info(
                "더 새 스템이 올라와 추출 결과를 버립니다 (challenge=%s)", challenge_id
            )
            return

        await self._chart_repo.save(
            replace(
                current,
                status=ChartStatus.FAILED if error else ChartStatus.READY,
                notes=[] if error else notes,
                duration=duration,
                error=error,
                updated_at=datetime.utcnow(),
            )
        )
