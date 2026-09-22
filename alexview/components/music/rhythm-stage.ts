/**
 * 리듬 게임 무대 — 위에서 떨어지는 노트를 캔버스에 직접 그린다(오투잼식 세로 레인).
 *
 * 초당 60번 다시 그리므로 React 를 거치지 않는다. 게임 화면이 매 프레임
 * drawRhythmStage 를 부르고, 점수 같은 글자만 React 가 드문드문 갱신한다.
 * 무대는 테마와 상관없이 늘 어둡다.
 */

import type { LiveHit, RhythmJudge, RhythmJudgement, RhythmNote } from "@/lib/rhythm-scoring"

export type RhythmFrame = {
  notes: RhythmNote[]
  /** 노트 시각만 뽑은 배열 — 보이는 구간을 이분 탐색으로 찾는다 */
  times: number[]
  keys: number
  keyLabels: string[]
  /** 판정 기준 곡 위치(초) */
  time: number
  /** 노트가 떨어지는 속도(px/초) */
  pixelsPerSecond: number
  judge: RhythmJudge
  pressed: boolean[]
  combo: number
}

/** 레인 사이 여백을 뺀 무대 너비(px)와 판정선 위치 — 터치 입력도 같은 값을 쓴다 */
export function stageLayout(cssW: number, cssH: number, keys: number) {
  const laneW = Math.min(keys === 4 ? 84 : 62, Math.floor((cssW - 16) / keys))
  const width = laneW * keys
  const left = Math.floor((cssW - width) / 2)
  const lineY = cssH - 96
  return { laneW, width, left, lineY }
}

const WHITE = "#f1e6ff" // 밤하늘 위 흰 노트
const BLUE = "#2ee6ff" // neon-cyan
const YELLOW = "#ff2e97" // neon-pink — 7키 가운데(Space)

function laneColor(keys: number, lane: number): string {
  if (keys === 4) return lane === 1 || lane === 2 ? BLUE : WHITE
  if (lane === 3) return YELLOW
  return lane % 2 === 1 ? BLUE : WHITE
}

const JUDGEMENT_COLOR: Record<RhythmJudgement, string> = {
  cool: "#2ee6ff", // neon-cyan
  good: "#3ddc97", // neon-green
  bad: "#ffd23f", // neon-yellow
  miss: "#ff4d6d",
}

const LABEL: Record<RhythmJudgement, string> = {
  cool: "COOL",
  good: "GOOD",
  bad: "BAD",
  miss: "MISS",
}

// 롱노트는 최대 6박이다. 이보다 먼저 시작한 노트는 화면에 남아 있을 수 없다.
const MAX_LONG_SEC = 5
const NOTE_H = 14
const HIT_FLASH_SEC = 0.22
const JUDGEMENT_SHOW_SEC = 0.6

let cachedFont: string | null = null

/** next/font 가 붙인 Orbitron 글꼴 이름. 캔버스는 CSS 변수를 못 읽어 한 번 꺼내 둔다. */
function displayFont(): string {
  if (cachedFont === null) {
    const v = getComputedStyle(document.documentElement).getPropertyValue("--font-orbitron-face").trim()
    cachedFont = v ? `${v}, ui-sans-serif, sans-serif` : "ui-sans-serif, system-ui, sans-serif"
  }
  return cachedFont
}

function lowerBound(arr: number[], x: number): number {
  let lo = 0
  let hi = arr.length
  while (lo < hi) {
    const mid = (lo + hi) >> 1
    if (arr[mid] < x) lo = mid + 1
    else hi = mid
  }
  return lo
}

function roundRect(g: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
  g.beginPath()
  g.roundRect(x, y, w, h, r)
  g.fill()
}

