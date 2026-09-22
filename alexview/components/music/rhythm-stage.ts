/**
 * 리듬 게임 무대 — 소실점에서 다가오는 3D 원근 레인(캔버스 2D 로 직접 그린다).
 *
 * 초당 60번 다시 그리므로 React 를 거치지 않는다. 게임 화면이 매 프레임
 * drawRhythmStage 를 부르고, 점수 같은 글자만 React 가 드문드문 갱신한다.
 *
 * 원근: 판정선에서 몇 초 뒤의 노트인지(dt)를 깊이 z(0~1)로 바꾸고,
 * 크기 s = 1 / (1 + K·z) 로 줄여 소실점 쪽으로 모은다. 판정은 시간으로만 하므로
 * 그림이 3D 여도 채점(서버와 같은 규칙)에는 영향이 없다.
 *
 * 타격감: 파편·충격파·레인 번쩍임·화면 흔들림·콤보 튕김·50콤보 효과·MISS 빨간 번쩍임.
 * 효과 상태(파편 등)는 캔버스마다 따로 들고 있고, 판정 기록(judge.hits)의 새 항목을 보고 만든다.
 */

import type { LiveHit, RhythmJudge, RhythmJudgement, RhythmNote } from "@/lib/rhythm-scoring"

export type RhythmFrame = {
  notes: RhythmNote[]
  /** 노트 시각만 뽑은 배열 — 보이는 구간을 이분 탐색으로 찾는다 */
  times: number[]
  keys: number
  keyLabels: string[]
  /** 판정 기준 곡 위치(초). 곡 시작 전 준비 시간에는 음수 */
  time: number
  /** 노트 속도 — 클수록 빨리 다가온다(설정의 배속 × 기준값) */
  pixelsPerSecond: number
  judge: RhythmJudge
  pressed: boolean[]
  combo: number
}

/** 판정선 높이에서의 레인 배치 — 터치 입력도 같은 값을 쓴다(판정선 근처를 누르므로). */
export function stageLayout(cssW: number, cssH: number, keys: number) {
  const laneW = Math.min(keys === 4 ? 96 : 70, Math.floor((cssW - 16) / keys))
  const width = laneW * keys
  const left = Math.floor((cssW - width) / 2)
  const lineY = cssH - 112
  return { laneW, width, left, lineY }
}

const WHITE = "#f1e6ff"
const CYAN = "#2ee6ff"
const PINK = "#ff2e97"

function laneColor(keys: number, lane: number): string {
  if (keys === 4) return lane === 1 || lane === 2 ? CYAN : WHITE
  if (lane === 3) return PINK
  return lane % 2 === 1 ? CYAN : WHITE
}

const JUDGEMENT_COLOR: Record<RhythmJudgement, string> = {
  cool: "#2ee6ff",
  good: "#3ddc97",
  bad: "#ffd23f",
  miss: "#ff4d6d",
}

const LABEL: Record<RhythmJudgement, string> = {
  cool: "COOL",
  good: "GOOD",
  bad: "BAD",
  miss: "MISS",
}

// 원근 세기 — 가장 먼 곳이 1/(1+K) 크기가 된다.
const PERSPECTIVE_K = 3.2
// 롱노트는 최대 6박이다. 이보다 먼저 시작한 노트는 화면에 남아 있을 수 없다.
const MAX_LONG_SEC = 5
const NOTE_H = 18
const JUDGEMENT_SHOW_SEC = 0.55
const FLOOR_STEP_SEC = 0.25

// ── 효과 상태 ─────────────────────────────────────────────────────────

type Particle = {
  x: number
  y: number
  vx: number
  vy: number
  life: number
  max: number
  size: number
  color: string
}

type Ring = { x: number; y: number; born: number; color: string; big: boolean }

type FxState = {
  seen: WeakSet<LiveHit>
  particles: Particle[]
  rings: Ring[]
  laneFlash: number[]
  shake: number
  missFlash: number
  comboPop: number
  milestone: number
  lastCombo: number
  lastNow: number
}

const fxByCanvas = new WeakMap<HTMLCanvasElement, FxState>()

