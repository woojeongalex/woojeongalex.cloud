from fastapi import APIRouter, Depends, HTTPException, Query

from music.adapter.inbound.api.mappers.music_inbound_mapper import from_suggest_create, to_suggest_response
from music.adapter.inbound.api.schemas.vocal_muse_recommender_schema import (
    MuseIntroduceSchema,
    MuseIntroduceResponse,
    VocalRecommendationCreateRequest,
    VocalRecommendationResponse,
)
from music.app.ports.input.vocal_muse_recommender_use_case import SuggestUseCase
from music.adapter.inbound.api.deps.music_deps import get_suggest_use_case

vocal_muse_recommender_router = APIRouter(tags=["music-suggest"])


@vocal_muse_recommender_router.get("/api/music/muse/myself", response_model=MuseIntroduceResponse)
async def muse_introduce_myself(
    muse: SuggestUseCase = Depends(get_suggest_use_case),
) -> MuseIntroduceResponse:
    return await muse.introduce_myself(MuseIntroduceSchema(id=3, name="보컬 뮤즈 (Vocal Muse)"))


@vocal_muse_recommender_router.post("/api/music/vocal-recommendations", response_model=VocalRecommendationResponse)
async def post_vocal_recommendations(
    body: VocalRecommendationCreateRequest,
    suggest: SuggestUseCase = Depends(get_suggest_use_case),
) -> VocalRecommendationResponse:
    return to_suggest_response(await suggest.upload(from_suggest_create(body)))


@vocal_muse_recommender_router.get("/api/music/vocal-recommendations", response_model=VocalRecommendationResponse)
async def get_vocal_recommendations(
    singEvaluationId: int = Query(
        ...,
        ge=1,
        alias="singEvaluationId",
        description="sing_evaluations.id",
    ),
    suggest: SuggestUseCase = Depends(get_suggest_use_case),
) -> VocalRecommendationResponse:
    dto = await suggest.read(singEvaluationId)
    if dto is None:
        raise HTTPException(status_code=404, detail="해당 분석에 대한 추천이 없습니다. 먼저 POST로 생성하세요.")
    return to_suggest_response(dto)
