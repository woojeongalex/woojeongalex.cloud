/**
 * 실시간 음높이 감지 — YIN 알고리즘 (de Cheveigné & Kawahara, 2002).
 *
 * 마이크에서 매 화면 갱신마다 한 프레임(약 40ms)을 받아 기본 주파수를 찾는다.
 * FFT 최고점 방식은 배음이 센 목소리·기타에서 한 옥타브 위를 자주 잡는데,
 * YIN 은 주기 자체를 찾으므로 그 실수가 적다.
 *
 * 계산량을 줄이려고 2배 솎아 낸 뒤 계산한다. 48kHz → 24kHz 여도 C7(2093Hz)까지는
 * 넉넉히 잡힌다.
 */

export type PitchReading = {
  hz: number
  /** MIDI 번호(실수). 69 = A4(440Hz) */
  midi: number
  /** 0~1. 주기성이 뚜렷할수록 1에 가깝다 */
  clarity: number
}

const DEFAULT_MIN_HZ = 65 // C2
const DEFAULT_MAX_HZ = 2100 // C7 조금 위
const YIN_THRESHOLD = 0.15
// 이보다 작은 소리는 무음으로 본다(대략 -45dBFS).
const MIN_RMS = 0.006

export type PitchDetectOptions = {
  minHz?: number
  maxHz?: number
}

export function hzToMidi(hz: number): number {
  return 69 + 12 * Math.log2(hz / 440)
}

export function detectPitch(
  input: Float32Array,
  sampleRate: number,
  options: PitchDetectOptions = {}
): PitchReading | null {
  const minHz = options.minHz ?? DEFAULT_MIN_HZ
  const maxHz = options.maxHz ?? DEFAULT_MAX_HZ

  // 2배 솎아내기 — 이웃 두 샘플 평균이 간단한 저역 통과 역할도 한다.
  const n = Math.floor(input.length / 2)
  const x = new Float32Array(n)
  let energy = 0
  for (let i = 0; i < n; i++) {
    const v = (input[2 * i] + input[2 * i + 1]) * 0.5
    x[i] = v
    energy += v * v
  }
  if (Math.sqrt(energy / n) < MIN_RMS) return null

  const sr = sampleRate / 2
  const tauMin = Math.max(2, Math.floor(sr / maxHz))
  const tauMax = Math.min(Math.floor(n / 2), Math.ceil(sr / minHz))
  if (tauMax <= tauMin) return null
  const w = n - tauMax

  // 1) 차이 함수, 2) 누적 평균으로 정규화
  const d = new Float32Array(tauMax + 1)
  for (let tau = 1; tau <= tauMax; tau++) {
    let sum = 0
    for (let i = 0; i < w; i++) {
      const diff = x[i] - x[i + tau]
      sum += diff * diff
    }
    d[tau] = sum
  }
  const cmnd = new Float32Array(tauMax + 1)
  cmnd[0] = 1
  let running = 0
  for (let tau = 1; tau <= tauMax; tau++) {
    running += d[tau]
    cmnd[tau] = running > 0 ? (d[tau] * tau) / running : 1
  }

  // 3) 임계값 아래로 처음 내려간 골짜기의 바닥
  let tau = -1
  for (let t = tauMin; t <= tauMax; t++) {
    if (cmnd[t] < YIN_THRESHOLD) {
      while (t + 1 <= tauMax && cmnd[t + 1] < cmnd[t]) t++
      tau = t
      break
    }
  }
  if (tau === -1) return null

  // 4) 포물선 보간으로 샘플 사이 위치까지
  let refined = tau
  if (tau > 1 && tau < tauMax) {
    const a = cmnd[tau - 1]
    const b = cmnd[tau]
    const c = cmnd[tau + 1]
    const denom = a + c - 2 * b
    if (denom !== 0) refined = tau + (a - c) / (2 * denom)
  }

  const hz = sr / refined
  if (hz < minHz || hz > maxHz) return null
  return { hz, midi: hzToMidi(hz), clarity: 1 - cmnd[tau] }
}
