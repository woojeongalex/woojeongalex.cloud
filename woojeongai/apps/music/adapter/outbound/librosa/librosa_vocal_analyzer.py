"""[Layer: Adapter Outbound] librosa 기반 보컬 분석 — CPU-bound, 동기 함수."""
from __future__ import annotations

import io
import logging
from dataclasses import dataclass

import librosa
import numpy as np

logger = logging.getLogger(__name__)

_GRADE_TABLE = [
    (95, "S"),
    (90, "A+"),
    (85, "A"),
    (80, "A-"),
    (75, "B+"),
    (70, "B"),
    (65, "B-"),
    (60, "C+"),
    (50, "C"),
    (0, "D"),
]


def _grade(score: int) -> str:
    for threshold, label in _GRADE_TABLE:
        if score >= threshold:
            return label
    return "D"


@dataclass(frozen=True)
class LibrosaAnalysisResult:
    pitch_score: int
    rhythm_score: int
    vocal_grade: str
    summary: str
    mean_hz: float
    std_hz: float
    tempo: float
    duration: float


def analyze_vocal_sync(audio_bytes: bytes, content_type: str = "audio/wav") -> LibrosaAnalysisResult:
    """동기 분석 함수 — 호출 측에서 asyncio.to_thread 위임."""
    y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None, mono=True)
    duration = float(librosa.get_duration(y=y, sr=sr))

    # ── 음정 분석 (pyin) ──────────────────────────────────────────────
    f0, voiced_flag, _ = librosa.pyin(
        y,
        fmin=float(librosa.note_to_hz("C2")),
        fmax=float(librosa.note_to_hz("C7")),
        sr=sr,
    )
    voiced_f0 = f0[voiced_flag & ~np.isnan(f0)]  # type: ignore[index]
    if len(voiced_f0) == 0:
        mean_hz, std_hz, pitch_score = 0.0, 0.0, 50
    else:
        mean_hz = float(np.mean(voiced_f0))
        std_hz = float(np.std(voiced_f0))
        # 변동 계수(CV) 기반 안정성: CV 낮을수록 안정 → 점수 높음
        cv = std_hz / mean_hz if mean_hz > 0 else 1.0
        pitch_score = max(0, min(100, int(100 - cv * 150)))

    # ── 리듬 분석 (beat_track) ────────────────────────────────────────
    tempo_arr, beats = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(tempo_arr) if np.ndim(tempo_arr) == 0 else float(tempo_arr[0])
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    # 비트 간격 일관성
    if len(beats) >= 2:
        intervals = np.diff(beats).astype(float)
        rhythm_cv = float(np.std(intervals) / np.mean(intervals)) if np.mean(intervals) > 0 else 1.0
        rhythm_score = max(0, min(100, int(100 - rhythm_cv * 120)))
    else:
        rhythm_score = 50

    overall = (pitch_score * 6 + rhythm_score * 4) // 10
    grade = _grade(overall)

    lines = [
        f"평균 음정: {mean_hz:.1f}Hz (표준편차 {std_hz:.1f}Hz)",
        f"템포: {tempo:.1f}BPM · 비트 수: {len(beats)}",
        f"음정 점수: {pitch_score} / 리듬 점수: {rhythm_score} → 종합 등급 {grade}",
    ]
    if pitch_score < 70:
        lines.append("음정 안정성 향상이 필요합니다. 롱톤 연습을 권장합니다.")
    if rhythm_score < 70:
        lines.append("박자 일관성 향상이 필요합니다. 메트로놈 연습을 권장합니다.")
    if overall >= 85:
        lines.append("전반적으로 뛰어난 보컬 역량을 보여주고 있습니다.")

    logger.info(
        "[Maestro][librosa] pitch=%d rhythm=%d grade=%s duration=%.1fs",
        pitch_score, rhythm_score, grade, duration,
    )
    return LibrosaAnalysisResult(
        pitch_score=pitch_score,
        rhythm_score=rhythm_score,
        vocal_grade=grade,
        summary=" ".join(lines),
        mean_hz=mean_hz,
        std_hz=std_hz,
        tempo=tempo,
        duration=duration,
    )
