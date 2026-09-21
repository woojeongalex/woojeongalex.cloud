"""노래방 화면용 악보(정답 멜로디 + 가사) 라우터."""

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)

from friday13th.adapter.inbound.api.deps.current_user_deps import require_admin
from music_challenge.adapter.inbound.api.deps.music_challenge_deps import (
    get_chart_use_case,
    get_update_lyrics_use_case,
    get_upload_stems_use_case,
    run_build_chart,
)
from music_challenge.adapter.inbound.api.mappers.chart_mapper import (
    chart_result_to_response,
    lyric_schemas_to_lines,
)
from music_challenge.adapter.inbound.api.schemas.chart_schema import (
    ChartResponse,
    UpdateLyricsRequest,
)
from music_challenge.app.dtos.chart_dto import StemFile, UploadStemsCommand
from music_challenge.app.ports.input.chart_use_case import (
    GetChartUseCase,
    UpdateLyricsUseCase,
    UploadStemsUseCase,
)

charts_router = APIRouter(prefix="/challenges", tags=["music-challenge"])

# 4분짜리 스테레오 WAV 가 40MB 남짓이다. EC2 메모리가 1GB 라 넉넉히 막아 둔다.
_MAX_STEM_BYTES = 60 * 1024 * 1024


async def _read_stem(upload: UploadFile, label: str) -> StemFile:
    data = await upload.read(_MAX_STEM_BYTES + 1)
    if len(data) > _MAX_STEM_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"{label} 파일이 너무 큽니다. 60MB 이하로 올려 주세요.",
        )
    if not data:
        raise HTTPException(status_code=422, detail=f"{label} 파일이 비어 있습니다.")
    return StemFile(
        filename=upload.filename or label,
        content_type=upload.content_type or "audio/wav",
        data=data,
    )


@charts_router.get("/{challenge_id}/chart", response_model=ChartResponse)
async def get_chart(
    challenge_id: int,
    use_case: GetChartUseCase = Depends(get_chart_use_case),
) -> ChartResponse:
    return chart_result_to_response(await use_case.get(challenge_id))


@charts_router.post(
    "/{challenge_id}/stems",
    response_model=ChartResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_stems(
    challenge_id: int,
    background: BackgroundTasks,
    vocal_file: UploadFile = File(...),
    instrumental_file: UploadFile | None = File(None),
    _admin: dict = Depends(require_admin),
    use_case: UploadStemsUseCase = Depends(get_upload_stems_use_case),
) -> ChartResponse:
    """스템을 저장하고 곧바로 202 를 돌려준다.

    정답 멜로디 추출은 3분 곡에 수십 초가 걸려 프록시 타임아웃에 걸릴 수 있으므로
    응답 뒤에 돌린다. 화면은 GET /chart 의 status 로 완료를 확인한다.
    """
    vocal = await _read_stem(vocal_file, "보컬")
    instrumental = (
        await _read_stem(instrumental_file, "반주") if instrumental_file else None
    )
    result = await use_case.upload(
        UploadStemsCommand(
            challenge_id=challenge_id, vocal=vocal, instrumental=instrumental
        )
    )
    background.add_task(run_build_chart, challenge_id, result.vocal_key, vocal.data)
    return chart_result_to_response(result.chart)


@charts_router.put("/{challenge_id}/lyrics", response_model=ChartResponse)
async def update_lyrics(
    challenge_id: int,
    body: UpdateLyricsRequest,
    _admin: dict = Depends(require_admin),
    use_case: UpdateLyricsUseCase = Depends(get_update_lyrics_use_case),
) -> ChartResponse:
    result = await use_case.update(challenge_id, lyric_schemas_to_lines(body.lines))
    return chart_result_to_response(result)
