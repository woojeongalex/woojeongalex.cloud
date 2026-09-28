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
from music_challenge.app.ports.output.audio_transcoder_port import AudioTranscoderPort
from music_challenge.app.ports.output.media_storage_port import MediaStoragePort
from music_challenge.app.use_cases.playback_copy import store_playback_copy
from music_challenge.app.use_cases.chart_result import to_chart_result
from music_challenge.domain.entities.chart_entity import ChallengeChart, ChartStatus
from music_challenge.domain.value_objects.chart_vo import MelodySource


class UploadStemsInteractor(UploadStemsUseCase):
    def __init__(
        self,
        challenge_repo: ChallengeRepositoryPort,
        chart_repo: ChartRepositoryPort,
        storage: MediaStoragePort,
        transcoder: AudioTranscoderPort,
    ) -> None:
        self._challenge_repo = challenge_repo
        self._chart_repo = chart_repo
        self._storage = storage
        self._transcoder = transcoder

    async def _put(
        self, challenge_id: int, role: str, stem: StemFile, played: bool = False
    ) -> str:
        key = f"music_challenge/stems/{challenge_id}/{uuid.uuid4()}_{role}_{stem.filename}"
        await self._storage.upload(key, stem.data, stem.content_type)
        # 멜로디 스템은 음정 추출에만 쓰고 들려주지 않으므로 재생용 사본이 필요 없다.
        if played:
            await store_playback_copy(self._storage, self._transcoder, key, stem.data)
        return key

    async def upload(self, command: UploadStemsCommand) -> UploadStemsResult:
        if not await self._challenge_repo.find_by_id(command.challenge_id):
            raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")

        # 보컬 멜로디에 악기 종류가 붙어 있으면 화면이 "피아노 멜로디"처럼 잘못 보인다.
        instrument = (
            command.instrument
            if command.melody_source == MelodySource.INSTRUMENT
            else None
        )

        existing = await self._chart_repo.find(command.challenge_id)
        melody_key = await self._put(command.challenge_id, "melody", command.melody)
        backing_key = (
            await self._put(
                command.challenge_id, "backing", command.backing, played=True
            )
            if command.backing
            else (existing.backing_s3_key if existing else None)
        )

        # 가사는 스템과 따로 관리하므로 스템을 다시 올려도 지우지 않는다.
        saved = await self._chart_repo.save(
            ChallengeChart(
                challenge_id=command.challenge_id,
                status=ChartStatus.PROCESSING,
                melody_source=command.melody_source,
                instrument=instrument,
                notes=[],
                duration=None,
                melody_s3_key=melody_key,
                backing_s3_key=backing_key,
                lyric_lines=existing.lyric_lines if existing else [],
                error=None,
                updated_at=datetime.utcnow(),
            )
        )
        chart = await to_chart_result(saved, self._storage)
        return UploadStemsResult(chart=chart, melody_key=melody_key)
