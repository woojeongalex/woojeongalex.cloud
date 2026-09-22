/**
 * 노래방·연주 실시간 채점.
 *
 * 화면이 매 프레임 "지금 곡 위치 + 지금 내 음높이"를 넣으면, 그 순간 불러야 할
 * 음표와 비교해 쌓는다. 음표가 끝나는 순간 그 음표의 판정이 확정된다.
 *
 * 규칙 (서버 재채점 music_challenge 의 karaoke 채점과 같은 값을 쓴다 — 바꾸면 양쪽 다)
 * - 옥타브는 따지지 않는다. 남자가 여자 노래를 한 옥타브 낮게 불러도 정답이다.
 * - 음정: 정답에서 ±50센트 안이면 온전히, ±100센트 안이면 절반만 인정한다.
 * - 박자: 음표가 시작되고 0.2초 안에 맞는 음을 내기 시작하면 제때 들어간 것이다.
 * - 음표 점수 = 음정 75% + 박자 25%. 긴 음표일수록 전체 점수에 크게 반영된다.
 */

import type { ChartNote } from "@/lib/music-challenge-api"

export const PERFECT_CENTS = 50
export const GOOD_CENTS = 100
export const TIMING_WINDOW_SEC = 0.2
const PITCH_WEIGHT = 0.75
const TIMING_WEIGHT = 0.25
// 탭이 뒤로 가 있다가 돌아오는 등 프레임 간격이 튀면 한 번에 쌓지 않는다.
const MAX_FRAME_SEC = 0.1
// 음표 경계에서 빠지는 프레임을 봐주는 폭 — 30fps 에서 두 프레임
const FRAME_SLACK_SEC = 1 / 30

export type Judgement = "perfect" | "great" | "good" | "miss"

export const JUDGEMENT_LABEL: Record<Judgement, string> = {
  perfect: "PERFECT",
  great: "GREAT",
  good: "GOOD",
  miss: "MISS",
}

export type NoteProgress = {
  /** 음정이 맞은 시간(초, 가중) */
  hit: number
  /** 이 음표 구간을 지나간 시간(초) */
  elapsed: number
  /** 처음 맞는 음을 낸 시각의 늦음(초). 아직 못 냈으면 null */
  onsetDelay: number | null
  judgement: Judgement | null
}

export type LiveScore = {
  /** 지나간 음표 기준 0~100 */
  score: number
  combo: number
  maxCombo: number
  counts: Record<Judgement, number>
  /** 방금 확정된 판정 — 화면에 잠깐 띄운다 */
  last: { index: number; judgement: Judgement } | null
}

export type FinalScore = {
  /** 곡 전체 기준 0~100. 부르지 않고 끝낸 음표는 0점으로 들어간다 */
  score: number
  /** 음정 맞은 비율 0~100 (길이 가중) */
  pitchAccuracy: number
  /** 제때 들어간 음표 비율 0~100 */
  timingAccuracy: number
  maxCombo: number
  counts: Record<Judgement, number>
  noteCount: number
}

/** 옥타브를 접은 음정 차이(반음). -6 이상 6 미만 */
export function foldedSemitones(userMidi: number, targetMidi: number): number {
  return ((((userMidi - targetMidi) % 12) + 18) % 12) - 6
}

/** 화면에 내 음높이를 정답 음표 곁에 그리기 위한, 옥타브를 맞춘 MIDI 값 */
export function foldToTarget(userMidi: number, targetMidi: number): number {
  return targetMidi + foldedSemitones(userMidi, targetMidi)
}

function judge(points: number): Judgement {
  if (points >= 0.9) return "perfect"
  if (points >= 0.7) return "great"
  if (points >= 0.4) return "good"
  return "miss"
}

function emptyCounts(): Record<Judgement, number> {
  return { perfect: 0, great: 0, good: 0, miss: 0 }
}

