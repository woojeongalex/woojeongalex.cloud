from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from music.adapter.outbound.orm.instrument_andrew_recorder_model import InstrumentRecordingEntity
from music.adapter.outbound.orm.instrument_fletcher_tuner_model import InstrumentEvaluationEntity, InstrumentTuningAnalysisEntity
from music.adapter.outbound.pg.pg_bundle_repository import save_three_part_bundle
from music.app.dtos.instrument_dto import AndrewIntroduceQuery, AndrewIntroduceResponse, FranzIntroduceQuery, FranzIntroduceResponse, InstrumentEvaluationCreateCommand, InstrumentEvaluationResultDto
from music.app.ports.output.instrument_andrew_recorder_port import InstrumentPort


class AndrewRecorderPgRepository(InstrumentPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def introduce_franz(self, query: FranzIntroduceQuery) -> FranzIntroduceResponse:
        return FranzIntroduceResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")

    async def introduce_andrew(self, query: AndrewIntroduceQuery) -> AndrewIntroduceResponse:
        return AndrewIntroduceResponse(id=query.id * 10000, name=query.name + "가 레포지토리에 다녀옴")

    async def save_evaluation_bundle(
        self, command: InstrumentEvaluationCreateCommand
    ) -> InstrumentEvaluationResultDto:
        evaluation = InstrumentEvaluationEntity(user_id=None)
        recording = InstrumentRecordingEntity(
            instrument_evaluation_id=0,
            user_id=None,
            instrument_id=command.instrument_id,
            file_name=command.file_name or f"{command.instrument_id}-recording",
            duration_sec=command.duration_sec,
        )
        analysis = InstrumentTuningAnalysisEntity(
            instrument_recording_id=0,
            analysis_engine="client_demo",
            tuning_accuracy=command.tuning_accuracy,
            pitch_deviation_cents=command.pitch_deviation_cents,
            summary=command.summary,
            string_readings=list(command.string_readings),
        )
        saved_eval, _, _ = await save_three_part_bundle(
            self._session,
            evaluation,
            recording,
            analysis,
            recording_fk_attr="instrument_evaluation_id",
            analysis_fk_attr="instrument_recording_id",
            log_label="andrew",
        )
        return InstrumentEvaluationResultDto(id=saved_eval.id)
