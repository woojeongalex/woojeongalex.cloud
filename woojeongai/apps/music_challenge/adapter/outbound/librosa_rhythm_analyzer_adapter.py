"""리듬 게임 채보용 곡 분석 — 박자와 소리가 시작되는 순간들.

완성곡(보컬+반주가 섞인 원곡)을 그대로 쓴다. 리듬 게임은 드럼·베이스·보컬 어느
것이든 "소리가 들리는 순간"에 노트가 있어야 자연스럽기 때문이다.

- 박자: librosa beat_track 의 비트 시각과 BPM
- 소리 시작: 원곡 전체의 onset 강도에서 봉우리를 찾는다
- 세기: 주변 ±4초 봉우리들의 상위 값으로 나눠 조용한 구간의 노트도 살아남게 한다
- 음이름: 화성 성분(HPSS)의 크로마에서 가장 강한 음
- 길이: 같은 음이름이 가장 강한 상태로, 화성 에너지가 절반 아래로 떨어지기 전까지
"""

import io

import librosa
import numpy as np

from music_challenge.app.ports.output.rhythm_analyzer_port import RhythmAnalyzerPort
from music_challenge.domain.value_objects.rhythm_vo import Onset, RhythmAnalysis

_SR = 22050
_HOP = 512
_NORM_WINDOW_S = 4.0
_MAX_SUSTAIN_S = 4.0


def _local_strength(times: np.ndarray, values: np.ndarray, window: float) -> np.ndarray:
    """각 봉우리를 주변 ±window 초 봉우리들의 95번째 백분위로 나눈 값(0~1).

    곡 전체 기준이면 조용한 도입부·브리지의 노트가 모두 탈락한다.
    """
    out = np.empty_like(values)
    for i, t in enumerate(times):
        lo, hi = np.searchsorted(times, [t - window, t + window])
        ref = max(float(np.percentile(values[lo:hi], 95)), 1e-6)
        out[i] = min(1.0, values[i] / ref)
    return out


def _relative(env: np.ndarray) -> np.ndarray:
    """onset 강도를 곡 전체 중앙값으로 나눈다. 타악기·화성 성분은 크기 단위가 달라서다."""
    positive = env[env > 0]
    return env / max(float(np.median(positive)) if positive.size else 1.0, 1e-6)


class LibrosaRhythmAnalyzerAdapter(RhythmAnalyzerPort):
    def analyze(self, audio: bytes) -> RhythmAnalysis:
        y, sr = librosa.load(io.BytesIO(audio), sr=_SR, mono=True)
        duration = float(len(y) / sr)

        # 위상은 쓰지 않으므로 크기 스펙트럼으로 나눈다. 복소수보다 메모리가 절반이다(EC2 1GB).
        mag = np.abs(librosa.stft(y, hop_length=_HOP))
        mag_h, mag_p = librosa.decompose.hpss(mag)
        del mag

        env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=_HOP)
        p_rel = _relative(
            librosa.onset.onset_strength(S=librosa.amplitude_to_db(mag_p), sr=sr)
        )
        h_rel = _relative(
            librosa.onset.onset_strength(S=librosa.amplitude_to_db(mag_h), sr=sr)
        )
        tempo, beat_frames = librosa.beat.beat_track(
            onset_envelope=env, sr=sr, hop_length=_HOP, trim=False
        )
        beats = librosa.frames_to_time(beat_frames, sr=sr, hop_length=_HOP)

        # 어려운 채보도 채울 수 있게 작은 봉우리까지 넉넉히 후보로 뽑는다.
        frames = librosa.onset.onset_detect(
            onset_envelope=env,
            sr=sr,
            hop_length=_HOP,
            backtrack=False,
            wait=1,
            delta=0.02,
        )
        frames = frames[frames < len(env)]
        times = librosa.frames_to_time(frames, sr=sr, hop_length=_HOP)
        strengths = _local_strength(times, env[frames], _NORM_WINDOW_S)

        chroma = librosa.feature.chroma_stft(S=mag_h**2, sr=sr)
        rms_h = librosa.feature.rms(S=mag_h)[0]
        del mag_h, mag_p

        last = len(rms_h) - 1
        max_sus = int(_MAX_SUSTAIN_S * sr / _HOP)
        onsets: list[Onset] = []
        for f, t, strength in zip(frames, times, strengths):
            f = int(f)
            c = chroma[:, max(0, f - 1) : f + 3].mean(axis=1)
            pc = int(np.argmax(c))
            level = rms_h[min(f + 2, last)]
            # 섞인 곡은 화성 에너지가 늘 이어지므로, 같은 음이 계속 가장 강한지도 본다.
            # 두 프레임까지의 짧은 흔들림은 봐준다.
            end, slips = f + 2, 0
            while end < min(last, f + max_sus) and rms_h[end] >= level * 0.5:
                if chroma[pc, end] < 0.8 * chroma[:, end].max():
                    slips += 1
                    if slips > 2:
                        break
                else:
                    slips = 0
                end += 1
            k = min(f, len(p_rel) - 1, len(h_rel) - 1)
            onsets.append(
                Onset(
                    time=float(t),
                    strength=float(strength),
                    pitch=pc / 12.0,
                    sustain=float((end - slips - f) * _HOP / sr),
                    percussive=bool(p_rel[k] > 1.5 * h_rel[k]),
                )
            )

        return RhythmAnalysis(
            duration=duration,
            bpm=round(float(np.atleast_1d(tempo)[0]), 2),
            beats=[round(float(b), 4) for b in beats],
            onsets=onsets,
        )