export function createKaraokeScorer(notes: ChartNote[]) {
  const progress: NoteProgress[] = notes.map(() => ({
    hit: 0,
    elapsed: 0,
    onsetDelay: null,
    judgement: null,
  }))
  const points: number[] = notes.map(() => 0)
  let cursor = 0 // 아직 확정되지 않은 첫 음표
  let lastTime: number | null = null
  let combo = 0
  let maxCombo = 0
  const counts = emptyCounts()
  let last: LiveScore["last"] = null

  // 프레임이 음표 경계를 걸치면 한 프레임씩 빠져서, 음표 길이로 나누면 완벽하게 불러도
  // 98점에 머문다. 그렇다고 지켜본 시간으로만 나누면 음표 중간에 멈춘 사람이 그 음표를
  // 다 부른 것으로 친다. 음표 길이에서 두 프레임(30fps 기준)만 봐준다.
  const pitchRatio = (i: number): number => {
    const note = notes[i]
    const p = progress[i]
    const denom = Math.max(p.elapsed, note.end - note.start - FRAME_SLACK_SEC)
    return denom > 0 ? Math.min(1, p.hit / denom) : 0
  }

  const notePoints = (i: number): number => {
    const p = progress[i]
    const onTime = p.onsetDelay !== null && p.onsetDelay <= TIMING_WINDOW_SEC
    return PITCH_WEIGHT * pitchRatio(i) + TIMING_WEIGHT * (onTime ? 1 : 0)
  }

  const settle = (i: number) => {
    const pts = notePoints(i)
    const j = judge(pts)
    points[i] = pts
    progress[i].judgement = j
    counts[j] += 1
    combo = j === "miss" ? 0 : combo + 1
    maxCombo = Math.max(maxCombo, combo)
    last = { index: i, judgement: j }
  }

  return {
    /** 매 프레임 호출. songTime 은 곡 기준 초, userMidi 는 음이 없으면 null */
    push(songTime: number, userMidi: number | null) {
      const dt = lastTime === null ? 0 : Math.min(MAX_FRAME_SEC, Math.max(0, songTime - lastTime))
      lastTime = songTime

      // 끝난 음표를 확정한다.
      while (cursor < notes.length && songTime >= notes[cursor].end) {
        settle(cursor)
        cursor += 1
      }
      if (cursor >= notes.length) return

      const note = notes[cursor]
      if (songTime < note.start || dt === 0) return

      const p = progress[cursor]
      p.elapsed += dt
      if (userMidi === null) return
      const cents = Math.abs(foldedSemitones(userMidi, note.midi)) * 100
      const credit = cents <= PERFECT_CENTS ? 1 : cents <= GOOD_CENTS ? 0.5 : 0
      if (credit > 0) {
        p.hit += dt * credit
        if (p.onsetDelay === null) p.onsetDelay = songTime - note.start
      }
    },

    live(): LiveScore {
      let weighted = 0
      let total = 0
      for (let i = 0; i < cursor; i++) {
        const d = notes[i].end - notes[i].start
        weighted += points[i] * d
        total += d
      }
      return {
        score: total > 0 ? Math.round((100 * weighted) / total) : 0,
        combo,
        maxCombo,
        counts: { ...counts },
        last,
      }
    },

    progress(i: number): NoteProgress {
      return progress[i]
    },

    /** 곡이 끝났거나 중간에 멈췄을 때. 남은 음표는 지금까지 쌓인 대로 확정한다 */
    finish(): FinalScore {
      while (cursor < notes.length) {
        settle(cursor)
        cursor += 1
      }
      let weighted = 0
      let pitchWeighted = 0
      let total = 0
      let onTime = 0
      notes.forEach((note, i) => {
        const d = note.end - note.start
        const p = progress[i]
        weighted += points[i] * d
        pitchWeighted += pitchRatio(i) * d
        total += d
        if (p.onsetDelay !== null && p.onsetDelay <= TIMING_WINDOW_SEC) onTime += 1
      })
      return {
        score: total > 0 ? Math.round((100 * weighted) / total) : 0,
        pitchAccuracy: total > 0 ? Math.round((100 * pitchWeighted) / total) : 0,
        timingAccuracy: notes.length ? Math.round((100 * onTime) / notes.length) : 0,
        maxCombo,
        counts: { ...counts },
        noteCount: notes.length,
      }
    },
  }
}

export type KaraokeScorer = ReturnType<typeof createKaraokeScorer>
