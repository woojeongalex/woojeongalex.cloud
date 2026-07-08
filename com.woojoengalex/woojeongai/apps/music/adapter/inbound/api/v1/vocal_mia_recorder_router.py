from fastapi import APIRouter, Depends

from music.adapter.inbound.api.mappers.music_inbound_mapper import from_evaluation_create, to_evaluation_response
from music.adapter.inbound.api.schemas.vocal_maestro_analyzer_schema import VocalEvaluationResponse
from music.adapter.inbound.api.schemas.vocal_mia_recorder_schema import MiaIntroduceSchema, MiaIntroduceResponse, VocalEvaluationCreateRequest
from music.app.ports.input.vocal_mia_recorder_use_case import EvaluationUseCase
from music.adapter.inbound.api.deps.music_deps import get_evaluation_use_case

vocal_mia_recorder_router = APIRouter(tags=["music-evaluation"])


@vocal_mia_recorder_router.get("/api/music/mia/myself", response_model=MiaIntroduceResponse)
async def mia_introduce_myself(
    mia: EvaluationUseCase = Depends(get_evaluation_use_case),
) -> MiaIntroduceResponse:
    return await mia.introduce_myself(MiaIntroduceSchema(id=2, name="보컬 미아 (Vocal Mia)"))


@vocal_mia_recorder_router.post("/api/music/sing-evaluation", response_model=VocalEvaluationResponse)
async def post_sing_evaluation(
    body: VocalEvaluationCreateRequest,
    evaluation: EvaluationUseCase = Depends(get_evaluation_use_case),
) -> VocalEvaluationResponse:
    return to_evaluation_response(await evaluation.upload(from_evaluation_create(body)))
