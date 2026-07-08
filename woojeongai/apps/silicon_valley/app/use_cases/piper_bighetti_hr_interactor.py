from __future__ import annotations

from silicon_valley.app.dtos.piper_bighetti_hr_dto import BighettiHrQuery, BighettiHrResponse
from silicon_valley.app.ports.input.piper_bighetti_hr_use_case import BighettiHrUseCase
from silicon_valley.app.ports.output.piper_bighetti_hr_port import BighettiHrPort


class BighettiHrInteractor(BighettiHrUseCase):
    def __init__(self, repository: BighettiHrPort):
        self.repository = repository

    async def introduce_myself(self, request) -> BighettiHrResponse:
        return await self.repository.introduce_myself(BighettiHrQuery(
            id=request.id,
            name=request.name,
        ))

    async def get_employee_list(self) -> dict:
        return {}
