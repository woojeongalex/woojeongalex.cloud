import asyncio

from fastapi import APIRouter, Depends, File, UploadFile

from music.adapter.inbound.api.mappers.music_inbound_mapper import to_video_analysis_response
from music.adapter.inbound.api.parsers.video_upload_parser import read_video_upload
from music.adapter.inbound.api.schemas.speech_lumiere_video_schema import LumiereIntroduceSchema, LumiereIntroduceResponse, VideoVocalAnalysisResponse
from music.app.ports.input.speech_lumiere_video_use_case import VideoAnalysisUseCase
from music.adapter.inbound.api.deps.music_deps import get_video_use_case

speech_lumiere_video_router = APIRouter(tags=["music-video"])


@speech_lumiere_video_router.get("/api/music/lumiere/myself", response_model=LumiereIntroduceResponse)
async def lumiere_introduce_myself(
    lumiere: VideoAnalysisUseCase = Depends(get_video_use_case),
) -> LumiereIntroduceResponse:
    return await lumiere.introduce_myself(LumiereIntroduceSchema(id=11, name="스피치 루미에르 (Lumiere)"))


@speech_lumiere_video_router.post("/api/music/analyze-video", response_model=VideoVocalAnalysisResponse)
async def analyze_video_upload(
    file: UploadFile = File(..., description="노래 부르는 영상 (mp4, mov 등)"),
    video: VideoAnalysisUseCase = Depends(get_video_use_case),
) -> VideoVocalAnalysisResponse:
    filename, data = await read_video_upload(file)
    dto = await asyncio.to_thread(video.analyze, data, filename)
    return to_video_analysis_response(dto)