function fxFor(canvas: HTMLCanvasElement, keys: number): FxState {
  let fx = fxByCanvas.get(canvas)
  if (!fx || fx.laneFlash.length !== keys) {
    fx = {
      seen: new WeakSet(),
      particles: [],
      rings: [],
      laneFlash: new Array<number>(keys).fill(0),
      shake: 0,
      missFlash: 0,
      comboPop: 0,
      milestone: 0,
      lastCombo: 0,
      lastNow: performance.now(),
    }
    fxByCanvas.set(canvas, fx)
  }
  return fx
}

/** 새 판이 시작될 때 이전 판의 파편·흔들림을 지운다. */
export function resetRhythmStage(canvas: HTMLCanvasElement) {
  fxByCanvas.delete(canvas)
}

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

/** "#rrggbb" → "rgba(r,g,b,a)" */
function alpha(hex: string, a: number): string {
  const n = parseInt(hex.slice(1), 16)
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${Math.max(0, Math.min(1, a))})`
}

/** 튀어나왔다가 살짝 되돌아오는 크기 변화(0→1 진행에 대해). */
function popScale(p: number, from: number): number {
  if (p >= 1) return 1
  const e = 1 - Math.pow(1 - p, 3)
  return from + (1 - from) * e + Math.sin(p * Math.PI) * 0.08
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

  const { keys, time, judge } = frame
  const { laneW, width, left, lineY } = stageLayout(cssW, cssH, keys)
  const cx = left + width / 2
  const fx = fxFor(canvas, keys)

  const now = performance.now()
  const dt = Math.min(0.05, Math.max(0, (now - fx.lastNow) / 1000))
  fx.lastNow = now

  // ── 원근 투영 ──
  // 가장 먼 레인 끝이 화면 위 40px 에 오도록 소실점 높이를 정한다.
  const farY = 40
  const horizonY = (farY * (1 + PERSPECTIVE_K) - lineY) / PERSPECTIVE_K
  const lookAhead = (lineY * 1.6) / frame.pixelsPerSecond
  const scaleAt = (secAhead: number) => {
    const z = Math.max(-0.28, secAhead / lookAhead)
    return 1 / (1 + PERSPECTIVE_K * z)
  }
  const yAt = (s: number) => horizonY + (lineY - horizonY) * s
  const xAt = (xLine: number, s: number) => cx + (xLine - cx) * s
  const laneX = (lane: number) => left + lane * laneW

  // ── 새 판정 → 효과 만들기 ──
  for (const hit of judge.hits) {
    if (fx.seen.has(hit)) continue
    fx.seen.add(hit)
    const hx = laneX(hit.lane) + laneW / 2
    if (hit.judgement === "miss") {
      fx.missFlash = 1
      continue
    }
    const color = hit.judgement === "cool" ? laneColor(keys, hit.lane) : JUDGEMENT_COLOR[hit.judgement]
    const count = hit.judgement === "cool" ? 18 : hit.judgement === "good" ? 12 : 6
    for (let i = 0; i < count; i++) {
      const ang = -Math.PI / 2 + (Math.random() - 0.5) * Math.PI * 1.1
      const speed = 180 + Math.random() * 360
      fx.particles.push({
        x: hx + (Math.random() - 0.5) * laneW * 0.5,
        y: lineY,
        vx: Math.cos(ang) * speed,
        vy: Math.sin(ang) * speed,
        life: 0,
        max: 0.35 + Math.random() * 0.3,
        size: 1.5 + Math.random() * 2.5,
        color: Math.random() < 0.3 ? "#ffffff" : color,
      })
    }
    fx.rings.push({ x: hx, y: lineY, born: now, color, big: false })
    fx.laneFlash[hit.lane] = 1
    fx.shake = Math.max(fx.shake, hit.judgement === "cool" ? 3 : 2)
  }
  if (frame.combo > fx.lastCombo) {
    fx.comboPop = 1
    if (Math.floor(frame.combo / 50) > Math.floor(fx.lastCombo / 50)) {
      fx.milestone = 1
      fx.shake = 9
      fx.rings.push({ x: cx, y: lineY, born: now, color: PINK, big: true })
    }
  }
  fx.lastCombo = frame.combo
  if (fx.particles.length > 400) fx.particles.splice(0, fx.particles.length - 400)

  // ── 화면 흔들림 ──
  g.setTransform(dpr, 0, 0, dpr, 0, 0)
  const shakeX = fx.shake > 0.1 ? (Math.random() - 0.5) * fx.shake * 2 : 0
  const shakeY = fx.shake > 0.1 ? (Math.random() - 0.5) * fx.shake * 2 : 0
  fx.shake *= Math.pow(0.001, dt)

  // 바탕 — 소실점 쪽이 은은하게 빛나는 밤하늘
  g.fillStyle = "#0d0619"
  g.fillRect(0, 0, cssW, cssH)
  const glow = g.createRadialGradient(cx, farY, 0, cx, farY, cssH * 0.7)
  glow.addColorStop(0, "rgba(255,46,151,0.22)")
  glow.addColorStop(0.4, "rgba(180,76,255,0.08)")
  glow.addColorStop(1, "rgba(13,6,25,0)")
  g.fillStyle = glow
  g.fillRect(0, 0, cssW, cssH)

  g.save()
  g.translate(shakeX, shakeY)

  // ── 레인 바닥(사다리꼴) ──
  const sFar = scaleAt(lookAhead)
  const sNear = scaleAt(-0.28 * lookAhead)
  const trapezoid = (x0: number, x1: number, sA: number, sB: number) => {
    g.beginPath()
    g.moveTo(xAt(x0, sA), yAt(sA))
    g.lineTo(xAt(x1, sA), yAt(sA))
    g.lineTo(xAt(x1, sB), yAt(sB))
    g.lineTo(xAt(x0, sB), yAt(sB))
    g.closePath()
  }
  const floor = g.createLinearGradient(0, farY, 0, lineY)
  floor.addColorStop(0, "rgba(18,6,42,0.2)")
  floor.addColorStop(1, "rgba(18,6,42,0.95)")
  g.fillStyle = floor
  trapezoid(left, left + width, sFar, sNear)
  g.fill()

  // 누른 레인의 빛기둥
  for (let lane = 0; lane < keys; lane++) {
    const flash = fx.laneFlash[lane]
    if (!frame.pressed[lane] && flash < 0.02) continue
    const color = laneColor(keys, lane)
    const beam = g.createLinearGradient(0, lineY, 0, yAt(scaleAt(lookAhead * 0.55)))
    beam.addColorStop(0, alpha(color, 0.35 + flash * 0.4))
    beam.addColorStop(1, alpha(color, 0))
    g.fillStyle = beam
    trapezoid(laneX(lane), laneX(lane) + laneW, scaleAt(lookAhead * 0.55), 1)
    g.fill()
  }
  for (let lane = 0; lane < keys; lane++) fx.laneFlash[lane] *= Math.pow(0.0005, dt)

  // 흘러가는 바닥 가로줄 — 속도감
  const phase = ((time % FLOOR_STEP_SEC) + FLOOR_STEP_SEC) % FLOOR_STEP_SEC
  for (let k = 0; k * FLOOR_STEP_SEC < lookAhead + FLOOR_STEP_SEC; k++) {
    const ahead = k * FLOOR_STEP_SEC - phase
    if (ahead < 0) continue
    const s = scaleAt(ahead)
    const beat = Math.round((time + ahead) / FLOOR_STEP_SEC) % 4 === 0
    g.strokeStyle = `rgba(180,76,255,${(beat ? 0.4 : 0.16) * s})`
    g.lineWidth = beat ? 1.5 : 1
    g.beginPath()
    g.moveTo(xAt(left, s), yAt(s))
    g.lineTo(xAt(left + width, s), yAt(s))
    g.stroke()
  }

  // 레인 경계선과 양옆 네온 레일
  for (let lane = 1; lane < keys; lane++) {
    g.strokeStyle = "rgba(180,76,255,0.28)"
    g.lineWidth = 1
    g.beginPath()
    g.moveTo(xAt(laneX(lane), sFar), yAt(sFar))
    g.lineTo(xAt(laneX(lane), sNear), yAt(sNear))
    g.stroke()
  }
  g.save()
  g.shadowColor = PINK
  g.shadowBlur = 14
  g.strokeStyle = PINK
  g.lineWidth = 2.5
  for (const x of [left, left + width]) {
    g.beginPath()
    g.moveTo(xAt(x, sFar), yAt(sFar))
    g.lineTo(xAt(x, sNear), yAt(sNear))
    g.stroke()
  }
  g.restore()

  // ── 노트 — 먼 것부터 그려야 가까운 노트가 위에 온다 ──
  const from = lowerBound(frame.times, time - MAX_LONG_SEC)
  const to = lowerBound(frame.times, time + lookAhead)
  let holdingAny = false
  for (let i = to - 1; i >= from; i--) {
    const [t, lane, end] = frame.notes[i]
    const state = judge.noteState(i)
    if (state === "done") continue
    const color = laneColor(keys, lane)
    const x0 = laneX(lane) + 4
    const x1 = laneX(lane) + laneW - 4
    const headAhead = t - time
    if (end !== null) {
      const tailAhead = Math.min(end - time, lookAhead)
      const bottomAhead = state === "held" ? 0 : headAhead
      if (tailAhead > bottomAhead) {
        const sT = scaleAt(tailAhead)
        const sB = scaleAt(Math.max(bottomAhead, -0.28 * lookAhead))
        const body = g.createLinearGradient(0, yAt(sT), 0, yAt(sB))
        body.addColorStop(0, alpha(color, 0.25))
        body.addColorStop(1, alpha(color, state === "held" ? 0.75 : 0.5))
        g.fillStyle = body
        const inset = laneW * 0.16
        trapezoid(x0 + inset, x1 - inset, sT, sB)
        g.fill()
        if (end - time <= lookAhead) drawNote(g, x0, x1, sT, color, 0.6)
      }
      if (state === "held") {
        holdingAny = true
        // 누르고 있는 동안 판정선에서 불꽃이 계속 튄다
        if (Math.random() < 0.6) {
          fx.particles.push({
            x: laneX(lane) + laneW / 2 + (Math.random() - 0.5) * laneW * 0.6,
            y: lineY,
            vx: (Math.random() - 0.5) * 120,
            vy: -120 - Math.random() * 220,
            life: 0,
            max: 0.25 + Math.random() * 0.2,
            size: 1.5 + Math.random() * 1.5,
            color,
          })
        }
        continue
      }
    }
    if (headAhead > lookAhead || headAhead < -0.28 * lookAhead) continue
    drawNote(g, x0, x1, scaleAt(headAhead), color, 1)
  }

  function drawNote(ctx: CanvasRenderingContext2D, xa: number, xb: number, s: number, color: string, a: number) {
    const y = yAt(s)
    const h = NOTE_H * s
    const l = xAt(xa, s)
    const r = xAt(xb, s)
    ctx.save()
    ctx.globalAlpha = a
    ctx.shadowColor = color
    ctx.shadowBlur = 14 * s
    // 앞면(어두운 두께) → 윗면(밝은 판) 순서로 그려 입체감을 낸다
    ctx.fillStyle = alpha(color, 0.55)
    ctx.beginPath()
    ctx.roundRect(l, y - h * 0.15, r - l, h * 0.55, 3 * s)
    ctx.fill()
    ctx.shadowBlur = 0
    const top = ctx.createLinearGradient(0, y - h * 0.6, 0, y + h * 0.1)
    top.addColorStop(0, "#ffffff")
    top.addColorStop(0.45, color)
    top.addColorStop(1, color)
    ctx.fillStyle = top
    ctx.beginPath()
    ctx.roundRect(l, y - h * 0.6, r - l, h * 0.6, 4 * s)
    ctx.fill()
    ctx.restore()
  }

  // ── 판정선 ──
  g.save()
  g.shadowColor = PINK
  g.shadowBlur = 22
  g.fillStyle = PINK
  g.fillRect(left - 6, lineY - 2, width + 12, 4)
  g.fillStyle = "rgba(255,255,255,0.85)"
  g.fillRect(left - 6, lineY - 0.5, width + 12, 1)
  g.restore()

  // ── 충격파 고리(판정선 위에 납작하게 — 바닥에 퍼지는 느낌) ──
  g.save()
  g.globalCompositeOperation = "lighter"
  fx.rings = fx.rings.filter((ring) => {
    const age = (now - ring.born) / 1000
    const life = ring.big ? 0.6 : 0.32
    if (age > life) return false
    const p = age / life
    const radius = (ring.big ? width * 0.75 : laneW * 0.9) * (0.3 + p)
    g.strokeStyle = alpha(ring.color, (1 - p) * (ring.big ? 0.8 : 0.9))
    g.lineWidth = (ring.big ? 6 : 3) * (1 - p) + 1
    g.beginPath()
    g.ellipse(ring.x, ring.y, radius, radius * 0.32, 0, 0, Math.PI * 2)
    g.stroke()
    return true
  })

  // ── 파편 ──
  for (const pt of fx.particles) {
    pt.life += dt
    pt.x += pt.vx * dt
    pt.y += pt.vy * dt
    pt.vy += 900 * dt
    pt.vx *= Math.pow(0.2, dt)
  }
  fx.particles = fx.particles.filter((pt) => pt.life < pt.max)
  for (const pt of fx.particles) {
    const k = 1 - pt.life / pt.max
    g.fillStyle = alpha(pt.color, k)
    g.beginPath()
    g.arc(pt.x, pt.y, pt.size * (0.6 + k * 0.6), 0, Math.PI * 2)
    g.fill()
  }
  g.restore()

  // ── 키(입체 버튼) — 누르면 눌려 들어간다 ──
  const keyTop = lineY + 16
  const keyH = 64
  g.textAlign = "center"
  g.textBaseline = "middle"
  for (let lane = 0; lane < keys; lane++) {
    const x = laneX(lane) + 5
    const w = laneW - 10
    const on = frame.pressed[lane]
    const color = laneColor(keys, lane)
    const press = on ? 5 : 0
    // 옆면(두께)
    g.fillStyle = on ? alpha(color, 0.45) : "rgba(59,29,102,0.9)"
    g.beginPath()
    g.roundRect(x, keyTop + 8, w, keyH - 8, 10)
    g.fill()
    // 윗면
    g.save()
    if (on) {
      g.shadowColor = color
      g.shadowBlur = 20
    }
    const face = g.createLinearGradient(0, keyTop + press, 0, keyTop + press + keyH - 12)
    face.addColorStop(0, on ? "#ffffff" : "rgba(90,45,153,0.55)")
    face.addColorStop(1, on ? color : "rgba(34,16,63,0.95)")
    g.fillStyle = face
    g.beginPath()
    g.roundRect(x, keyTop + press, w, keyH - 12, 10)
    g.fill()
    g.restore()
    g.fillStyle = on ? "#0d0619" : "rgba(241,230,255,0.75)"
    g.font = `700 ${keys === 4 ? 22 : 15}px ${displayFont()}`
    g.fillText(frame.keyLabels[lane] ?? "", x + w / 2, keyTop + press + (keyH - 12) / 2 + 1)
  }

  g.restore() // 흔들림 끝

  // 아래 글자들은 모두 가운데 정렬 — save/restore 로 위의 설정이 풀렸으므로 다시 정한다
  g.textAlign = "center"
  g.textBaseline = "middle"

  // ── 판정 글자·콤보(흔들림과 무관하게 또렷하게) ──
  let last: LiveHit | null = null
  for (const hit of judge.hits) if (!last || hit.at >= last.at) last = hit
  const textY = yAt(scaleAt(lookAhead * 0.3))
  if (last && time - last.at >= 0 && time - last.at < JUDGEMENT_SHOW_SEC) {
    const age = time - last.at
    const p = Math.min(1, age / 0.14)
    const scale = popScale(p, 1.7)
    const fade = age > JUDGEMENT_SHOW_SEC - 0.15 ? (JUDGEMENT_SHOW_SEC - age) / 0.15 : 1
    const color = JUDGEMENT_COLOR[last.judgement]
    g.save()
    g.translate(cx, textY)
    g.scale(scale, scale)
    g.globalAlpha = fade
    g.font = `900 44px ${displayFont()}`
    g.lineJoin = "round"
    g.lineWidth = 6
    g.strokeStyle = "rgba(13,6,25,0.85)"
    g.strokeText(LABEL[last.judgement], 0, 0)
    g.shadowColor = color
    g.shadowBlur = 24
    const fill = g.createLinearGradient(0, -22, 0, 22)
    fill.addColorStop(0, "#ffffff")
    fill.addColorStop(0.5, color)
    fill.addColorStop(1, color)
    g.fillStyle = fill
    g.fillText(LABEL[last.judgement], 0, 0)
    g.restore()
  }
  if (frame.combo >= 2) {
    const s = 1 + fx.comboPop * 0.35
    g.save()
    g.translate(cx, textY + 58)
    g.scale(s, s)
    g.font = `800 34px ${displayFont()}`
    g.lineWidth = 5
    g.strokeStyle = "rgba(13,6,25,0.8)"
    g.strokeText(String(frame.combo), 0, 0)
    g.shadowColor = PINK
    g.shadowBlur = 18
    g.fillStyle = "#ffffff"
    g.fillText(String(frame.combo), 0, 0)
    g.shadowBlur = 0
    g.font = `700 12px ${displayFont()}`
    g.fillStyle = "rgba(255,46,151,0.95)"
    g.fillText("COMBO", 0, 26)
    g.restore()
  }
  fx.comboPop *= Math.pow(0.0001, dt)

  // 50콤보마다 — 크게 번쩍
  if (fx.milestone > 0.02) {
    const m = fx.milestone
    g.save()
    g.globalAlpha = m
    g.translate(cx, textY - 70)
    const sc = 1 + (1 - m) * 0.6
    g.scale(sc, sc)
    g.font = `900 30px ${displayFont()}`
    g.shadowColor = "#ffd23f"
    g.shadowBlur = 30
    g.fillStyle = "#ffd23f"
    g.fillText(`${Math.floor(frame.combo / 50) * 50} COMBO!`, 0, 0)
    g.restore()
    fx.milestone *= Math.pow(0.05, dt)
  }

  // MISS — 가장자리가 붉게 번쩍
  if (fx.missFlash > 0.02) {
    const v = g.createRadialGradient(cx, cssH / 2, cssH * 0.25, cx, cssH / 2, cssH * 0.8)
    v.addColorStop(0, "rgba(255,77,109,0)")
    v.addColorStop(1, `rgba(255,77,109,${0.35 * fx.missFlash})`)
    g.fillStyle = v
    g.fillRect(0, 0, cssW, cssH)
    fx.missFlash *= Math.pow(0.002, dt)
  }

  // 롱노트를 잡고 있으면 판정선이 더 밝게 숨쉰다
  if (holdingAny) {
    g.save()
    g.globalAlpha = 0.25 + 0.15 * Math.sin(now / 60)
    g.fillStyle = "#ffffff"
    g.fillRect(left, lineY - 1, width, 2)
    g.restore()
  }

  // 곡 시작 전 — READY / GO!
  if (time < 0.35) {
    const ready = time < -0.45
    const label = ready ? "READY" : "GO!"
    const p = ready ? (Math.sin(now / 180) + 1) / 2 : Math.min(1, (time + 0.45) / 0.8)
    g.save()
    g.translate(cx, cssH * 0.38)
    const sc = ready ? 1 + p * 0.05 : 1 + p * 0.8
    g.scale(sc, sc)
    g.globalAlpha = ready ? 0.85 : 1 - p
    g.font = `900 54px ${displayFont()}`
    g.shadowColor = ready ? CYAN : PINK
    g.shadowBlur = 30
    g.fillStyle = "#ffffff"
    g.fillText(label, 0, 0)
    g.restore()
  }
}