export function drawRhythmStage(canvas: HTMLCanvasElement, frame: RhythmFrame) {
  const dpr = window.devicePixelRatio || 1
  const cssW = canvas.clientWidth
  const cssH = canvas.clientHeight
  if (canvas.width !== Math.round(cssW * dpr) || canvas.height !== Math.round(cssH * dpr)) {
    canvas.width = Math.round(cssW * dpr)
    canvas.height = Math.round(cssH * dpr)
  }
  const g = canvas.getContext("2d")
  if (!g) return
  g.setTransform(dpr, 0, 0, dpr, 0, 0)

  const { keys, time, pixelsPerSecond: pps, judge } = frame
  const { laneW, width, left, lineY } = stageLayout(cssW, cssH, keys)

  // 바탕과 레인
  g.fillStyle = "#0d0619"
  g.fillRect(0, 0, cssW, cssH)
  g.fillStyle = "#07030f"
  g.fillRect(left, 0, width, cssH)
  for (let lane = 0; lane < keys; lane++) {
    const x = left + lane * laneW
    if (frame.pressed[lane]) {
      const beam = g.createLinearGradient(0, lineY, 0, lineY - 260)
      beam.addColorStop(0, `${laneColor(keys, lane)}55`)
      beam.addColorStop(1, `${laneColor(keys, lane)}00`)
      g.fillStyle = beam
      g.fillRect(x, lineY - 260, laneW, 260)
    }
    g.fillStyle = "rgba(180,76,255,0.22)"
    g.fillRect(x, 0, 1, cssH)
  }
  g.fillRect(left + width, 0, 1, cssH)

  // 노트 — 판정선 위(미래)에서 아래로 내려온다
  const lookAhead = lineY / pps
  const from = lowerBound(frame.times, time - MAX_LONG_SEC)
  const to = lowerBound(frame.times, time + lookAhead + 0.1)
  for (let i = from; i < to; i++) {
    const [t, lane, end] = frame.notes[i]
    const state = judge.noteState(i)
    if (state === "done") continue
    const x = left + lane * laneW
    const color = laneColor(keys, lane)
    const headY = lineY - (t - time) * pps
    if (end !== null) {
      const tailY = lineY - (end - time) * pps
      // 누르고 있으면 몸통이 판정선에서 줄어든다
      const bottom = state === "held" ? lineY : headY
      if (bottom < -NOTE_H) continue
      g.fillStyle = `${color}${state === "held" ? "aa" : "66"}`
      g.fillRect(x + laneW * 0.18, tailY, laneW * 0.64, bottom - tailY)
      g.fillStyle = color
      roundRect(g, x + 3, tailY - 4, laneW - 6, 8, 3)
      if (state === "held") continue
    }
    if (headY < -NOTE_H || headY > cssH) continue
    // 노트마다 은은한 네온 빛. 화면에 수십 개뿐이라 그리기 부담은 작다.
    g.save()
    g.shadowColor = color
    g.shadowBlur = 10
    g.fillStyle = color
    roundRect(g, x + 3, headY - NOTE_H / 2, laneW - 6, NOTE_H, 4)
    g.restore()
  }

  // 판정선
  g.save()
  g.shadowColor = "#ff2e97"
  g.shadowBlur = 18
  g.fillStyle = "#ff2e97"
  g.fillRect(left, lineY - 1.5, width, 3)
  g.restore()

  // 친 순간의 빛
  const hits: LiveHit[] = judge.hits
  let last: LiveHit | null = null
  for (const hit of hits) {
    const age = time - hit.at
    if (age < 0) continue
    if (!last || hit.at >= last.at) last = hit
    if (hit.judgement === "miss" || age > HIT_FLASH_SEC) continue
    const k = 1 - age / HIT_FLASH_SEC
    const cx = left + hit.lane * laneW + laneW / 2
    g.fillStyle = `rgba(255,255,255,${0.5 * k})`
    g.beginPath()
    g.arc(cx, lineY, laneW * (0.35 + 0.4 * (1 - k)), 0, Math.PI * 2)
    g.fill()
  }

  // 키 자리
  g.font = "600 14px ui-monospace, SFMono-Regular, Menlo, monospace"
  g.textAlign = "center"
  g.textBaseline = "middle"
  for (let lane = 0; lane < keys; lane++) {
    const x = left + lane * laneW
    const on = frame.pressed[lane]
    g.fillStyle = on ? laneColor(keys, lane) : "rgba(180,76,255,0.14)"
    roundRect(g, x + 4, lineY + 14, laneW - 8, 56, 8)
    g.fillStyle = on ? "#0d0619" : "rgba(241,230,255,0.6)"
    g.fillText(frame.keyLabels[lane] ?? "", x + laneW / 2, lineY + 42)
  }

  // 판정 글자와 콤보 — 무대 가운데 위쪽
  if (last && time - last.at < JUDGEMENT_SHOW_SEC) {
    const age = time - last.at
    const pop = age < 0.08 ? 1.25 - (age / 0.08) * 0.25 : 1
    const cx = left + width / 2
    const cy = lineY * 0.42
    g.save()
    g.translate(cx, cy)
    g.scale(pop, pop)
    g.fillStyle = JUDGEMENT_COLOR[last.judgement]
    g.font = `800 34px ${displayFont()}`
    g.shadowColor = JUDGEMENT_COLOR[last.judgement]
    g.shadowBlur = 16
    g.fillText(LABEL[last.judgement], 0, 0)
    if (frame.combo >= 2) {
      g.fillStyle = "rgba(255,255,255,0.9)"
      g.font = "700 22px ui-monospace, SFMono-Regular, Menlo, monospace"
      g.fillText(`${frame.combo} COMBO`, 0, 36)
    }
    g.restore()
  }
}
