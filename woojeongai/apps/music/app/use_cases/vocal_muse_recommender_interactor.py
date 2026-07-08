from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from music.domain.vocal_bard_searcher_catalog import VOCAL_CATALOG
from music.adapter.inbound.api.schemas.vocal_muse_recommender_schema import MuseIntroduceSchema, MuseIntroduceResponse
from music.app.dtos.suggest_dto import (
    AiVocalAnalysisDto,
    MuseIntroduceQuery,
    VocalRecommendationCreateCommand,
    VocalRecommendationResultDto,
    VocalRecommendationSaveCommand,
)
from music.app.ports.input.vocal_muse_recommender_use_case import SuggestUseCase
from music.app.ports.output.vocal_muse_recommender_port import SuggestPort

logger = logging.getLogger(__name__)


@dataclass
class _VocalRule:
    predicate: Callable[[int, int, str], bool]
    genres: list[str]
    song_keys: tuple[str, str]
    pattern: str

    def matches(self, pitch: int, rhythm: int, summary_lower: str) -> bool:
        return self.predicate(pitch, rhythm, summary_lower)


_VOCAL_RULES: list[_VocalRule] = [
    _VocalRule(
        predicate=lambda p, r, _: p >= 88 and r >= 88,
        genres=["발라드", "뮤지컬 넘버"],
        song_keys=("night_letter", "defying"),
        pattern=(
            "음정 안정성과 박자 정확도가 모두 높습니다. 감성 발라드와 뮤지컬 넘버로 "
            "호흡·발성 표현을 넓혀 보세요."
        ),
    ),
    _VocalRule(
        predicate=lambda p, r, _: p >= 75 and r >= 75,
        genres=["발라드", "어쿠스틱 팝"],
        song_keys=("night_letter", "spring"),
        pattern="음정·박자 균형이 안정적인 편입니다. 서정적인 장르에서 발성 패턴을 다듬기 좋습니다.",
    ),
    _VocalRule(
        predicate=lambda p, _, s: p >= 60 or "호흡" in s or "발성" in s,
        genres=["R&B", "발라드"],
        song_keys=("spring", "night_letter"),
        pattern="리듬·감성 표현을 보완하면 좋습니다. 짧은 구간 위주로 음정·박자를 맞춰 보세요.",
    ),
    _VocalRule(
        predicate=lambda p, r, s: True,
        genres=["팝", "어쿠스틱"],
        song_keys=("spring", "defying"),
        pattern="연습량을 늘리며 음정 구간을 나눠 연습해 보세요. 장르별 발성 루틴을 추천합니다.",
    ),
]


def _resolve_catalog_songs() -> dict[str, str]:
    titles = [i.title for i in VOCAL_CATALOG]
    return {
        "night_letter": next((t for t in titles if "밤편지" in t), titles[1]),
        "defying": next((t for t in titles if "Defying" in t or "Gravity" in t), "Defying Gravity"),
        "spring": next((t for t in titles if "봄" in t), titles[0]),
    }


def _compose_recommendation(
    ai: AiVocalAnalysisDto,
) -> tuple[list[str], list[str], str]:
    pitch = ai.pitch_score
    rhythm = ai.rhythm_score
    summary_lower = (ai.summary or "").lower()
    catalog_songs = _resolve_catalog_songs()

    for rule in _VOCAL_RULES:
        if rule.matches(pitch, rhythm, summary_lower):
            songs = [catalog_songs[k] for k in rule.song_keys]
            return rule.genres, songs, rule.pattern

    raise RuntimeError("추천 규칙을 찾을 수 없습니다.")


class MuseRecommenderInteractor(SuggestUseCase):
    def __init__(self, repository: SuggestPort) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: MuseIntroduceSchema) -> MuseIntroduceResponse:
        return await self.repository.introduce_myself(MuseIntroduceQuery(id=schema.id, name=schema.name))

    async def upload(
        self, command: VocalRecommendationCreateCommand
    ) -> VocalRecommendationResultDto:
        '''Muse의 보컬 추천 생성·저장'''
        row = await self.repository.get_sing_evaluation_by_id(command.sing_evaluation_id)
        if row is None:
            raise ValueError("해당 보컬 평가가 없습니다.")

        ai = await self.repository.get_ai_analysis_for_sing_evaluation(row.id)
        if ai is None:
            raise ValueError("해당 평가에 대한 AI 분석 결과가 없습니다.")

        genres, songs, pattern = _compose_recommendation(ai)
        save_command = VocalRecommendationSaveCommand(
            sing_evaluation_id=row.id,
            ai_vocal_analysis_id=ai.id,
            vocalization_pattern=pattern,
            recommended_genres=genres,
            recommended_songs=songs,
        )
        result = await self.repository.save_recommendation(save_command)
        logger.info(
            "[MUSIC][muse][4/interactor] 추천 저장 id=%s evaluation_id=%s genres=%s",
            result.id,
            result.sing_evaluation_id,
            genres,
        )
        return result

    async def read(
        self, sing_evaluation_id: int
    ) -> VocalRecommendationResultDto | None:
        '''Muse의 최신 추천 조회'''
        return await self.repository.get_latest_by_evaluation_id(sing_evaluation_id)
