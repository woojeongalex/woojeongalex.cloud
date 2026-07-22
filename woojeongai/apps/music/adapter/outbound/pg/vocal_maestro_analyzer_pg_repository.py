"""[Layer: Adapter Outbound] Maestro PG 레포지토리 — sing_evaluations + ai_vocal_analyses."""
from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from music.adapter.outbound.orm.vocal_maestro_analyzer_model import (
    AiVocalAnalysisEntity,
    SingEvaluationEntity,
)
from music.adapter.outbound.orm.vocal_mia_recorder_model import UserVocalRecordingEntity
from music.app.dtos.evaluation_dto import (
    MaestroAnalyzeResultDto,
    MaestroIntroduceQuery,
    MaestroIntroduceResponse,
)
from music.app.ports.output.vocal_maestro_analyzer_port import MaestroPort

logger = logging.getLogger(__name__)


class MaestroAnalyzerPgRepository(MaestroPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def introduce_myself(self, query: MaestroIntroduceQuery) -> MaestroIntroduceResponse:
        logger.info("[Maestro][repo] introduce name=%s", query.name)
        return MaestroIntroduceResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")

    async def save_analysis(
        self,
        user_id: int | None,
        input_source: str,
        file_name: str,
        duration_sec: int,
        catalog_song_id: str | None,
        mr_search_list_id: int | None,
        result: MaestroAnalyzeResultDto,
    ) -> int:
        # 1. 평가 세션 생성
        session_entity = SingEvaluationEntity(user_id=user_id)
        self._session.add(session_entity)
        await self._session.flush()  # id 획득

        # 2. 녹음 기록 생성
        recording = UserVocalRecordingEntity(
            user_id=user_id,
            sing_evaluation_id=session_entity.id,
            input_source=input_source,
            file_name=file_name,
            duration_sec=duration_sec,
            catalog_song_id=catalog_song_id,
            mr_search_list_id=mr_search_list_id,
            content_type="audio/wav",
        )
        self._session.add(recording)
        await self._session.flush()

        # 3. AI 분석 결과 저장
        analysis = AiVocalAnalysisEntity(
            user_vocal_recording_id=recording.id,
            analysis_engine="librosa-pyin",
            pitch_score=result.pitch_score,
            rhythm_score=result.rhythm_score,
            vocal_grade=result.vocal_grade,
            summary=result.summary,
        )
        self._session.add(analysis)
        await self._session.flush()
        await self._session.commit()

        logger.info(
            "[Maestro][repo] saved analysis_id=%d session_id=%d",
            analysis.id, session_entity.id,
        )
        return analysis.id  # type: ignore[return-value]
