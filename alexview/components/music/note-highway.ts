/**
 * 노래방·연주 화면의 음표 흐름 — 캔버스에 직접 그린다.
 *
 * 초당 60번 다시 그려야 해서 React 렌더링을 거치지 않는다. 화면(player)이 매
 * 프레임 drawHighway 를 부르고, 점수·가사 같은 글자만 React 가 드문드문 갱신한다.
 *
 * 무대는 테마와 상관없이 늘 어둡다. 음표가 가장 잘 보이고, 브랜드 강조색(sky)은
 * "맞았다"는 신호에만 쓴다.
 */

import type { Judgement, NoteProgress } from "@/lib/karaoke-scoring"
import type { ChartNote } from "@/lib/music-challenge-api"
import { isBlackKey, midiToName } from "@/lib/music-notes"

export type TrailPoint = { t: number; midi: number | null }

export type HighwayFrame = {
  notes: ChartNote[]
  /** 화면 기준 곡 위치(초) */
  time: number
  lo: number
  hi: number
  trail: TrailPoint[]
  progress: (i: number) => NoteProgress
}

const PAST_SEC = 2
const FUTURE_SEC = 4
const PLAYHEAD_RATIO = PAST_SEC / (PAST_SEC + FUTURE_SEC)

const COLOR = {
  stage: "#09090b", // zinc-950
  laneDark: "rgba(255,255,255,0.035)",
  gridLabel: "rgba(255,255,255,0.35)",
  upcoming: "rgba(255,255,255,0.28)",
  active: "rgba(255,255,255,0.9)",
  hitFill: "#0ea5e9", // sky-500
  playhead: "rgba(14,165,233,0.9)",
  trail: "#38bdf8", // sky-400
}

const JUDGED: Record<Judgement, string> = {
  perfect: "rgba(14,165,233,0.85)",
  great: "rgba(34,197,94,0.75)",
  good: "rgba(234,179,8,0.65)",
  miss: "rgba(239,68,68,0.35)",
}

export function drawHighway(canvas: HTMLCanvasElement, frame: HighwayFrame) {
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

  const { notes, time, lo, hi, trail, progress } = frame
  const rows = hi - lo + 1
  const rowH = cssH / rows
  const playX = cssW * PLAYHEAD_RATIO
  const pxPerSec = cssW / (PAST_SEC + FUTURE_SEC)
  const x = (t: number) => playX + (t - time) * pxPerSec
  const y = (midi: number) => (hi - midi) * rowH

  g.fillStyle = COLOR.stage
  g.fillRect(0, 0, cssW, cssH)

  // 검은 건반 줄무늬 + 도(C) 눈금
  for (let m = lo; m <= hi; m++) {
    if (isBlackKey(m)) {
      g.fillStyle = COLOR.laneDark
      g.fillRect(0, y(m), cssW, rowH)
    }
    if (m % 12 === 0) {
      g.fillStyle = COLOR.gridLabel
      g.font = "10px ui-monospace, monospace"
      g.fillText(midiToName(m), 4, y(m) + rowH - 2)
    }
  }

  const barH = Math.max(4, rowH * 0.8)
  const tStart = time - PAST_SEC
  const tEnd = time + FUTURE_SEC
  notes.forEach((note, i) => {
    if (note.end < tStart || note.start > tEnd) return
    const nx = x(note.start)
    const nw = Math.max(3, (note.end - note.start) * pxPerSec)
    const ny = y(note.midi) + (rowH - barH) / 2
    const p = progress(i)
    const radius = Math.min(barH / 2, 6)

    g.fillStyle = p.judgement
      ? JUDGED[p.judgement]
      : note.start <= time && time < note.end
        ? COLOR.active
        : COLOR.upcoming
    roundRect(g, nx, ny, nw, barH, radius)
    g.fill()

    // 지금 부르는 음표는 맞은 만큼 강조색으로 채운다.
    if (!p.judgement && note.start <= time && p.elapsed > 0) {
      const ratio = Math.min(1, p.hit / (note.end - note.start))
      g.fillStyle = COLOR.hitFill
      roundRect(g, nx, ny, nw * ratio, barH, radius)
      g.fill()
    }
  })

  // 내 목소리 선 — 끊긴 곳(음이 아닌 순간)에서는 선을 떼어 그린다.
  g.strokeStyle = COLOR.trail
  g.lineWidth = 3
  g.lineCap = "round"
  g.lineJoin = "round"
  g.beginPath()
  let pen = false
  for (const pt of trail) {
    if (pt.t < tStart || pt.midi === null) {
      pen = false
      continue
    }
    const px = x(pt.t)
    const py = y(pt.midi) + rowH / 2
    if (pen) g.lineTo(px, py)
    else g.moveTo(px, py)
    pen = true
  }
  g.stroke()

  g.strokeStyle = COLOR.playhead
  g.lineWidth = 2
  g.beginPath()
  g.moveTo(playX, 0)
  g.lineTo(playX, cssH)
  g.stroke()
}

function roundRect(
  g: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  r: number
) {
  const rr = Math.min(r, w / 2, h / 2)
  g.beginPath()
  g.moveTo(x + rr, y)
  g.arcTo(x + w, y, x + w, y + h, rr)
  g.arcTo(x + w, y + h, x, y + h, rr)
  g.arcTo(x, y + h, x, y, rr)
  g.arcTo(x, y, x + w, y, rr)
  g.closePath()
}

/** 곡 음역에 위아래 여유를 둔 표시 범위. 한 옥타브보다 좁으면 한 옥타브로 넓힌다 */
export function highwayRange(notes: ChartNote[]): { lo: number; hi: number } {
  if (notes.length === 0) return { lo: 55, hi: 72 }
  let lo = Math.min(...notes.map((n) => n.midi)) - 3
  let hi = Math.max(...notes.map((n) => n.midi)) + 3
  if (hi - lo < 14) {
    const mid = Math.round((lo + hi) / 2)
    lo = mid - 7
    hi = mid + 7
  }
  return { lo, hi }
}
