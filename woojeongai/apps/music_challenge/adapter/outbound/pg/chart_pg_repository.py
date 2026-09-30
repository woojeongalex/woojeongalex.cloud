from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from music_challenge.adapter.outbound.orm.music_challenge_orm import (
    ChallengeChartModel,
    RhythmChartModel,
)
from music_challenge.app.ports.output.chart_repository_port import (
    ChartRepositoryPort,
    ChartSummary,
)
from music_challenge.domain.entities.chart_entity import ChallengeChart, ChartStatus
from music_challenge.domain.value_objects.chart_vo import (
    InstrumentKind,
    LyricLine,
    MelodySource,
    Note,
)


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
        model.melody_source = chart.melody_source.value
        model.instrument = chart.instrument.value if chart.instrument else None
        model.notes = [
            {"start": n.start, "end": n.end, "midi": n.midi} for n in chart.notes
        ] or None
        model.duration = chart.duration
        model.melody_s3_key = chart.melody_s3_key
        model.backing_s3_key = chart.backing_s3_key
        model.lyric_lines = [
            {"text": line.text, "start": line.start} for line in chart.lyric_lines
        ] or None
        model.error = chart.error
        model.updated_at = datetime.utcnow()

        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def find_ready_summaries(self) -> list[ChartSummary]:
        # 음역은 컬럼이 아니라 notes 안에 있어 파이썬에서 접는다. 곡 수가 수십 개
        # 수준이라 한 번 훑는 편이 컬럼을 늘려 마이그레이션하는 것보다 싸다.
        # BPM 은 리듬 게임 채보에만 있고 없을 수도 있어 바깥 조인으로 붙인다.
        stmt = (
            select(
                ChallengeChartModel.challenge_id,
                ChallengeChartModel.notes,
                RhythmChartModel.bpm,
            )
            .outerjoin(
                RhythmChartModel,
                RhythmChartModel.challenge_id == ChallengeChartModel.challenge_id,
            )
            .where(ChallengeChartModel.status == ChartStatus.READY.value)
        )
        rows = await self._session.execute(stmt)

        out: list[ChartSummary] = []
        for challenge_id, notes, bpm in rows.all():
            midis = [n["midi"] for n in (notes or [])]
            if not midis:
                continue
            out.append(
                ChartSummary(
                    challenge_id=challenge_id,
                    low_midi=min(midis),
                    high_midi=max(midis),
                    bpm=bpm,
                )
            )
        return out

    def _to_entity(self, model: ChallengeChartModel) -> ChallengeChart:
        return ChallengeChart(
            challenge_id=model.challenge_id,
            status=ChartStatus(model.status),
            melody_source=MelodySource(model.melody_source),
            instrument=InstrumentKind(model.instrument) if model.instrument else None,
            notes=[
                Note(start=n["start"], end=n["end"], midi=n["midi"])
                for n in (model.notes or [])
            ],
            duration=model.duration,
            melody_s3_key=model.melody_s3_key,
            backing_s3_key=model.backing_s3_key,
            lyric_lines=[
                LyricLine(text=line["text"], start=line.get("start"))
                for line in (model.lyric_lines or [])
            ],
            error=model.error,
            updated_at=model.updated_at,
        )
