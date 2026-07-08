from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from music.adapter.outbound.orm.vocal_maestro_analyzer_model import AiVocalAnalysisEntity, SingEvaluationEntity
from music.adapter.outbound.orm.vocal_mia_recorder_model import UserVocalRecordingEntity
from music.app.dtos.evaluation_dto import MiaIntroduceQuery, MiaIntroduceResponse, VocalEvaluationCreateCommand, VocalEvaluationResultDto
from music.app.ports.output.vocal_mia_maestro_port import EvaluationPort

logger = logging.getLogger(__name__)


class MiaRecorderPgRepository(EvaluationPort):
    """Command를 받아 3NF INSERT(세션 → 녹음 → AI 분석) 후 DTO 반환."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def introduce_myself(self, query: MiaIntroduceQuery) -> MiaIntroduceResponse:
        logger.info("[MUSIC][mia][5/repository] introduce_myself name=%s", query.name)
        return MiaIntroduceResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")

    async def save_evaluation_bundle(
        self, command: VocalEvaluationCreateCommand
    ) -> VocalEvaluationResultDto:
        db = self._session
        engine = "librosa" if command.input_source == "video" else "mic_demo"

        evaluation = SingEvaluationEntity(user_id=None)
        db.add(evaluation)
        await db.flush()
        eval_id = evaluation.id
        assert eval_id is not None

        vocal_recording = UserVocalRecordingEntity(
            sing_evaluation_id=eval_id,
            user_id=None,
            catalog_song_id=command.catalog_song_id,
            mr_search_list_id=command.mr_search_list_id,
            input_source=command.input_source,
            file_name=command.file_name or "",
            duration_sec=command.duration_sec,
        )
        db.add(vocal_recording)
        await db.flush()
        recording_id = vocal_recording.id
        assert recording_id is not None

        ai_analysis = AiVocalAnalysisEntity(
            user_vocal_recording_id=recording_id,
            analysis_engine=engine,
            pitch_score=command.pitch_score,
            rhythm_score=command.rhythm_score,
            vocal_grade=command.vocal_grade,
            summary=command.summary,
        )
        db.add(ai_analysis)
        await db.commit()
        await db.refresh(evaluation)
        await db.refresh(vocal_recording)
        await db.refresh(ai_analysis)
        logger.info(
            "[MUSIC][mia][5/repository] Neon INSERT eval=%s recording=%s ai=%s",
            evaluation.id,
            vocal_recording.id,
            ai_analysis.id,
        )
        return VocalEvaluationResultDto(id=eval_id)
