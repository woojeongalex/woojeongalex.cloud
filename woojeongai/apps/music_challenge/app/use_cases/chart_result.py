from music_challenge.app.dtos.chart_dto import ChartResult
from music_challenge.app.ports.output.media_storage_port import MediaStoragePort
from music_challenge.domain.entities.chart_entity import ChallengeChart, ChartStatus
from music_challenge.domain.value_objects.chart_vo import MelodySource
from music_challenge.domain.value_objects.music_challenge_vo import ChallengeType


def default_melody_source(challenge_type: ChallengeType) -> MelodySource:
    """아직 스템을 올리지 않은 챌린지의 기본 추출 방식. 악기 챌린지만 악기로 본다."""
    return (
        MelodySource.INSTRUMENT
        if challenge_type == ChallengeType.INSTRUMENT
        else MelodySource.VOCAL
    )


def empty_chart_result(challenge_id: int, source: MelodySource) -> ChartResult:
    return ChartResult(
        challenge_id=challenge_id,
        status=ChartStatus.EMPTY,
        melody_source=source,
        instrument=None,
        notes=[],
        duration=None,
        lyric_lines=[],
        backing_url=None,
        has_melody=False,
        error=None,
    )


async def to_chart_result(
    chart: ChallengeChart, storage: MediaStoragePort
) -> ChartResult:
    """악보 엔티티를 응답용으로 바꾼다. 반주는 바로 재생할 수 있게 서명 URL 로 준다."""
    backing_url = (
        await storage.playback_url(chart.backing_s3_key)
        if chart.backing_s3_key
        else None
    )
    return ChartResult(
        challenge_id=chart.challenge_id,
        status=chart.status,
        melody_source=chart.melody_source,
        instrument=chart.instrument,
        notes=chart.notes,
        duration=chart.duration,
        lyric_lines=chart.lyric_lines,
        backing_url=backing_url,
        has_melody=chart.melody_s3_key is not None,
        error=chart.error,
    )
