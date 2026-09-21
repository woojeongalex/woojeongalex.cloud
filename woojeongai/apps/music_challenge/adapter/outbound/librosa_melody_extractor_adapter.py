"""[Layer: Adapter Outbound] MelodyExtractorPort 구현체 — librosa pyin 기반.

보컬 스템(반주가 빠진 목소리만의 트랙)을 받아 음표 목록으로 바꾼다.
완성곡을 넣으면 반주 음까지 잡히므로 반드시 보컬 스템이어야 한다.

처리 순서
1. 16kHz 모노로 맞추고 20ms 간격으로 pyin 음높이를 잰다.
2. 너무 작은 소리(숨소리, 리버브 꼬리)는 버린다.
3. 비브라토에 흔들리지 않도록, 지금 음표의 중심에서 0.7 반음 이상
   벗어날 때만 새 음표로 끊는다(히스테리시스).
4. 너무 짧은 음표는 버리고, 끊긴 같은 음은 다시 잇는다.
"""

import io

import librosa
import numpy as np

from music_challenge.app.ports.output.melody_extractor_port import (
    ExtractedMelody,
    MelodyExtractorPort,
)
from music_challenge.domain.value_objects.chart_vo import Note

_SR = 16000
_HOP = 320  # 20ms
# 창이 길면 같은 음 사이의 짧은 쉼을 덮어 버린다. 64ms 면 C2 도 네 주기가 들어간다.
_FRAME = 1024
_FRAME_SEC = _HOP / _SR

# 이 음역 밖은 사람 목소리로 보지 않는다.
_FMIN = float(librosa.note_to_hz("C2"))
_FMAX = float(librosa.note_to_hz("C6"))

# 가장 큰 소리보다 이만큼 작으면 무음으로 본다.
_SILENCE_DB = 35.0
# 음표 중심에서 이만큼 벗어나야 다른 음으로 본다.
_SPLIT_SEMITONES = 0.7
# 음표 안에서 이 정도 짧게 끊긴 건 같은 음으로 이어 본다.
_MAX_GAP_FRAMES = 3
_MIN_NOTE_SEC = 0.1
_MERGE_GAP_SEC = 0.08


def _frame_pitches(y: np.ndarray) -> np.ndarray:
    """프레임별 MIDI 음높이(실수). 소리가 없거나 음정이 없으면 nan."""
    f0, voiced, _ = librosa.pyin(
        y,
        fmin=_FMIN,
        fmax=_FMAX,
        sr=_SR,
        frame_length=_FRAME,
        hop_length=_HOP,
    )
    midi = librosa.hz_to_midi(f0)
    midi[~voiced] = np.nan

    rms = librosa.feature.rms(y=y, frame_length=_FRAME, hop_length=_HOP)[0]
    rms_db = librosa.amplitude_to_db(rms, ref=np.max)
    n = min(len(midi), len(rms_db))
    midi = midi[:n]
    midi[rms_db[:n] < -_SILENCE_DB] = np.nan
    return midi


def _segment(midi: np.ndarray) -> list[Note]:
    notes: list[Note] = []
    frames: list[float] = []
    start_idx = 0
    gap = 0

    def close(end_idx: int) -> None:
        if not frames:
            return
        start = start_idx * _FRAME_SEC
        end = end_idx * _FRAME_SEC
        if end - start >= _MIN_NOTE_SEC:
            notes.append(
                Note(
                    start=round(start, 3),
                    end=round(end, 3),
                    midi=int(round(float(np.median(frames)))),
                )
            )

    for i, m in enumerate(midi):
        if np.isnan(m):
            if frames:
                gap += 1
                if gap > _MAX_GAP_FRAMES:
                    close(i - gap + 1)
                    frames = []
            continue

        if frames and abs(m - float(np.median(frames))) < _SPLIT_SEMITONES:
            frames.append(float(m))
            gap = 0
            continue

        if frames:
            close(i - gap)
        frames = [float(m)]
        start_idx = i
        gap = 0

    if frames:
        close(len(midi) - gap)

    return _merge(notes)


def _merge(notes: list[Note]) -> list[Note]:
    merged: list[Note] = []
    for note in notes:
        prev = merged[-1] if merged else None
        if prev and prev.midi == note.midi and note.start - prev.end < _MERGE_GAP_SEC:
            merged[-1] = Note(start=prev.start, end=note.end, midi=prev.midi)
        else:
            merged.append(note)
    return merged


def extract_melody(y: np.ndarray, sr: int) -> ExtractedMelody:
    """이미 읽어 둔 신호에서 추출한다. 테스트에서 직접 부르기 위해 분리했다."""
    if sr != _SR:
        y = librosa.resample(y, orig_sr=sr, target_sr=_SR)
    duration = float(len(y) / _SR)
    return ExtractedMelody(
        notes=_segment(_frame_pitches(y)), duration=round(duration, 3)
    )


class LibrosaMelodyExtractorAdapter(MelodyExtractorPort):
    def extract(self, audio_bytes: bytes) -> ExtractedMelody:
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None, mono=True)
        return extract_melody(y, int(sr))
