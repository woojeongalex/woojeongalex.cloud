from __future__ import annotations

import logging

from music.adapter.inbound.api.schemas.speech_oracle_analyst_schema import OracleIntroduceSchema, OracleIntroduceResponse
from music.app.dtos.speech_dto import OracleIntroduceQuery
from music.app.ports.input.speech_oracle_analyst_use_case import OracleAnalystUseCase
from music.app.ports.output.speech_oracle_analyst_port import OraclePort

logger = logging.getLogger(__name__)


class OracleAnalystInteractor(OracleAnalystUseCase):
    def __init__(self, repository: OraclePort) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: OracleIntroduceSchema) -> OracleIntroduceResponse:
        return await self.repository.introduce_myself(OracleIntroduceQuery(id=schema.id, name=schema.name))
