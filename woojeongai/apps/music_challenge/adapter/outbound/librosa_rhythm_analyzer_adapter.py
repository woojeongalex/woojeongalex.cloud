"""리듬 게임 채보용 곡 분석 — 박자와 소리가 시작되는 순간들.

완성곡(보컬+반주가 섞인 원곡)을 그대로 쓴다. 리듬 게임은 드럼·베이스·보컬 어느
것이든 "소리가 들리는 순간"에 노트가 있어야 자연스럽기 때문이다.

- 박자: librosa beat_track 의 비트 시각과 BPM. 단, 비트를 **드럼 타격에 맞춰 통째로 민다**
- 소리 시작: 원곡 전체의 onset 강도에서 봉우리를 찾고, 봉우리 앞의 골로 되돌려 시작점을 쓴다
- 세기: 주변 ±4초 봉우리들의 상위 값으로 나눠 조용한 구간의 노트도 살아남게 한다
- 음이름: 화성 성분(HPSS)의 크로마에서 가장 강한 음
- 길이: 같은 음이름이 가장 강한 상태로, 화성 에너지가 절반 아래로 떨어지기 전까지

2026-09-28 "노트가 소리보다 늦다"를 고쳤다. onset 강도의 봉우리는 실제 타격보다
두세 프레임(약 50~70ms) 늦는데, 비트도 같은 강도에서 뽑혀 함께 늦어 있었다.
운영 곡 7개에서 비트 ±6% 안에 드럼이 있는 비율이 0~3.6% 였다(보정 뒤 30~85%).
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
# 비트를 드럼에 맞출 때 쓰는 허용 오차의 하한(초). 분석 프레임 간격(512/22050 = 23ms)의
# 두 배쯤 둔다. 이보다 좁으면 빠른 곡에서 프레임 하나 차이로 다 걸러져 보정이 망가진다.
_MIN_ALIGN_TOL = 0.05


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


def _beat_offset(beats: np.ndarray, hits: np.ndarray, period: float) -> float:
    """비트 격자를 통째로 얼마나 밀어야 드럼 타격에 얹히는지(초).

    ±0.25박을 훑으며 "비트마다 그 자리에 있는 가장 센 드럼"의 합이 가장 큰 값을 고른다.

    허용 오차에 절대 하한(_MIN_ALIGN_TOL)을 둔다. 박길이 비례로만 잡으면 빠른 곡에서
    분석 프레임 간격(약 23ms)보다 좁아져 아무것도 잡히지 않고 보정값이 아무렇게나
    정해진다. 실제로 152BPM 곡에서 허용 오차가 23.7ms 라 보정이 먹지 않았다.

    드럼마다 세지 않고 비트마다 세는 것도 중요하다. 드럼이 촘촘한 곡에서 한 비트에
    여러 타격이 겹쳐 점수를 부풀리기 때문이다.

    점수는 세기를 더하지 않고 "드럼이 있는 비트의 개수"로 센다. 세기로 더하면 소리가
    큰 후렴에 맞춰지고 조용한 절이 밀린다(운영 7곡 평균 60.9% vs 62.8%).
    """
    if beats.size == 0 or hits.size == 0:
        return 0.0
    tol = max(period * 0.06, _MIN_ALIGN_TOL)
    best, best_score = 0.0, -1
    for step in range(-25, 26):
        offset = step * period * 0.01
        shifted = beats + offset
        idx = np.searchsorted(hits, shifted)
        score = 0
        for k in range(shifted.size):
            for j in (idx[k] - 1, idx[k]):
                if 0 <= j < hits.size and abs(hits[j] - shifted[k]) <= tol:
                    score += 1
                    break
        if score > best_score:
            best, best_score = offset, score
    # 창에 든 타격의 치우침 중앙값으로 한 번 더 미는 것도 해 봤지만 일치율이
    # 59.9% → 52.4% 로 떨어졌다. 훑기가 찾은 자리가 이미 최적이다.
    return best


class LibrosaRhythmAnalyzerAdapter(RhythmAnalyzerPort):
    def analyze(self, audio: bytes) -> RhythmAnalysis:
        y, sr = librosa.load(io.BytesIO(audio), sr=_SR, mono=True)
        duration = float(len(y) / sr)

        # 위상은 쓰지 않으므로 크기 스펙트럼으로 나눈다. 복소수보다 메모리가 절반이다(EC2 1GB).
        mag = np.abs(librosa.stft(y, hop_length=_HOP))
        mag_h, mag_p = librosa.decompose.hpss(mag)
        del mag

        env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=_HOP)
        p_env = librosa.onset.onset_strength(S=librosa.amplitude_to_db(mag_p), sr=sr)
        tempo, beat_frames = librosa.beat.beat_track(
            onset_envelope=env, sr=sr, hop_length=_HOP, trim=False
        )
        beats = librosa.frames_to_time(beat_frames, sr=sr, hop_length=_HOP)

        # 드럼 타격 — 메인 리듬의 기준이자 비트 격자를 맞출 자.
        drum_frames = librosa.onset.onset_backtrack(
            librosa.onset.onset_detect(
                onset_envelope=p_env,
                sr=sr,
                hop_length=_HOP,
                backtrack=False,
                delta=0.05,
            ),
            p_env,
        )
        drum_frames = drum_frames[drum_frames < len(p_env)]
        drums = librosa.frames_to_time(drum_frames, sr=sr, hop_length=_HOP)

        # 비트는 onset 봉우리에 맞춰져 있어 실제 타격보다 늦다. 드럼에 얹히게 통째로 민다.
        if beats.size > 1:
            period = float(np.median(np.diff(beats)))
            beats = beats + _beat_offset(beats, drums, period)

        # 어려운 채보도 채울 수 있게 작은 봉우리까지 넉넉히 후보로 뽑는다.
        # 봉우리는 실제 타격보다 늦으므로 앞의 골로 되돌려 시작점을 쓴다.
        frames = librosa.onset.onset_backtrack(
            librosa.onset.onset_detect(
                onset_envelope=env,
                sr=sr,
                hop_length=_HOP,
                backtrack=False,
                wait=1,
                delta=0.02,
            ),
            env,
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
            onsets.append(
                Onset(
                    time=float(t),
                    strength=float(strength),
                    pitch=pc / 12.0,
                    sustain=float((end - slips - f) * _HOP / sr),
                )
            )

        return RhythmAnalysis(
            duration=duration,
            bpm=round(float(np.atleast_1d(tempo)[0]), 2),
            beats=[round(float(b), 4) for b in beats],
            onsets=onsets,
        )
