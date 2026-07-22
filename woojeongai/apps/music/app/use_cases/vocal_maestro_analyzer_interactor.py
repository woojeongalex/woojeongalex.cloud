"""[Layer: Use Cases] Maestro 보컬 분석 인터랙터."""
from __future__ import annotations

import asyncio
import logging

from music.adapter.inbound.api.schemas.vocal_maestro_analyzer_schema import (
    MaestroAnalyzeResponse,
    MaestroIntroduceResponse,
    MaestroIntroduceSchema,
)
from music.app.dtos.evaluation_dto import (
    MaestroAnalyzeCommand,
    MaestroAnalyzeResultDto,
    MaestroIntroduceQuery,
)
from music.app.ports.input.vocal_maestro_analyzer_use_case import MaestroAnalyzerUseCase
from music.app.ports.output.vocal_librosa_analysis_port import VocalLibrosaPort
from music.app.ports.output.vocal_maestro_analyzer_port import MaestroPort

logger = logging.getLogger(__name__)


class MaestroAnalyzerInteractor(MaestroAnalyzerUseCase):
    def __init__(self, repository: MaestroPort, librosa_port: VocalLibrosaPort) -> None:
        self._repository = repository
        self._librosa = librosa_port

    async def introduce_myself(self, schema: MaestroIntroduceSchema) -> MaestroIntroduceResponse:
        result = await self._repository.introduce_myself(
            MaestroIntroduceQuery(id=schema.id, name=schema.name)
        )
        return MaestroIntroduceResponse(id=result.id, name=result.name)

    async def analyze_vocal(self, command: MaestroAnalyzeCommand) -> MaestroAnalyzeResponse:
        logger.info(
            "[Maestro][analyze] user=%s source=%s file=%s",
            command.user_id, command.input_source, command.file_name,
        )
        # CPU-bound → to_thread
        raw = await asyncio.to_thread(
            self._librosa.analyze,
            command.audio_bytes,
            command.content_type,
        )

        dto = MaestroAnalyzeResultDto(
            analysis_id=0,  # DB 저장 후 교체
            pitch_score=raw.pitch_score,
            rhythm_score=raw.rhythm_score,
            vocal_grade=raw.vocal_grade,
            summary=raw.summary,
            mean_hz=raw.mean_hz,
            std_hz=raw.std_hz,
            tempo=raw.tempo,
            duration=raw.duration,
        )

        analysis_id = await self._repository.save_analysis(
            user_id=command.user_id,
            input_source=command.input_source,
            file_name=command.file_name,
            duration_sec=command.duration_sec or int(raw.duration),
            catalog_song_id=command.catalog_song_id,
            mr_search_list_id=command.mr_search_list_id,
            result=dto,
        )

        return MaestroAnalyzeResponse(
            analysis_id=analysis_id,
            pitch_score=raw.pitch_score,
            rhythm_score=raw.rhythm_score,
            vocal_grade=raw.vocal_grade,
            summary=raw.summary,
            mean_hz=raw.mean_hz,
            std_hz=raw.std_hz,
            tempo=raw.tempo,
            duration=raw.duration,
        )
