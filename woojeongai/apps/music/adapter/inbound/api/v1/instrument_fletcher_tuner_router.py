from fastapi import APIRouter, Depends

from music.adapter.inbound.api.schemas.instrument_fletcher_tuner_schema import FletcherIntroduceSchema, FletcherIntroduceResponse
from music.app.ports.input.instrument_fletcher_tuner_use_case import FletcherTunerUseCase
from music.adapter.inbound.api.deps.music_deps import get_fletcher_use_case

instrument_fletcher_tuner_router = APIRouter(tags=["music-instrument"])


@instrument_fletcher_tuner_router.get("/api/music/fletcher/myself", response_model=FletcherIntroduceResponse)
async def fletcher_introduce_myself(
    fletcher: FletcherTunerUseCase = Depends(get_fletcher_use_case),
) -> FletcherIntroduceResponse:
    return await fletcher.introduce_myself(FletcherIntroduceSchema(id=6, name="악기 플레처 (Fletcher)"))
