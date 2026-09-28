/**
 * 리듬 게임 판정·점수 규칙.
 *
 * 서버(woojeongai/apps/music_challenge/domain/services/rhythm_scoring.py)와 똑같은 규칙이다.
 * 랭킹에는 서버가 입력 기록으로 다시 계산한 점수만 오른다. 한쪽을 고치면 둘 다 고친다.
 *
 * - 판정 창: ±75ms COOL, ±130ms GOOD, ±185ms BAD, 밖이면 MISS
 *   (2026-09-28 난이도를 낮추려고 60/110/160 에서 넓혔다)
 * - 누르면 그 레인에서 창 안의 가장 이른 미판정 노트를 친다. 창 안에 없으면 아무 일 없음
 * - 롱노트는 머리·꼬리를 따로 판정. 끝까지 누르고 있으면 꼬리 COOL, 일찍 떼면 그만큼 낮아짐
 * - 콤보는 BAD·MISS 에서 끊김
 * - 점수(최대 1,000,000) = 900,000 × 정확도 + 100,000 × 최대 콤보 / 판정 수
 */

/** [시각(초), 레인, 롱노트 끝 시각 | null] */
export type RhythmNote = [number, number, number | null]
/** [레인, 누른 시각, 뗀 시각] — 곡 기준 초(지연 보정 후) */
export type RhythmPress = [number, number, number]

export type RhythmJudgement = "cool" | "good" | "bad" | "miss"

export const COOL_WINDOW = 0.075
export const GOOD_WINDOW = 0.13
export const BAD_WINDOW = 0.185

const WEIGHT: Record<RhythmJudgement, number> = { cool: 1, good: 0.6, bad: 0.2, miss: 0 }

export const RHYTHM_JUDGEMENT_LABEL: Record<RhythmJudgement, string> = {
  cool: "COOL",
  good: "GOOD",
  bad: "BAD",
  miss: "MISS",
}

export type RhythmResult = {
  score: number
  accuracy: number
  maxCombo: number
  counts: Record<RhythmJudgement, number>
  total: number
}

export function judgeOffset(delta: number): RhythmJudgement {
  const d = Math.abs(delta)
  if (d <= COOL_WINDOW) return "cool"
  if (d <= GOOD_WINDOW) return "good"
  if (d <= BAD_WINDOW) return "bad"
  return "miss"
}

export function judgeRelease(up: number, end: number): RhythmJudgement {
  return up >= end ? "cool" : judgeOffset(end - up)
}

/** 등급 — 화면 표시용. 서버에는 없다. */
export function rhythmGrade(accuracy: number): string {
  if (accuracy >= 95) return "S"
  if (accuracy >= 90) return "A"
  if (accuracy >= 80) return "B"
  if (accuracy >= 70) return "C"
  return "D"
}

/** 판정 수와 최대 콤보로 점수를 낸다. 게임 중 점수와 최종 점수가 같은 식을 쓴다. */
export function rhythmPoints(
  counts: Record<RhythmJudgement, number>,
  maxCombo: number,
  total: number
): { score: number; accuracy: number } {
  if (total === 0) return { score: 0, accuracy: 0 }
  const weighted =
    counts.cool * WEIGHT.cool + counts.good * WEIGHT.good + counts.bad * WEIGHT.bad
  const score = Math.round((900000 * weighted) / total + (100000 * maxCombo) / total)
  return {
    score: Math.min(1000000, score),
    accuracy: Math.round((weighted / total) * 10000) / 100,
  }
}

/** 입력 기록 전체로 최종 점수를 계산한다(서버 score_play 와 같은 순서·규칙). */
export function scoreRhythm(notes: RhythmNote[], presses: RhythmPress[]): RhythmResult {
  // [기준 시각, 레인, 꼬리 여부, 판정]
  const events: [number, number, number, RhythmJudgement][] = []
  const judged = new Array<boolean>(notes.length).fill(false)
  const byLane = new Map<number, number[]>()
  notes.forEach(([, lane], i) => {
    const list = byLane.get(lane)
    if (list) list.push(i)
    else byLane.set(lane, [i])
  })
  const cursor = new Map<number, number>()

  const sorted = [...presses].sort((a, b) => a[1] - b[1] || a[0] - b[0])
  for (const [lane, down, up] of sorted) {
    const idxs = byLane.get(lane)
    if (!idxs) continue
    let c = cursor.get(lane) ?? 0
    while (c < idxs.length && (judged[idxs[c]] || notes[idxs[c]][0] < down - BAD_WINDOW)) c++
    cursor.set(lane, c)
    if (c >= idxs.length || notes[idxs[c]][0] > down + BAD_WINDOW) continue
    const i = idxs[c]
    const [time, noteLane, end] = notes[i]
    judged[i] = true
    events.push([time, noteLane, 0, judgeOffset(down - time)])
    if (end !== null) events.push([end, noteLane, 1, judgeRelease(up, end)])
  }
  notes.forEach(([time, lane, end], i) => {
    if (judged[i]) return
    events.push([time, lane, 0, "miss"])
    if (end !== null) events.push([end, lane, 1, "miss"])
  })

  events.sort((a, b) => a[0] - b[0] || a[1] - b[1] || a[2] - b[2])
  const counts: Record<RhythmJudgement, number> = { cool: 0, good: 0, bad: 0, miss: 0 }
  let combo = 0
  let maxCombo = 0
  for (const [, , , j] of events) {
    counts[j]++
    if (j === "cool" || j === "good") {
      combo++
      maxCombo = Math.max(maxCombo, combo)
    } else {
      combo = 0
    }
  }
  const { score, accuracy } = rhythmPoints(counts, maxCombo, events.length)
  return { score, accuracy, maxCombo, counts, total: events.length }
}

