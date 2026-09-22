"""리듬 게임 채보 — 조회, 생성 요청, 백그라운드 생성."""

import asyncio
import logging
import uuid
from dataclasses import replace
from datetime import datetime

from fastapi import HTTPException

from music_challenge.app.dtos.rhythm_dto import (
    RhythmChartResult,
    RhythmSheetResult,
    RhythmSheetSummary,
)
from music_challenge.app.ports.input.rhythm_use_case import (
    BuildRhythmChartUseCase,
    GetRhythmChartUseCase,
    RequestRhythmBuildUseCase,
)
from music_challenge.app.ports.output.challenge_repository_port import (
    ChallengeRepositoryPort,
)
from music_challenge.app.ports.output.media_storage_port import MediaStoragePort
from music_challenge.app.ports.output.rhythm_analyzer_port import RhythmAnalyzerPort
from music_challenge.app.ports.output.rhythm_repository_port import (
    RhythmChartRepositoryPort,
)
from music_challenge.domain.entities.chart_entity import ChartStatus
from music_challenge.domain.entities.rhythm_entity import RhythmChart
from music_challenge.domain.services.rhythm_pattern import build_all_sheets
from music_challenge.domain.value_objects.rhythm_vo import (
    RHYTHM_KEYS,
    RhythmDifficulty,
)

logger = logging.getLogger(__name__)

# 이보다 소리 시작 순간이 적으면 무음이거나 곡이 아닌 파일로 본다.
_MIN_ONSETS = 30


async def _load_challenge(repo: ChallengeRepositoryPort, challenge_id: int):
    challenge = await repo.find_by_id(challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")
    return challenge


def _summary(chart: RhythmChart | None, challenge_id: int, audio_url: str | None):
    if chart is None:
        return RhythmChartResult(
            challenge_id=challenge_id,
            status=ChartStatus.EMPTY,
            bpm=None,
            duration=None,
            audio_url=audio_url,
            sheets=[],
            error=None,
        )
    return RhythmChartResult(
        challenge_id=challenge_id,
        status=chart.status,
        bpm=chart.bpm,
        duration=chart.duration,
        audio_url=audio_url,
        sheets=[
            RhythmSheetSummary(
                keys=s.keys,
                difficulty=s.difficulty,
                level=s.level,
                note_count=len(s.notes),
            )
            for s in chart.sheets
        ],
        error=chart.error,
    )


class GetRhythmChartInteractor(GetRhythmChartUseCase):
    def __init__(
        self,
        challenge_repo: ChallengeRepositoryPort,
        rhythm_repo: RhythmChartRepositoryPort,
        storage: MediaStoragePort,
    ) -> None:
        self._challenge_repo = challenge_repo
        self._rhythm_repo = rhythm_repo
        self._storage = storage

    async def get(self, challenge_id: int) -> RhythmChartResult:
        challenge = await _load_challenge(self._challenge_repo, challenge_id)
        chart = await self._rhythm_repo.find(challenge_id)
        audio_url = await self._storage.presigned_url(challenge.music_s3_key)
        return _summary(chart, challenge_id, audio_url)

    async def get_sheet(
        self, challenge_id: int, keys: int, difficulty: RhythmDifficulty
    ) -> RhythmSheetResult:
        if keys not in RHYTHM_KEYS:
            raise HTTPException(status_code=422, detail="4키 또는 7키만 있습니다.")
        challenge = await _load_challenge(self._challenge_repo, challenge_id)
        chart = await self._rhythm_repo.find(challenge_id)
        sheet = chart.sheet(keys, difficulty) if chart else None
        if chart is None or chart.status != ChartStatus.READY or sheet is None:
            raise HTTPException(
                status_code=404, detail="이 곡은 아직 리듬 게임 채보가 없습니다."
            )
        return RhythmSheetResult(
            challenge_id=challenge_id,
            keys=keys,
            difficulty=difficulty,
            level=sheet.level,
            bpm=chart.bpm,
            duration=chart.duration,
            audio_url=await self._storage.presigned_url(challenge.music_s3_key),
            notes=sheet.notes,
        )


class RequestRhythmBuildInteractor(RequestRhythmBuildUseCase):
    def __init__(
        self,
        challenge_repo: ChallengeRepositoryPort,
        rhythm_repo: RhythmChartRepositoryPort,
        storage: MediaStoragePort,
    ) -> None:
        self._challenge_repo = challenge_repo
        self._rhythm_repo = rhythm_repo
        self._storage = storage

    async def request(self, challenge_id: int) -> tuple[RhythmChartResult, str, str]:
        challenge = await _load_challenge(self._challenge_repo, challenge_id)
        existing = await self._rhythm_repo.find(challenge_id)
        job_id = uuid.uuid4().hex
        # 다시 만드는 동안에도 이전 채보로 계속 플레이할 수 있게 채보는 남겨 둔다.
        saved = await self._rhythm_repo.save(
            RhythmChart(
                challenge_id=challenge_id,
                status=ChartStatus.PROCESSING,
                job_id=job_id,
                bpm=existing.bpm if existing else None,
                duration=existing.duration if existing else None,
                sheets=existing.sheets if existing else [],
                error=None,
                updated_at=datetime.utcnow(),
            )
        )
        audio_url = await self._storage.presigned_url(challenge.music_s3_key)
        return _summary(saved, challenge_id, audio_url), job_id, challenge.music_s3_key


class BuildRhythmChartInteractor(BuildRhythmChartUseCase):
    def __init__(
        self,
        rhythm_repo: RhythmChartRepositoryPort,
        storage: MediaStoragePort,
        analyzer: RhythmAnalyzerPort,
    ) -> None:
        self._rhythm_repo = rhythm_repo
        self._storage = storage
        self._analyzer = analyzer

    async def build(self, challenge_id: int, job_id: str, source_key: str) -> None:
        sheets = []
        bpm: float | None = None
        duration: float | None = None
        error: str | None = None
        try:
            audio = await self._storage.download(source_key)
            # 3분 곡에 10~20초 걸리는 CPU 작업이라 이벤트 루프를 막지 않게 한다.
            analysis = await asyncio.to_thread(self._analyzer.analyze, audio)
            del audio
            if len(analysis.onsets) < _MIN_ONSETS:
                error = "곡에서 박자를 거의 찾지 못했습니다. 무음이거나 너무 짧은 파일인지 확인해 주세요."
            else:
                sheets = build_all_sheets(analysis)
                bpm, duration = analysis.bpm, analysis.duration
        except Exception:
            logger.exception("리듬 채보 생성 실패 (challenge=%s)", challenge_id)
            error = "원곡을 읽지 못했습니다. WAV 또는 MP3 파일인지 확인해 주세요."

        current = await self._rhythm_repo.find(challenge_id)
        if current is None or current.job_id != job_id:
            logger.info(
                "더 새 생성 요청이 있어 결과를 버립니다 (challenge=%s)", challenge_id
            )
            return
        if error:
            # 실패해도 이전 채보가 있으면 그대로 두어 플레이가 끊기지 않게 한다.
            await self._rhythm_repo.save(
                replace(
                    current,
                    status=ChartStatus.READY if current.sheets else ChartStatus.FAILED,
                    error=error,
                    updated_at=datetime.utcnow(),
                )
            )
            return
        await self._rhythm_repo.save(
            replace(
                current,
                status=ChartStatus.READY,
                bpm=bpm,
                duration=duration,
                sheets=sheets,
                error=None,
                updated_at=datetime.utcnow(),
            )
        )
