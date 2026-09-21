from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from music_challenge.adapter.outbound.orm.music_challenge_orm import ChallengeChartModel
from music_challenge.app.ports.output.chart_repository_port import ChartRepositoryPort
from music_challenge.domain.entities.chart_entity import ChallengeChart, ChartStatus
from music_challenge.domain.value_objects.chart_vo import LyricLine, Note


class ChartPgRepository(ChartRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find(self, challenge_id: int) -> ChallengeChart | None:
        model = await self._session.get(ChallengeChartModel, challenge_id)
        return self._to_entity(model) if model else None

    async def save(self, chart: ChallengeChart) -> ChallengeChart:
        model = await self._session.get(ChallengeChartModel, chart.challenge_id)
        if model is None:
            model = ChallengeChartModel(challenge_id=chart.challenge_id)
            self._session.add(model)

        model.status = chart.status.value
        model.notes = [
            {"start": n.start, "end": n.end, "midi": n.midi} for n in chart.notes
        ] or None
        model.duration = chart.duration
        model.vocal_s3_key = chart.vocal_s3_key
        model.instrumental_s3_key = chart.instrumental_s3_key
        model.lyric_lines = [
            {"text": line.text, "start": line.start} for line in chart.lyric_lines
        ] or None
        model.error = chart.error
        model.updated_at = datetime.utcnow()

        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    def _to_entity(self, model: ChallengeChartModel) -> ChallengeChart:
        return ChallengeChart(
            challenge_id=model.challenge_id,
            status=ChartStatus(model.status),
            notes=[
                Note(start=n["start"], end=n["end"], midi=n["midi"])
                for n in (model.notes or [])
            ],
            duration=model.duration,
            vocal_s3_key=model.vocal_s3_key,
            instrumental_s3_key=model.instrumental_s3_key,
            lyric_lines=[
                LyricLine(text=line["text"], start=line.get("start"))
                for line in (model.lyric_lines or [])
            ],
            error=model.error,
            updated_at=model.updated_at,
        )