/** 판정 수 — 머리 + 롱노트 꼬리 */
export function judgementCount(notes: RhythmNote[]): number {
  return notes.reduce((n, [, , end]) => n + (end === null ? 1 : 2), 0)
}

export type LiveHit = {
  lane: number
  judgement: RhythmJudgement
  /** 판정이 난 곡 위치(초) — 화면 효과의 시작 시각 */
  at: number
}

/**
 * 게임 중 실시간 판정. 최종 점수는 끝난 뒤 scoreRhythm 으로 다시 계산하므로
 * 여기서는 화면에 보일 판정·콤보만 정확하면 된다.
 */
export function createRhythmJudge(notes: RhythmNote[], keys: number) {
  const state = new Array<"open" | "hit" | "held" | "done">(notes.length).fill("open")
  const byLane: number[][] = Array.from({ length: keys }, () => [])
  notes.forEach(([, lane], i) => byLane[lane]?.push(i))
  const cursor = new Array<number>(keys).fill(0)
  const holding = new Array<number>(keys).fill(-1)
  // 아직 MISS 처리하지 않은 가장 이른 노트 — 곡 순서대로 훑는다.
  let missScan = 0
  const counts: Record<RhythmJudgement, number> = { cool: 0, good: 0, bad: 0, miss: 0 }
  let combo = 0
  let maxCombo = 0
  const total = judgementCount(notes)
  const hits: LiveHit[] = []

  const record = (lane: number, judgement: RhythmJudgement, at: number) => {
    counts[judgement]++
    if (judgement === "cool" || judgement === "good") {
      combo++
      maxCombo = Math.max(maxCombo, combo)
    } else {
      combo = 0
    }
    hits.push({ lane, judgement, at })
    if (hits.length > 64) hits.shift()
  }

  return {
    press(lane: number, t: number): number | null {
      const idxs = byLane[lane]
      if (!idxs) return null
      let c = cursor[lane]
      while (c < idxs.length && (state[idxs[c]] !== "open" || notes[idxs[c]][0] < t - BAD_WINDOW)) c++
      cursor[lane] = c
      if (c >= idxs.length || notes[idxs[c]][0] > t + BAD_WINDOW) return null
      const i = idxs[c]
      const [time, , end] = notes[i]
      record(lane, judgeOffset(t - time), t)
      state[i] = end === null ? "done" : "held"
      if (end !== null) holding[lane] = i
      return i
    },
    release(lane: number, t: number) {
      const i = holding[lane]
      if (i < 0) return
      holding[lane] = -1
      state[i] = "done"
      record(lane, judgeRelease(t, notes[i][2] ?? t), t)
    },
    /** 창을 지나간 노트는 MISS, 끝까지 누른 롱노트는 꼬리 COOL */
    tick(t: number) {
      for (let lane = 0; lane < keys; lane++) {
        const i = holding[lane]
        if (i >= 0 && (notes[i][2] ?? 0) <= t) {
          holding[lane] = -1
          state[i] = "done"
          record(lane, "cool", t)
        }
      }
      while (missScan < notes.length && notes[missScan][0] < t - BAD_WINDOW - 0.03) {
        if (state[missScan] === "open") {
          state[missScan] = "done"
          const [, lane, end] = notes[missScan]
          record(lane, "miss", t)
          if (end !== null) record(lane, "miss", t)
        }
        missScan++
      }
    },
    /** 화면용 — 치거나 놓친 노트는 그리지 않고, 누르고 있는 롱노트는 몸통만 그린다 */
    noteState(i: number) {
      return state[i]
    },
    isHolding(lane: number) {
      return holding[lane] >= 0
    },
    live() {
      const { score, accuracy } = rhythmPoints(counts, maxCombo, total)
      return { score, accuracy, combo, maxCombo, counts: { ...counts } }
    },
    hits,
  }
}

export type RhythmJudge = ReturnType<typeof createRhythmJudge>
export type RhythmLive = ReturnType<RhythmJudge["live"]>
