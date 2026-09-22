"""[Layer: Adapter Outbound] MelodyExtractorPort 구현체 — librosa pyin 기반.

멜로디 스템(보컬 스템 또는 멜로디 악기 스템)을 받아 음표 목록으로 바꾼다.
완성곡이나 여러 악기가 섞인 반주를 넣으면 다른 소리까지 음표로 잡히므로
반드시 멜로디 한 줄만 담긴 스템이어야 한다. pyin 은 한 번에 한 음만 잡으므로
화음(여러 음 동시)은 판정할 수 없다.

처리 순서
1. 16kHz 모노로 맞추고 20ms 간격으로 pyin 음높이를 잰다.
2. 너무 작은 소리(숨소리, 리버브·잔향 꼬리)는 버린다.
3. 비브라토에 흔들리지 않도록, 지금 음표의 중심에서 0.7 반음 이상
   벗어날 때만 새 음표로 끊는다(히스테리시스).
4. (악기) 건반·줄을 새로 친 순간(어택)에서도 끊는다. 같은 음을 연달아 치면
   음높이가 이어져서 3번만으로는 한 음으로 합쳐지기 때문이다.
5. 너무 짧은 음표는 버리고, (보컬) 숨 때문에 끊긴 같은 음은 다시 잇는다.
"""

import io
from dataclasses import dataclass

import librosa
import numpy as np

from music_challenge.app.ports.output.melody_extractor_port import (
    ExtractedMelody,
    MelodyExtractorPort,
)
from music_challenge.app.ports.output.pitch_tracker_port import PitchTrackerPort
from music_challenge.domain.value_objects.chart_vo import MelodySource, Note

_SR = 16000
_HOP = 320  # 20ms
# 창이 길면 같은 음 사이의 짧은 쉼을 덮어 버린다. 64ms 면 C2 도 네 주기가 들어간다.
_FRAME = 1024
_FRAME_SEC = _HOP / _SR

# 가장 큰 소리보다 이만큼 작으면 무음으로 본다.
_SILENCE_DB = 35.0
# 음표 중심에서 이만큼 벗어나야 다른 음으로 본다.
_SPLIT_SEMITONES = 0.7
# 음표 안에서 이 정도 짧게 끊긴 건 같은 음으로 이어 본다.
_MAX_GAP_FRAMES = 3
_MIN_NOTE_SEC = 0.1


@dataclass(frozen=True)
class _Profile:
    fmin: float
    fmax: float
    # 어택(새로 친 순간)에서 음표를 끊을지
    split_on_onsets: bool
    # 이 간격보다 가깝게 끊긴 같은 음은 한 음으로 잇는다. 0 이면 잇지 않는다.
    merge_gap_sec: float


_PROFILES: dict[MelodySource, _Profile] = {
    # 사람 목소리 음역. 같은 음을 이어 부르다 숨 때문에 끊기는 경우가 많아 다시 잇는다.
    MelodySource.VOCAL: _Profile(
        fmin=float(librosa.note_to_hz("C2")),
        fmax=float(librosa.note_to_hz("C6")),
        split_on_onsets=False,
        merge_gap_sec=0.08,
    ),
    # 기타 최저음 E2 ~ 플루트·바이올린 고음역까지. 어택으로 끊은 같은 음을 다시 이으면
    # 끊은 의미가 없으므로 잇지 않는다.
    MelodySource.INSTRUMENT: _Profile(
        fmin=float(librosa.note_to_hz("C2")),
        fmax=float(librosa.note_to_hz("C7")),
        split_on_onsets=True,
        merge_gap_sec=0.0,
    ),
}


