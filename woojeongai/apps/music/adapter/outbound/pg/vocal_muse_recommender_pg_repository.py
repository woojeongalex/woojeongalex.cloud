from __future__ import annotations

import logging

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from music.adapter.outbound.orm.vocal_maestro_analyzer_model import AiVocalAnalysisEntity, SingEvaluationEntity
from music.adapter.outbound.orm.vocal_mia_recorder_model import UserVocalRecordingEntity
from music.adapter.outbound.orm.vocal_muse_recommender_model import VocalRecommendationEntity
from music.app.dtos.suggest_dto import (
    AiVocalAnalysisDto,
    MuseIntroduceQuery,
    MuseIntroduceResponse,
    SingEvaluationDto,
    VocalRecommendationResultDto,
    VocalRecommendationSaveCommand,
)
from music.app.ports.output.vocal_muse_recommender_port import SuggestPort

logger = logging.getLogger(__name__)


class MuseRecommenderPgRepository(SuggestPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def introduce_myself(self, query: MuseIntroduceQuery) -> MuseIntroduceResponse:
        logger.info("[MUSIC][muse][5/repository] introduce_myself name=%s", query.name)
        return MuseIntroduceResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")

    async def get_sing_evaluation_by_id(
        self, evaluation_id: int
    ) -> SingEvaluationDto | None:
        stmt = select(SingEvaluationEntity).where(SingEvaluationEntity.id == evaluation_id)
        entity = (await self._session.execute(stmt)).scalar_one_or_none()
        if entity is None:
            return None
        return SingEvaluationDto(id=entity.id)

    async def get_ai_analysis_for_sing_evaluation(
        self, sing_evaluation_id: int
    ) -> AiVocalAnalysisDto | None:
        stmt = (
            select(AiVocalAnalysisEntity)
            .join(
                UserVocalRecordingEntity,
                AiVocalAnalysisEntity.user_vocal_recording_id == UserVocalRecordingEntity.id,
            )
            .where(UserVocalRecordingEntity.sing_evaluation_id == sing_evaluation_id)
        )
        entity = (await self._session.execute(stmt)).scalar_one_or_none()
        return _to_ai_dto(entity) if entity else None

    async def get_ai_analysis_by_id(
        self, ai_analysis_id: int
    ) -> AiVocalAnalysisDto | None:
        stmt = select(AiVocalAnalysisEntity).where(AiVocalAnalysisEntity.id == ai_analysis_id)
        entity = (await self._session.execute(stmt)).scalar_one_or_none()
        return _to_ai_dto(entity) if entity else None

    async def save_recommendation(
        self, command: VocalRecommendationSaveCommand
    ) -> VocalRecommendationResultDto:
        row = VocalRecommendationEntity(
            sing_evaluation_id=command.sing_evaluation_id,
            ai_vocal_analysis_id=command.ai_vocal_analysis_id,
            vocalization_pattern=command.vocalization_pattern,
            recommended_genres=command.recommended_genres,
            recommended_songs=command.recommended_songs,
        )
        self._session.add(row)
        await self._session.commit()
        await self._session.refresh(row)
        logger.info(
            "[MUSIC][muse][5/repository] Neon INSERT vocal_recommendations id=%s "
            "for_evaluation=%s ai=%s",
            row.id,
            row.sing_evaluation_id,
            row.ai_vocal_analysis_id,
        )
        ai = await self.get_ai_analysis_by_id(command.ai_vocal_analysis_id)
        assert ai is not None
        return _to_result_dto(row, ai)

    async def get_latest_by_evaluation_id(
        self, sing_evaluation_id: int
    ) -> VocalRecommendationResultDto | None:
        stmt = (
            select(VocalRecommendationEntity)
            .where(VocalRecommendationEntity.sing_evaluation_id == sing_evaluation_id)
            .order_by(desc(VocalRecommendationEntity.created_at))
            .limit(1)
        )
        row = (await self._session.execute(stmt)).scalar_one_or_none()
        if row is None:
            return None
        ai = await self.get_ai_analysis_by_id(row.ai_vocal_analysis_id)
        assert ai is not None
        return _to_result_dto(row, ai)


def _to_ai_dto(e: AiVocalAnalysisEntity) -> AiVocalAnalysisDto:
    return AiVocalAnalysisDto(
        id=e.id,
        pitch_score=e.pitch_score,
        rhythm_score=e.rhythm_score,
        vocal_grade=e.vocal_grade,
        summary=e.summary,
    )


def _to_result_dto(
    row: VocalRecommendationEntity, ai: AiVocalAnalysisDto
) -> VocalRecommendationResultDto:
    return VocalRecommendationResultDto(
        id=row.id,
        sing_evaluation_id=row.sing_evaluation_id,
        pitch_score_snapshot=ai.pitch_score,
        rhythm_score_snapshot=ai.rhythm_score,
        vocal_grade_snapshot=ai.vocal_grade,
        vocalization_pattern=row.vocalization_pattern,
        recommended_genres=[str(x) for x in (row.recommended_genres or [])],
        recommended_songs=[str(x) for x in (row.recommended_songs or [])],
    )
