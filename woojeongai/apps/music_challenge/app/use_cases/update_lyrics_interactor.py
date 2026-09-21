from dataclasses import replace
from datetime import datetime

from fastapi import HTTPException

from music_challenge.app.dtos.chart_dto import ChartResult
from music_challenge.app.ports.input.chart_use_case import UpdateLyricsUseCase
from music_challenge.app.ports.output.challenge_repository_port import (
    ChallengeRepositoryPort,
)
from music_challenge.app.ports.output.chart_repository_port import ChartRepositoryPort
from music_challenge.app.ports.output.media_storage_port import MediaStoragePort
from music_challenge.app.use_cases.chart_result import to_chart_result
from music_challenge.domain.entities.chart_entity import ChallengeChart, ChartStatus
from music_challenge.domain.value_objects.chart_vo import LyricLine


def _validate(lines: list[LyricLine]) -> None:
    """타이밍이 찍힌 줄들은 시간 순서여야 한다. 아직 안 찍은 줄(None)은 건너뛴다."""
    last = -1.0
    for i, line in enumerate(lines, start=1):
        if line.start is None:
            continue
        if line.start < 0:
            raise HTTPException(
                status_code=422, detail=f"{i}번째 줄의 시간이 음수입니다."
            )
        if line.start < last:
            raise HTTPException(
                status_code=422,
                detail=f"{i}번째 줄의 시간이 앞 줄보다 빠릅니다. 순서대로 맞춰 주세요.",
            )
        last = line.start


class UpdateLyricsInteractor(UpdateLyricsUseCase):
    def __init__(
        self,
        challenge_repo: ChallengeRepositoryPort,
        chart_repo: ChartRepositoryPort,
        storage: MediaStoragePort,
    ) -> None:
        self._challenge_repo = challenge_repo
        self._chart_repo = chart_repo
        self._storage = storage

    async def update(self, challenge_id: int, lines: list[LyricLine]) -> ChartResult:
        if not await self._challenge_repo.find_by_id(challenge_id):
            raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")
        _validate(lines)

        existing = await self._chart_repo.find(challenge_id)
        # 스템보다 가사를 먼저 넣을 수도 있으므로 악보가 없으면 빈 악보를 만든다.
        base = existing or ChallengeChart(
            challenge_id=challenge_id,
            status=ChartStatus.EMPTY,
            notes=[],
            duration=None,
            vocal_s3_key=None,
            instrumental_s3_key=None,
            lyric_lines=[],
            error=None,
            updated_at=datetime.utcnow(),
        )
        saved = await self._chart_repo.save(
            replace(base, lyric_lines=lines, updated_at=datetime.utcnow())
        )
        return await to_chart_result(saved, challenge_id, self._storage)
