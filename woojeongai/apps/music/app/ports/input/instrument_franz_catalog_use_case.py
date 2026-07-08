"""[Layer: Ports] 악기 카탈로그 입력 Port — 카탈로그 검색 (inbound → usecase)."""
from __future__ import annotations

from abc import ABC, abstractmethod

from music.adapter.inbound.api.schemas.instrument_franz_catalog_schema import FranzIntroduceSchema, FranzIntroduceResponse
from music.app.dtos.instrument_dto import InstrumentCatalogResultDto


class InstrumentCatalogUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: FranzIntroduceSchema) -> FranzIntroduceResponse:
        pass

    @abstractmethod
    def search(self, q: str = "") -> InstrumentCatalogResultDto:
        pass
