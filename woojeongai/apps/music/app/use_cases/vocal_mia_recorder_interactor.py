from __future__ import annotations

import logging
from dataclasses import replace

from music.adapter.inbound.api.schemas.vocal_mia_recorder_schema import MiaIntroduceSchema, MiaIntroduceResponse
from music.app.dtos.evaluation_dto import MiaIntroduceQuery, VocalEvaluationCreateCommand, VocalEvaluationResultDto
from music.app.ports.input.vocal_mia_recorder_use_case import EvaluationUseCase
from music.app.ports.output.vocal_bard_searcher_port import ListPort
from music.app.ports.output.vocal_mia_maestro_port import EvaluationPort

logger = logging.getLogger(__name__)


class MiaRecorderInteractor(EvaluationUseCase):
    def __init__(
        self,
        repository: EvaluationPort,
        list_repository: ListPort,
    ) -> None:
        self.repository = repository
        self.list_repository = list_repository

    async def introduce_myself(self, schema: MiaIntroduceSchema) -> MiaIntroduceResponse:
        return await self.repository.introduce_myself(MiaIntroduceQuery(id=schema.id, name=schema.name))

    async def _resolve_catalog_and_mr(
        self,
        catalog_song_id: str | None,
        mr_search_list_id: int | None,
    ) -> tuple[str | None, int | None]:
        if mr_search_list_id is None:
            return catalog_song_id, None

        mr = await self.list_repository.get_by_id(mr_search_list_id)
        if mr is None:
            raise ValueError("선택한 MR 검색 기록을 찾을 수 없습니다.")

        resolved_catalog = mr.catalog_song_id
        if catalog_song_id is not None and catalog_song_id != resolved_catalog:
            logger.warning(
                "[MUSIC][mia][4/interactor] catalogSongId=%s → MR 기준 %s 로 정정",
                catalog_song_id,
                resolved_catalog,
            )
        return resolved_catalog, mr_search_list_id

    async def upload(
        self, command: VocalEvaluationCreateCommand
    ) -> VocalEvaluationResultDto:
        '''Mia의 보컬 평가 제출 (3NF 저장)'''
        resolved_catalog, resolved_mr_id = await self._resolve_catalog_and_mr(
            command.catalog_song_id,
            command.mr_search_list_id,
        )
        resolved_command = replace(
            command,
            catalog_song_id=resolved_catalog,
            mr_search_list_id=resolved_mr_id,
        )
        result = await self.repository.save_evaluation_bundle(resolved_command)
        logger.info("[MUSIC][mia][4/interactor] 저장 완료 eval=%s", result.id)
        return result
