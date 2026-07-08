from __future__ import annotations

import logging
import os
import tempfile
import uuid
from pathlib import Path
from typing import Any

from music.adapter.inbound.api.schemas.speech_lumiere_video_schema import LumiereIntroduceSchema, LumiereIntroduceResponse
from music.app.dtos.video_analysis_dto import LumiereIntroduceQuery, VideoVocalAnalysisResultDto
from music.app.ports.input.speech_lumiere_video_use_case import VideoAnalysisUseCase

logger = logging.getLogger(__name__)

# ── 지원 확장자 ────────────────────────────────────────────────────────────────
_VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"}


# ── video_audio_preprocess ────────────────────────────────────────────────────

def _is_supported_video_filename(name: str) -> bool:
    return Path(name).suffix.lower() in _VIDEO_EXTENSIONS


def _extract_audio_wav_from_video(
    video_path: str, wav_out_path: str, sr: int = 22050
) -> None:
    try:
        from moviepy import VideoFileClip
    except ImportError:
        from moviepy.editor import VideoFileClip  # type: ignore[no-redef]

    clip = VideoFileClip(video_path)
    try:
        if clip.audio is None:
            raise ValueError("비디오에 오디오 트랙이 없습니다.")
        clip.audio.write_audiofile(
            wav_out_path,
            fps=sr,
            nbytes=2,
            codec="pcm_s16le",
            logger=None,
        )
    finally:
        clip.close()

    if not os.path.isfile(wav_out_path) or os.path.getsize(wav_out_path) == 0:
        raise RuntimeError("오디오 추출 결과 WAV 파일이 비어 있거나 생성되지 않았습니다.")

    logger.info("[lumiere][preprocess] WAV 추출 완료 sr=%s out=%s", sr, wav_out_path)


# ── librosa_vocal_analysis ────────────────────────────────────────────────────

def _analyze_pitch_bpm_duration(wav_path: str, sr: int = 22050) -> dict[str, Any]:
    import librosa
    import numpy as np

    y, sr = librosa.load(wav_path, sr=sr, mono=True)
    duration = float(librosa.get_duration(y=y, sr=sr))

    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo_arr, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    bpm = float(np.atleast_1d(tempo_arr).reshape(-1)[0])

    f0 = librosa.yin(
        y,
        fmin=librosa.note_to_hz("E2"),
        fmax=librosa.note_to_hz("C7"),
        sr=sr,
    )
    valid = (f0 > 65.0) & (f0 < 1500.0)
    f0_v = f0[valid]
    mean_hz = float(np.nanmean(f0)) if f0.size else 0.0
    median_hz = float(np.median(f0_v)) if f0_v.size else 0.0

    max_samples = 100
    step = max(1, len(f0) // max_samples)
    f0_sample = [round(float(x), 2) for x in f0[::step][:max_samples]]

    pitch_data: dict[str, Any] = {
        "sample_rate": sr,
        "mean_f0_hz": round(mean_hz, 2),
        "median_f0_hz": round(median_hz, 2),
        "f0_contour_sample": f0_sample,
    }

    logger.info(
        "[lumiere][librosa] duration=%.2fs bpm=%.1f mean_f0=%.1f",
        duration,
        bpm,
        mean_hz,
    )
    return {"pitch_data": pitch_data, "bpm": round(bpm, 2), "duration": round(duration, 3)}


# ── emotion_analysis ──────────────────────────────────────────────────────────

def _neutral_stub() -> dict[str, float]:
    return {"sadness": 0.05, "passion": 0.12, "neutral": 0.83}


def _analyze_emotion(audio_path: str) -> dict[str, float]:
    if not os.path.isfile(audio_path):
        logger.warning("[lumiere][emotion] 파일 없음: %s", audio_path)
        return _neutral_stub()
    logger.info("[lumiere][emotion] 플레이스홀더 분석 (외부 API 미연동): %s", audio_path)
    return _neutral_stub()


def _emotions_for_json(em: dict[str, float]) -> dict[str, float]:
    out: dict[str, float] = {}
    for k, v in em.items():
        try:
            out[str(k)] = float(v)
        except (TypeError, ValueError):
            continue
    return out if out else _neutral_stub()


# ── interactor ────────────────────────────────────────────────────────────────

class LumiereVideoInteractor(VideoAnalysisUseCase):
    async def introduce_myself(self, schema: LumiereIntroduceSchema) -> LumiereIntroduceResponse:
        return LumiereIntroduceResponse(
            id=schema.id * 10000,
            name=schema.name + "가 레포지토리에 다녀옴",
        )

    def analyze(
        self, data: bytes, original_filename: str
    ) -> VideoVocalAnalysisResultDto:
        '''Lumière의 영상 보컬 분석'''
        if not data:
            raise ValueError("업로드 파일이 비어 있습니다.")
        name = original_filename or "video.bin"
        if not _is_supported_video_filename(name):
            allowed = ", ".join(sorted(_VIDEO_EXTENSIONS))
            raise ValueError(f"지원하지 않는 확장자입니다. 허용: {allowed}")

        suffix = Path(name).suffix.lower() or ".mp4"

        with tempfile.TemporaryDirectory(prefix="vocal_vid_") as tmp:
            vid_path = os.path.join(tmp, f"in_{uuid.uuid4().hex}{suffix}")
            wav_path = os.path.join(tmp, "extracted.wav")

            with open(vid_path, "wb") as f:
                f.write(data)

            _extract_audio_wav_from_video(vid_path, wav_path)

            lib_out = _analyze_pitch_bpm_duration(wav_path)
            raw_emotion = _analyze_emotion(wav_path)
            emotions = _emotions_for_json(raw_emotion)

        return VideoVocalAnalysisResultDto(
            pitch_data=lib_out["pitch_data"],
            bpm=lib_out["bpm"],
            duration=lib_out["duration"],
            emotions=emotions,
        )
