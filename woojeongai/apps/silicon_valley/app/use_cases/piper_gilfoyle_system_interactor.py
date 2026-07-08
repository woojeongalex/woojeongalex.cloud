from __future__ import annotations

from silicon_valley.app.dtos.piper_gilfoyle_system_dto import GilfoyleSystemQuery, GilfoyleSystemResponse
from silicon_valley.app.ports.input.piper_gilfoyle_system_use_case import GilfoyleSystemUseCase
from silicon_valley.app.ports.output.piper_gilfoyle_system_port import GilfoyleSystemPort


class GilfoyleSystemInteractor(GilfoyleSystemUseCase):
    def __init__(self, repository: GilfoyleSystemPort):
        self.repository = repository

    async def introduce_myself(self, request) -> GilfoyleSystemResponse:
        return await self.repository.introduce_myself(GilfoyleSystemQuery(
            id=request.id,
            name=request.name,
        ))

    async def monitor_system(self) -> dict:
        return {}
