from fastapi import APIRouter, Depends

from music.adapter.inbound.api.schemas.vocal_maestro_analyzer_schema import MaestroIntroduceSchema, MaestroIntroduceResponse
from music.app.ports.input.vocal_maestro_analyzer_use_case import MaestroAnalyzerUseCase
from music.adapter.inbound.api.deps.music_deps import get_maestro_use_case

vocal_maestro_analyzer_router = APIRouter(tags=["music-evaluation"])


@vocal_maestro_analyzer_router.get("/api/music/maestro/myself", response_model=MaestroIntroduceResponse)
async def maestro_introduce_myself(
    maestro: MaestroAnalyzerUseCase = Depends(get_maestro_use_case),
) -> MaestroIntroduceResponse:
    return await maestro.introduce_myself(MaestroIntroduceSchema(id=3, name="보컬 마에스트로 (Maestro)"))
