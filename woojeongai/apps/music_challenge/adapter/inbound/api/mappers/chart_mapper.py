from music_challenge.adapter.inbound.api.schemas.chart_schema import (
    ChartResponse,
    LyricLineSchema,
    NoteSchema,
)
from music_challenge.app.dtos.chart_dto import ChartResult
from music_challenge.domain.value_objects.chart_vo import LyricLine


def chart_result_to_response(result: ChartResult) -> ChartResponse:
    return ChartResponse(
        challenge_id=result.challenge_id,
        status=result.status.value,
        melody_source=result.melody_source.value,
        instrument=result.instrument.value if result.instrument else None,
        notes=[NoteSchema(start=n.start, end=n.end, midi=n.midi) for n in result.notes],
        duration=result.duration,
        lyric_lines=[
            LyricLineSchema(text=line.text, start=line.start)
            for line in result.lyric_lines
        ],
        backing_url=result.backing_url,
        has_melody=result.has_melody,
        error=result.error,
    )


def lyric_schemas_to_lines(lines: list[LyricLineSchema]) -> list[LyricLine]:
    # 빈 줄은 화면에 띄울 게 없으므로 저장하지 않는다.
    return [
        LyricLine(text=line.text.strip(), start=line.start)
        for line in lines
        if line.text.strip()
    ]
