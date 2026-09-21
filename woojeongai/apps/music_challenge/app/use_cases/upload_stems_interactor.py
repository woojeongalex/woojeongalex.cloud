import uuid
from datetime import datetime

from fastapi import HTTPException

from music_challenge.app.dtos.chart_dto import (
    StemFile,
    UploadStemsCommand,
    UploadStemsResult,
)
from music_challenge.app.ports.input.chart_use_case import UploadStemsUseCase
from music_challenge.app.ports.output.challenge_repository_port import (
    ChallengeRepositoryPort,
)
from music_challenge.app.ports.output.chart_repository_port import ChartRepositoryPort
from music_challenge.app.ports.output.media_storage_port import MediaStoragePort
from music_challenge.app.use_cases.chart_result import to_chart_result
from music_challenge.domain.entities.chart_entity import ChallengeChart, ChartStatus


class UploadStemsInteractor(UploadStemsUseCase):
    def __init__(
        self,
        challenge_repo: ChallengeRepositoryPort,
        chart_repo: ChartRepositoryPort,
        storage: MediaStoragePort,
    ) -> None:
        self._challenge_repo = challenge_repo
        self._chart_repo = chart_repo
        self._storage = storage

    async def _put(self, challenge_id: int, role: str, stem: StemFile) -> str:
        key = f"music_challenge/stems/{challenge_id}/{uuid.uuid4()}_{role}_{stem.filename}"
        await self._storage.upload(key, stem.data, stem.content_type)
        return key

    async def upload(self, command: UploadStemsCommand) -> UploadStemsResult:
        if not await self._challenge_repo.find_by_id(command.challenge_id):
            raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")

        existing = await self._chart_repo.find(command.challenge_id)
        vocal_key = await self._put(command.challenge_id, "vocal", command.vocal)
        instrumental_key = (
            await self._put(command.challenge_id, "instrumental", command.instrumental)
            if command.instrumental
            else (existing.instrumental_s3_key if existing else None)
        )

        # 가사는 스템과 따로 관리하므로 스템을 다시 올려도 지우지 않는다.
        saved = await self._chart_repo.save(
            ChallengeChart(
                challenge_id=command.challenge_id,
                status=ChartStatus.PROCESSING,
                notes=[],
                duration=None,
                vocal_s3_key=vocal_key,
                instrumental_s3_key=instrumental_key,
                lyric_lines=existing.lyric_lines if existing else [],
                error=None,
                updated_at=datetime.utcnow(),
            )
        )
        chart = await to_chart_result(saved, command.challenge_id, self._storage)
        return UploadStemsResult(chart=chart, vocal_key=vocal_key)
