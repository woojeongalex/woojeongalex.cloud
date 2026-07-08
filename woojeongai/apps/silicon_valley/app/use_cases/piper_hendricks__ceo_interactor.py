from __future__ import annotations

from silicon_valley.app.dtos.piper_hendricks__ceo_dto import HendricksCeoQuery, HendricksCeoResponse
from silicon_valley.app.ports.input.piper_hendricks__ceo_use_case import HendricksCeoUseCase
from silicon_valley.app.ports.output.piper_hendricks__ceo_port import HendricksCeoPort


class HendricksCeoInteractor(HendricksCeoUseCase):
    def __init__(self, repository: HendricksCeoPort):
        self.repository = repository

    async def introduce_myself(self, request) -> HendricksCeoResponse:
        return await self.repository.introduce_myself(HendricksCeoQuery(
            id=request.id,
            name=request.name,
        ))

    async def get_company_status(self) -> dict:
        return {}
