from fastapi import HTTPException

from music_challenge.app.dtos.chart_dto import ChartResult
from music_challenge.app.ports.input.chart_use_case import GetChartUseCase
from music_challenge.app.ports.output.challenge_repository_port import (
    ChallengeRepositoryPort,
)
from music_challenge.app.ports.output.chart_repository_port import ChartRepositoryPort
from music_challenge.app.ports.output.media_storage_port import MediaStoragePort
from music_challenge.app.use_cases.chart_result import to_chart_result


class GetChartInteractor(GetChartUseCase):
    def __init__(
        self,
        challenge_repo: ChallengeRepositoryPort,
        chart_repo: ChartRepositoryPort,
        storage: MediaStoragePort,
    ) -> None:
        self._challenge_repo = challenge_repo
        self._chart_repo = chart_repo
        self._storage = storage

    async def get(self, challenge_id: int) -> ChartResult:
        if not await self._challenge_repo.find_by_id(challenge_id):
            raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")
        chart = await self._chart_repo.find(challenge_id)
        return await to_chart_result(chart, challenge_id, self._storage)
