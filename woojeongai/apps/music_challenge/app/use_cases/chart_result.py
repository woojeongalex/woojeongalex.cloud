from music_challenge.app.dtos.chart_dto import ChartResult
from music_challenge.app.ports.output.media_storage_port import MediaStoragePort
from music_challenge.domain.entities.chart_entity import ChallengeChart, ChartStatus


async def to_chart_result(
    chart: ChallengeChart | None, challenge_id: int, storage: MediaStoragePort
) -> ChartResult:
    """악보 엔티티를 응답용으로 바꾼다. 아직 악보가 없으면 빈 상태를 돌려준다."""
    if chart is None:
        return ChartResult(
            challenge_id=challenge_id,
            status=ChartStatus.EMPTY,
            notes=[],
            duration=None,
            lyric_lines=[],
            instrumental_url=None,
            has_vocal=False,
            error=None,
        )

    instrumental_url = (
        await storage.presigned_url(chart.instrumental_s3_key)
        if chart.instrumental_s3_key
        else None
    )
    return ChartResult(
        challenge_id=chart.challenge_id,
        status=chart.status,
        notes=chart.notes,
        duration=chart.duration,
        lyric_lines=chart.lyric_lines,
        instrumental_url=instrumental_url,
        has_vocal=chart.vocal_s3_key is not None,
        error=chart.error,
    )
