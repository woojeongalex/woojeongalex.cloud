from fastapi import APIRouter, Depends, Query

from music.adapter.inbound.api.mappers.music_inbound_mapper import to_instrument_catalog_response
from music.adapter.inbound.api.schemas.instrument_franz_catalog_schema import FranzIntroduceSchema, FranzIntroduceResponse, InstrumentCatalogResponse
from music.app.ports.input.instrument_franz_catalog_use_case import InstrumentCatalogUseCase
from music.adapter.inbound.api.deps.music_deps import get_instrument_catalog_use_case

instrument_franz_catalog_router = APIRouter(tags=["music-instrument"])


@instrument_franz_catalog_router.get("/api/music/franz/myself", response_model=FranzIntroduceResponse)
async def franz_introduce_myself(
    franz: InstrumentCatalogUseCase = Depends(get_instrument_catalog_use_case),
) -> FranzIntroduceResponse:
    return await franz.introduce_myself(FranzIntroduceSchema(id=4, name="악기 프란츠 (Franz)"))


@instrument_franz_catalog_router.get("/api/music/instrument-catalog", response_model=InstrumentCatalogResponse)
async def get_instrument_catalog(
    q: str = Query("", description="악기 검색어"),
    instrument: InstrumentCatalogUseCase = Depends(get_instrument_catalog_use_case),
) -> InstrumentCatalogResponse:
    return to_instrument_catalog_response(instrument.search(q))