def _frame_pitches(y: np.ndarray, profile: _Profile) -> np.ndarray:
    """프레임별 MIDI 음높이(실수). 소리가 없거나 음정이 없으면 nan."""
    f0, voiced, _ = librosa.pyin(
        y,
        fmin=profile.fmin,
        fmax=profile.fmax,
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


# 어택으로 인정하려면 직후 소리가 직전보다 이만큼 커져야 한다(약 +3dB).
_ONSET_RISE = 1.4
# 어택 직후 이 프레임 수 안에서 가장 큰 소리를 본다.
_ONSET_LOOKAHEAD = 3


def _onset_frames(y: np.ndarray) -> set[int]:
    """건반·줄을 새로 친 프레임. backtrack 으로 에너지가 솟기 직전 지점에 맞춘다.

    같은 음을 연달아 치면 앞 음의 잔향과 새 음이 겹쳐 맥놀이가 생기고,
    onset_detect 는 그 출렁임을 새 타건으로 잡는다(합성 피아노에서 음표 28 개가
    47 개로 쪼개졌다). 실제로 친 순간은 소리가 뚜렷이 커지므로 그런 것만 남긴다.
    """
    frames = librosa.onset.onset_detect(
        y=y, sr=_SR, hop_length=_HOP, backtrack=True, units="frames"
    )
    rms = librosa.feature.rms(y=y, frame_length=_FRAME, hop_length=_HOP)[0]
    kept: set[int] = set()
    for f in frames:
        f = int(f)
        before = rms[max(0, f - 1)]
        after = rms[f : f + _ONSET_LOOKAHEAD + 1].max(initial=0.0)
        if after >= before * _ONSET_RISE:
            kept.add(f)
    return kept


def _segment(midi: np.ndarray, onsets: set[int], merge_gap_sec: float) -> list[Note]:
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

        same_pitch = (
            bool(frames) and abs(m - float(np.median(frames))) < _SPLIT_SEMITONES
        )
        # 같은 음이라도 새로 친 순간이면 끊는다. 너무 짧게 잘게 쪼개지 않도록
        # 지금 음표가 최소 길이를 넘겼을 때만.
        reattack = i in onsets and len(frames) * _FRAME_SEC >= _MIN_NOTE_SEC
        if same_pitch and not reattack:
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

    return _merge(notes, merge_gap_sec)


def _merge(notes: list[Note], merge_gap_sec: float) -> list[Note]:
    merged: list[Note] = []
    for note in notes:
        prev = merged[-1] if merged else None
        if prev and prev.midi == note.midi and note.start - prev.end < merge_gap_sec:
            merged[-1] = Note(start=prev.start, end=note.end, midi=prev.midi)
        else:
            merged.append(note)
    return merged


# ── 실제 보컬 후처리 ────────────────────────────────────────────────
# Suno 곡(Still Here In The Dark)을 Demucs 로 분리해 뽑았더니 음표 508 개 중 33% 가
# 0.15초 미만 조각이었고, 22 곳에서 옥타브 이상 튀었다. 합성음에서는 없던 문제다.
# - 조각: 음을 끌어올리거나 꺾을 때 지나가는 중간음이 따로 잡힌다.
# - 튐: 숨 섞인 소리·잔향에서 pyin 이 한 옥타브(또는 한 옥타브 반) 아래를 잡는다.

# 주변 흐름을 볼 때 앞뒤로 이만큼(초)의 음표를 본다.
_CONTEXT_SEC = 2.5
# 주변 흐름에서 이만큼(반음) 벗어나면 분석 오류로 의심한다.
_OUTLIER_SEMITONES = 9
# 의심 음표가 이보다 짧으면 버리고, 길면 옥타브만 주변에 맞춘다.
_OUTLIER_DROP_SEC = 0.25
# 이보다 짧은 조각은 옆 음표에 합칠 후보다.
_FRAGMENT_SEC = 0.15
# 옆 음표와 이 이내로 붙어 있고 음 차이가 이 이내일 때만 합친다.
_FRAGMENT_GAP_SEC = 0.06
_FRAGMENT_SEMITONES = 2


def _local_median(notes: list[Note], i: int) -> float | None:
    """i 번째 음표를 뺀 주변 음표들의 길이 가중 중앙값."""
    center = (notes[i].start + notes[i].end) / 2
    ctx = [
        n
        for j, n in enumerate(notes)
        if j != i and abs((n.start + n.end) / 2 - center) <= _CONTEXT_SEC
    ]
    if not ctx:
        return None
    ctx.sort(key=lambda n: n.midi)
    half = sum(n.end - n.start for n in ctx) / 2
    acc = 0.0
    for n in ctx:
        acc += n.end - n.start
        if acc >= half:
            return float(n.midi)
    return float(ctx[-1].midi)


def _fix_outliers(notes: list[Note]) -> list[Note]:
    fixed: list[Note] = []
    for i, note in enumerate(notes):
        med = _local_median(notes, i)
        if med is None or abs(note.midi - med) < _OUTLIER_SEMITONES:
            fixed.append(note)
            continue
        if note.end - note.start < _OUTLIER_DROP_SEC:
            continue  # 짧게 튄 건 분석 오류로 보고 버린다
        # 긴 음은 실제로 부른 음일 수 있으니 옥타브만 주변 흐름에 맞춘다.
        shift = 12 * round((note.midi - med) / 12)
        fixed.append(Note(start=note.start, end=note.end, midi=note.midi - shift))
    return fixed


def _absorb_fragments(notes: list[Note]) -> list[Note]:
    """짧은 조각을 붙어 있는 비슷한 음의 옆 음표에 합친다. 옆 음표의 음을 따른다."""
    notes = list(notes)
    changed = True
    while changed:
        changed = False
        for i, note in enumerate(notes):
            if note.end - note.start >= _FRAGMENT_SEC:
                continue
            neighbors = []
            if i > 0:
                prev = notes[i - 1]
                if (
                    note.start - prev.end <= _FRAGMENT_GAP_SEC
                    and abs(prev.midi - note.midi) <= _FRAGMENT_SEMITONES
                ):
                    neighbors.append(i - 1)
            if i + 1 < len(notes):
                nxt = notes[i + 1]
                if (
                    nxt.start - note.end <= _FRAGMENT_GAP_SEC
                    and abs(nxt.midi - note.midi) <= _FRAGMENT_SEMITONES
                ):
                    neighbors.append(i + 1)
            if not neighbors:
                continue
            j = max(neighbors, key=lambda k: notes[k].end - notes[k].start)
            host = notes[j]
            notes[j] = Note(
                start=min(host.start, note.start),
                end=max(host.end, note.end),
                midi=host.midi,
            )
            del notes[i]
            changed = True
            break
    return notes


def _clean_vocal(notes: list[Note]) -> list[Note]:
    return _merge(
        _absorb_fragments(_fix_outliers(notes)),
        _PROFILES[MelodySource.VOCAL].merge_gap_sec,
    )


def extract_melody(y: np.ndarray, sr: int, source: MelodySource) -> ExtractedMelody:
    """이미 읽어 둔 신호에서 추출한다. 테스트에서 직접 부르기 위해 분리했다."""
    profile = _PROFILES[source]
    if sr != _SR:
        y = librosa.resample(y, orig_sr=sr, target_sr=_SR)
    duration = float(len(y) / _SR)
    onsets = _onset_frames(y) if profile.split_on_onsets else set()
    notes = _segment(_frame_pitches(y, profile), onsets, profile.merge_gap_sec)
    # 악기에는 적용하지 않는다. 1~2반음짜리 짧은 음을 합치면 트릴·빠른 패시지가 뭉개진다.
    if source == MelodySource.VOCAL:
        notes = _clean_vocal(notes)
    return ExtractedMelody(notes=notes, duration=round(duration, 3))


class LibrosaMelodyExtractorAdapter(MelodyExtractorPort):
    def extract(self, audio_bytes: bytes, source: MelodySource) -> ExtractedMelody:
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None, mono=True)
        return extract_melody(y, int(sr), source)


def pitch_track(
    y: np.ndarray, sr: int, source: MelodySource
) -> list[tuple[float, float | None]]:
    """녹음의 프레임별 음높이. 정답 악보를 만들 때와 같은 분석이라 기준이 어긋나지 않는다."""
    if sr != _SR:
        y = librosa.resample(y, orig_sr=sr, target_sr=_SR)
    midi = _frame_pitches(y, _PROFILES[source])
    return [
        (round(i * _FRAME_SEC, 3), None if np.isnan(m) else float(m))
        for i, m in enumerate(midi)
    ]


class LibrosaPitchTrackerAdapter(PitchTrackerPort):
    def track(
        self, audio_bytes: bytes, source: MelodySource
    ) -> list[tuple[float, float | None]]:
        y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None, mono=True)
        return pitch_track(y, int(sr), source)
