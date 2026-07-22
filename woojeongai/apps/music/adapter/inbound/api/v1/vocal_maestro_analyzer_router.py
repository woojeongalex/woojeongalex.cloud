"""[Layer: Adapter Inbound] Maestro 라우터 — 자기소개 + 보컬 분석."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile

from music.adapter.inbound.api.deps.music_deps import get_maestro_use_case
from music.adapter.inbound.api.schemas.vocal_maestro_analyzer_schema import (
    MaestroAnalyzeResponse,
    MaestroIntroduceResponse,
    MaestroIntroduceSchema,
)
from music.app.dtos.evaluation_dto import MaestroAnalyzeCommand
from music.app.ports.input.vocal_maestro_analyzer_use_case import MaestroAnalyzerUseCase

vocal_maestro_analyzer_router = APIRouter(tags=["music-vocal"])


@vocal_maestro_analyzer_router.get(
    "/api/music/maestro/myself",
    response_model=MaestroIntroduceResponse,
)
async def maestro_introduce_myself(
    maestro: MaestroAnalyzerUseCase = Depends(get_maestro_use_case),
) -> MaestroIntroduceResponse:
    return await maestro.introduce_myself(MaestroIntroduceSchema(id=3, name="보컬 마에스트로 (Maestro)"))


@vocal_maestro_analyzer_router.post(
    "/api/music/maestro/analyze",
    response_model=MaestroAnalyzeResponse,
    summary="보컬 오디오 분석 (librosa pyin)",
)
async def analyze_vocal(
    file: UploadFile = File(..., description="오디오 파일 (wav/mp3/m4a)"),
    input_source: str = Form("mic", description="mic | video"),
    user_id: int | None = Form(None, description="로그인 유저 ID (선택)"),
    catalog_song_id: str | None = Form(None),
    mr_search_list_id: int | None = Form(None),
    maestro: MaestroAnalyzerUseCase = Depends(get_maestro_use_case),
) -> MaestroAnalyzeResponse:
    audio_bytes = await file.read()
    command = MaestroAnalyzeCommand(
        audio_bytes=audio_bytes,
        content_type=file.content_type or "audio/wav",
        user_id=user_id,
        input_source=input_source,
        file_name=file.filename or "upload",
        duration_sec=0,
        catalog_song_id=catalog_song_id,
        mr_search_list_id=mr_search_list_id,
    )
    return await maestro.analyze_vocal(command)
