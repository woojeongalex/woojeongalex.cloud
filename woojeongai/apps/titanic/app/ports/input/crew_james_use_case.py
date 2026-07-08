from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from titanic.adapter.inbound.api.schemas.crew_james_introduce_schema import JamesIntroduceSchema
from titanic.app.dtos.crew_james_command import JamesIntroduceResponse, PersonCommand


class JamesUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: JamesIntroduceSchema) -> JamesIntroduceResponse:
        pass

    @abstractmethod
    async def upload(self, person_commands: list[PersonCommand], file_name: str) -> dict[str, Any]:
        pass
