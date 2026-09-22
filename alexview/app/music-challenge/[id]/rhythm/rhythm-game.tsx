"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import Link from "next/link"
import { ArrowLeft, Keyboard, Loader2, Play, Square } from "lucide-react"
import { LoadingBlock, StatusNote } from "@/components/common/status-note"
import { RhythmRankingList } from "@/components/music/rhythm-ranking"
import { drawRhythmStage, stageLayout } from "@/components/music/rhythm-stage"
import { fetchChallenge, type Challenge } from "@/lib/music-challenge-api"
import {
  RHYTHM_DIFFICULTIES,
  RHYTHM_DIFFICULTY_LABEL,
  RHYTHM_KEYS,
  RHYTHM_KEY_CODES,
  RHYTHM_KEY_LABELS,
  fetchRhythmChart,
  fetchRhythmSheet,
  submitRhythmPlay,
  type RhythmChart,
  type RhythmDifficulty,
  type RhythmKeys,
  type RhythmPlayResult,
  type RhythmSheet,
} from "@/lib/rhythm-api"
import {
  createRhythmJudge,
  scoreRhythm,
  type RhythmJudge,
  type RhythmLive,
  type RhythmPress,
  type RhythmResult,
} from "@/lib/rhythm-scoring"
import { toUserFacingMessage, UI_ERRORS } from "@/lib/user-facing-error"
import { cn } from "@/lib/utils"
import { RhythmResultPanel } from "./rhythm-result-panel"

type Phase = "setup" | "loading" | "playing" | "finished"

// 곡을 틀기 전 노트가 위에서 내려올 시간(초). 이 동안 곡 위치는 음수다.
const PREROLL_SEC = 2
const TICK_MS = 10
const UI_REFRESH_MS = 100
// 오디오 위치와 게임 시계가 이만큼 어긋나면 곧바로 맞춘다(초). 그 아래는 조금씩 당긴다.
const HARD_RESYNC_SEC = 0.06
const SOFT_RESYNC = 0.02
const BASE_PPS = 240

const PREFS_KEY = "iuem-rhythm-prefs"
const OFFSET_LIMIT_MS = 300

type Prefs = {
  keys: RhythmKeys
  difficulty: RhythmDifficulty
  speed: number
  offsetMs: number
}

const DEFAULT_PREFS: Prefs = { keys: 4, difficulty: "normal", speed: 2.5, offsetMs: 0 }

function readPrefs(): Prefs {
  try {
    const raw = JSON.parse(localStorage.getItem(PREFS_KEY) ?? "{}") as Partial<Prefs>
    return {
      keys: raw.keys === 7 ? 7 : 4,
      difficulty: RHYTHM_DIFFICULTIES.includes(raw.difficulty as RhythmDifficulty)
        ? (raw.difficulty as RhythmDifficulty)
        : DEFAULT_PREFS.difficulty,
      speed: Number.isFinite(raw.speed) ? Math.min(5, Math.max(1, Number(raw.speed))) : 2.5,
      offsetMs: Number.isFinite(raw.offsetMs)
        ? Math.min(OFFSET_LIMIT_MS, Math.max(-OFFSET_LIMIT_MS, Number(raw.offsetMs)))
        : 0,
    }
  } catch {
    return DEFAULT_PREFS
  }
}

function savePrefs(prefs: Prefs) {
  try {
    localStorage.setItem(PREFS_KEY, JSON.stringify(prefs))
  } catch {
    // 저장하지 못해도 이번 판에는 적용된다.
  }
}

type RhythmGameProps = {
  challengeId: number
}

export function RhythmGame({ challengeId }: RhythmGameProps) {
  const [challenge, setChallenge] = useState<Challenge | null>(null)
  const [chart, setChart] = useState<RhythmChart | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [prefs, setPrefs] = useState<Prefs>(DEFAULT_PREFS)
  const [phase, setPhase] = useState<Phase>("setup")
  const [sheet, setSheet] = useState<RhythmSheet | null>(null)
  const [live, setLive] = useState<RhythmLive | null>(null)
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState<RhythmResult | null>(null)
  const [server, setServer] = useState<RhythmPlayResult | null>(null)
  const [sending, setSending] = useState(false)
  const [sendError, setSendError] = useState<string | null>(null)
  const [rankingKey, setRankingKey] = useState(0)

  const audioRef = useRef<HTMLAudioElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const judgeRef = useRef<RhythmJudge | null>(null)
  const sheetRef = useRef<RhythmSheet | null>(null)
  const timesRef = useRef<number[]>([])
  const pressesRef = useRef<RhythmPress[]>([])
  const openPressRef = useRef<number[]>([])
  const pressedRef = useRef<boolean[]>([])
  const pointerLaneRef = useRef(new Map<number, number>())
  // 곡 위치 0초에 해당하는 performance.now() 값. 키 입력 시각도 이 기준으로 바꾼다.
  const zeroRef = useRef(0)
  const audioStartedRef = useRef(false)
  const offsetRef = useRef(0)
  const speedRef = useRef(2.5)
  const tickRef = useRef<number | undefined>(undefined)
  const rafRef = useRef(0)
  const lastUiRef = useRef(0)
  const playingRef = useRef(false)

  useEffect(() => {
    const saved = readPrefs()
    setPrefs(saved)
  }, [])

  useEffect(() => {
    offsetRef.current = prefs.offsetMs
    speedRef.current = prefs.speed
  }, [prefs])

  useEffect(() => {
    let alive = true
    Promise.all([fetchChallenge(challengeId), fetchRhythmChart(challengeId)])
      .then(([c, r]) => {
        if (!alive) return
        setChallenge(c)
        setChart(r)
      })
      .catch((e) => {
        if (alive) setLoadError(toUserFacingMessage(e, UI_ERRORS.challengeLoadFailed))
      })
    return () => {
      alive = false
    }
  }, [challengeId])

  const updatePrefs = (patch: Partial<Prefs>) => {
    setPrefs((p) => {
      const next = { ...p, ...patch }
      savePrefs(next)
      return next
    })
  }

  /** 판정 기준 곡 위치 = 게임 시계 − 사용자 싱크 보정 */
  const songTime = useCallback(
    (perfTs: number) => (perfTs - zeroRef.current) / 1000 - offsetRef.current / 1000,
    []
  )

  const stopLoops = () => {
    clearInterval(tickRef.current)
    cancelAnimationFrame(rafRef.current)
  }

  const submit = useCallback(
    async (s: RhythmSheet, presses: RhythmPress[]) => {
      setSending(true)
      setSendError(null)
      try {
        const r = await submitRhythmPlay({
          challengeId,
          keys: s.keys,
          difficulty: s.difficulty,
          presses,
        })
        setServer(r)
        setRankingKey((k) => k + 1)
      } catch (e) {
        setSendError(toUserFacingMessage(e, UI_ERRORS.requestFailed))
      } finally {
        setSending(false)
      }
    },
    [challengeId]
  )

  const finish = useCallback(() => {
    if (!playingRef.current) return
    playingRef.current = false
    stopLoops()
    const audio = audioRef.current
    if (audio) {
      audio.onended = null
      audio.pause()
    }
    const s = sheetRef.current
    if (!s) return
    // 누른 채 끝났으면 지금 뗀 것으로 본다.
    const t = songTime(performance.now())
    openPressRef.current.forEach((idx) => {
      if (idx >= 0) pressesRef.current[idx][2] = Math.max(pressesRef.current[idx][1], t)
    })
    const presses = pressesRef.current.map((p) => [...p] as RhythmPress)
    setResult(scoreRhythm(s.notes, presses))
    setServer(null)
    setPhase("finished")
    void submit(s, presses)
  }, [songTime, submit])

  // ── 입력 ────────────────────────────────────────────────────────────
  const pressLane = useCallback(
    (lane: number, perfTs: number) => {
      const judge = judgeRef.current
      if (!playingRef.current || !judge || pressedRef.current[lane]) return
      const t = songTime(perfTs)
      pressedRef.current[lane] = true
      openPressRef.current[lane] = pressesRef.current.length
      pressesRef.current.push([lane, t, t])
      judge.press(lane, t)
    },
    [songTime]
  )

  const releaseLane = useCallback(
    (lane: number, perfTs: number) => {
      const judge = judgeRef.current
      if (!judge || !pressedRef.current[lane]) return
      const t = songTime(perfTs)
      pressedRef.current[lane] = false
      const idx = openPressRef.current[lane]
      if (idx >= 0) pressesRef.current[idx][2] = Math.max(pressesRef.current[idx][1], t)
      openPressRef.current[lane] = -1
      judge.release(lane, t)
    },
    [songTime]
  )

  useEffect(() => {
    if (phase !== "playing" || !sheet) return
    const codes = RHYTHM_KEY_CODES[sheet.keys]
    const keys = RHYTHM_KEY_LABELS[sheet.keys].map((l) => (l === "␣" ? " " : l.toLowerCase()))
    // 자판 배열과 상관없이 같은 자리를 쓰도록 code 로 찾고, code 가 비어 있는 입력기만 key 로 찾는다.
    const laneOf = (e: KeyboardEvent) =>
      e.code ? codes.indexOf(e.code) : keys.indexOf(e.key.toLowerCase())
    const onDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" || e.code === "Escape") {
        finish()
        return
      }
      const lane = laneOf(e)
      if (lane < 0) return
      e.preventDefault()
      if (e.repeat) return
      pressLane(lane, e.timeStamp)
    }
    const onUp = (e: KeyboardEvent) => {
      const lane = laneOf(e)
      if (lane < 0) return
      e.preventDefault()
      releaseLane(lane, e.timeStamp)
    }
    // 창을 벗어나면 keyup 이 오지 않는다. 누르고 있던 레인을 모두 뗀 것으로 본다.
    const onBlur = () => {
      const now = performance.now()
      for (let lane = 0; lane < sheet.keys; lane++) releaseLane(lane, now)
    }
    window.addEventListener("keydown", onDown)
    window.addEventListener("keyup", onUp)
    window.addEventListener("blur", onBlur)
    return () => {
      window.removeEventListener("keydown", onDown)
      window.removeEventListener("keyup", onUp)
      window.removeEventListener("blur", onBlur)
    }
  }, [phase, sheet, finish, pressLane, releaseLane])

  const laneAt = (e: React.PointerEvent<HTMLCanvasElement>): number | null => {
    const s = sheetRef.current
    const canvas = canvasRef.current
    if (!s || !canvas) return null
    const rect = canvas.getBoundingClientRect()
    const { laneW, left } = stageLayout(rect.width, rect.height, s.keys)
    const lane = Math.floor((e.clientX - rect.left - left) / laneW)
    return lane >= 0 && lane < s.keys ? lane : null
  }

  const onPointerDown = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const lane = laneAt(e)
    if (lane === null) return
    try {
      // 손가락이 레인 밖으로 미끄러져도 뗄 때 이벤트를 받는다.
      e.currentTarget.setPointerCapture(e.pointerId)
    } catch {
      // 캡처할 수 없는 포인터여도 누름 자체는 처리한다.
    }
    pointerLaneRef.current.set(e.pointerId, lane)
    pressLane(lane, e.timeStamp)
  }

  const onPointerUp = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const lane = pointerLaneRef.current.get(e.pointerId)
    if (lane === undefined) return
    pointerLaneRef.current.delete(e.pointerId)
    releaseLane(lane, e.timeStamp)
  }

  // ── 시계·판정·그리기 ────────────────────────────────────────────────
  /**
   * 게임 시계는 performance.now() 로 흐르고, 오디오 위치에 맞춰 조금씩 당긴다.
   * audio.currentTime 은 수십 ms 단위로 갱신되는 브라우저가 있어 그대로 쓰면 노트가 떨린다.
   * 판정은 화면 갱신과 떼어 10ms 마다 한다 — 탭을 옮겨도 판정과 게임 종료는 멈추지 않는다.
   */
  const tick = useCallback(() => {
    const audio = audioRef.current
    const judge = judgeRef.current
    const s = sheetRef.current
    if (!audio || !judge || !s || !playingRef.current) return
    const now = performance.now()
    const clock = (now - zeroRef.current) / 1000

    if (!audioStartedRef.current && clock >= 0) {
      audioStartedRef.current = true
      audio.currentTime = 0
      void audio.play().catch(() => {
        setLoadError("곡을 재생하지 못했습니다. 다시 시도해 주세요.")
        finish()
      })
    } else if (audioStartedRef.current && !audio.paused && audio.currentTime > 0) {
      const drift = audio.currentTime - clock
      zeroRef.current -= Math.abs(drift) > HARD_RESYNC_SEC ? drift * 1000 : drift * 1000 * SOFT_RESYNC
    }

    const t = songTime(now)
    judge.tick(t)

    if (now - lastUiRef.current >= UI_REFRESH_MS) {
      lastUiRef.current = now
      setLive(judge.live())
      const duration = s.duration ?? audio.duration
      setProgress(duration > 0 ? Math.min(1, Math.max(0, t / duration)) : 0)
    }
  }, [finish, songTime])

  const draw = useCallback(() => {
    const canvas = canvasRef.current
    const judge = judgeRef.current
    const s = sheetRef.current
    if (canvas && judge && s) {
      drawRhythmStage(canvas, {
        notes: s.notes,
        times: timesRef.current,
        keys: s.keys,
        keyLabels: RHYTHM_KEY_LABELS[s.keys],
        time: songTime(performance.now()),
        pixelsPerSecond: BASE_PPS * speedRef.current,
        judge,
        pressed: pressedRef.current,
        combo: judge.live().combo,
      })
    }
    rafRef.current = requestAnimationFrame(draw)
  }, [songTime])

  const start = async () => {
    const audio = audioRef.current
    if (!audio || !chart) return
    // Safari 는 클릭 순간에만 소리 재생을 허락하므로 지금 소리 없이 한 번 재생해 둔다.
    audio.muted = true
    const unlock = audio
      .play()
      .then(() => audio.pause())
      .catch(() => undefined)
      .finally(() => {
        audio.muted = false
        audio.currentTime = 0
      })
    setLoadError(null)
    setPhase("loading")
    let s: RhythmSheet
    try {
      s = await fetchRhythmSheet(challengeId, prefs.keys, prefs.difficulty)
    } catch (e) {
      await unlock
      setLoadError(toUserFacingMessage(e, UI_ERRORS.requestFailed))
      setPhase("setup")
      return
    }
    await unlock

    sheetRef.current = s
    timesRef.current = s.notes.map((n) => n[0])
    judgeRef.current = createRhythmJudge(s.notes, s.keys)
    pressesRef.current = []
    openPressRef.current = new Array<number>(s.keys).fill(-1)
    pressedRef.current = new Array<boolean>(s.keys).fill(false)
    pointerLaneRef.current.clear()
    audioStartedRef.current = false
    zeroRef.current = performance.now() + PREROLL_SEC * 1000
    playingRef.current = true
    audio.onended = () => finish()

    setSheet(s)
    setLive(null)
    setProgress(0)
    setResult(null)
    setServer(null)
    setSendError(null)
    setPhase("playing")
    tickRef.current = window.setInterval(tick, TICK_MS)
    rafRef.current = requestAnimationFrame(draw)
  }

  // 게임 중에는 뒤 페이지가 스크롤되지 않게 잠근다. 휴대폰에서 레인을 문지르다 화면이 밀리면 칠 수 없다.
  const locked = phase === "playing" || phase === "loading"
  useEffect(() => {
    if (!locked) return
    window.scrollTo(0, 0)
    const prev = document.body.style.overflow
    document.body.style.overflow = "hidden"
    return () => {
      document.body.style.overflow = prev
    }
  }, [locked])

  // 화면을 떠나면 곡과 루프를 멈춘다.
  useEffect(() => {
    const ref = audioRef
    return () => {
      playingRef.current = false
      clearInterval(tickRef.current)
      cancelAnimationFrame(rafRef.current)
      if (ref.current) {
        ref.current.onended = null
        ref.current.pause()
      }
    }
  }, [])

  if (loadError && !challenge) {
    return (
      <Shell challengeId={challengeId}>
        <StatusNote className="mt-8">{loadError}</StatusNote>
      </Shell>
    )
  }
  if (!challenge || !chart) {
    return (
      <Shell challengeId={challengeId}>
        <LoadingBlock label="채보를 불러오는 중입니다." className="mt-8 h-64" />
      </Shell>
    )
  }
  if (chart.status !== "ready" && chart.sheets.length === 0) {
    return (
      <Shell challengeId={challengeId}>
        <StatusNote className="mt-8">
          {chart.status === "processing"
            ? "채보를 만드는 중입니다. 잠시 뒤 새로고침해 주세요."
            : "이 곡은 아직 리듬 게임 채보가 없습니다."}
        </StatusNote>
      </Shell>
    )
  }

  const selected = chart.sheets.find(
    (s) => s.keys === prefs.keys && s.difficulty === prefs.difficulty
  )
  const inGame = phase === "playing"

  return (
    <Shell challengeId={challengeId}>
      <div className="mt-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-muted-foreground">
            리듬 게임
            {chart.bpm ? ` · BPM ${Math.round(chart.bpm)}` : ""}
            {sheet && phase !== "setup"
              ? ` · ${sheet.keys}키 ${RHYTHM_DIFFICULTY_LABEL[sheet.difficulty]} Lv.${sheet.level}`
              : ""}
          </p>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight">{challenge.title}</h1>
        </div>
      </div>

      <audio ref={audioRef} src={chart.audio_url ?? challenge.music_url} preload="auto" />

      {/* 게임 중에는 무대가 화면 전체를 쓴다 — 판정선과 키 자리가 화면 밖으로 밀리지 않게. */}
      {(inGame || phase === "loading") && (
        <div className="fixed inset-0 z-50 flex flex-col bg-zinc-950 text-white">
          <div className="mx-auto flex w-full max-w-3xl items-center gap-4 px-4 pt-4">
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs text-white/50">
                {challenge.title}
                {sheet ? ` · ${sheet.keys}키 ${RHYTHM_DIFFICULTY_LABEL[sheet.difficulty]} Lv.${sheet.level}` : ""}
              </p>
              <div className="mt-2 h-1 overflow-hidden rounded-full bg-white/10">
                <div className="h-full bg-sky-400" style={{ width: `${progress * 100}%` }} />
              </div>
            </div>
            <div className="text-right font-mono">
              <p className="text-2xl font-semibold leading-none tabular-nums">
                {(live?.score ?? 0).toLocaleString()}
              </p>
              <p className="mt-1 text-xs text-white/50">
                {live ? `${live.accuracy.toFixed(2)}%` : "0.00%"}
              </p>
            </div>
            <button
              type="button"
              onClick={finish}
              disabled={!inGame}
              className="inline-flex items-center gap-1.5 rounded-full border border-white/20 px-3 py-2 text-xs font-medium transition-colors hover:bg-white/10"
            >
              <Square className="h-3.5 w-3.5" aria-hidden="true" />
              그만하기
              <span className="hidden text-white/50 sm:inline">(Esc)</span>
            </button>
          </div>
          <canvas
            ref={canvasRef}
            onPointerDown={onPointerDown}
            onPointerUp={onPointerUp}
            onPointerCancel={onPointerUp}
            className="mt-3 block min-h-0 w-full flex-1 touch-none select-none"
            aria-label="노트가 떨어지는 무대. 판정선에 닿을 때 해당 키를 누르세요."
          />
          {phase === "loading" && (
            <div className="absolute inset-0 flex items-center justify-center bg-zinc-950/80">
              <Loader2 className="h-8 w-8 animate-spin text-sky-400" aria-hidden="true" />
            </div>
          )}
        </div>
      )}

      {phase === "setup" && (
        <div className="mt-5 space-y-5">
          <section className="rounded-3xl border border-border bg-card p-6">
            <h2 className="text-sm font-medium text-muted-foreground">키 수</h2>
            <div className="mt-2 flex gap-2" role="radiogroup" aria-label="키 수">
              {RHYTHM_KEYS.map((k) => (
                <button
                  key={k}
                  type="button"
                  role="radio"
                  aria-checked={prefs.keys === k}
                  onClick={() => updatePrefs({ keys: k })}
                  className={cn(
                    "rounded-full border px-5 py-2 text-sm font-semibold transition-colors",
                    prefs.keys === k
                      ? "border-sky-500 bg-sky-500 text-white"
                      : "border-border bg-background hover:bg-accent"
                  )}
                >
                  {k}키
                </button>
              ))}
            </div>

            <h2 className="mt-5 text-sm font-medium text-muted-foreground">난이도</h2>
            <div className="mt-2 grid grid-cols-3 gap-2" role="radiogroup" aria-label="난이도">
              {RHYTHM_DIFFICULTIES.map((d) => {
                const info = chart.sheets.find((s) => s.keys === prefs.keys && s.difficulty === d)
                return (
                  <button
                    key={d}
                    type="button"
                    role="radio"
                    aria-checked={prefs.difficulty === d}
                    disabled={!info}
                    onClick={() => updatePrefs({ difficulty: d })}
                    className={cn(
                      "rounded-2xl border px-4 py-3 text-left transition-colors disabled:opacity-40",
                      prefs.difficulty === d
                        ? "border-sky-500 bg-sky-500/10"
                        : "border-border bg-background hover:bg-accent"
                    )}
                  >
                    <span className="block text-sm font-semibold">{RHYTHM_DIFFICULTY_LABEL[d]}</span>
                    <span className="mt-1 block font-mono text-xs text-muted-foreground">
                      {info ? `Lv.${info.level} · 노트 ${info.note_count}` : "없음"}
                    </span>
                  </button>
                )
              })}
            </div>

            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <label className="block text-sm">
                <span className="font-medium">노트 속도</span>
                <span className="ml-2 font-mono text-muted-foreground">x{prefs.speed.toFixed(1)}</span>
                <input
                  type="range"
                  min={1}
                  max={5}
                  step={0.5}
                  value={prefs.speed}
                  onChange={(e) => updatePrefs({ speed: Number(e.target.value) })}
                  className="mt-2 block w-full"
                />
              </label>
              <label className="block text-sm">
                <span className="font-medium">싱크 보정</span>
                <span className="ml-2 font-mono text-muted-foreground">
                  {prefs.offsetMs > 0 ? "+" : ""}
                  {prefs.offsetMs}ms
                </span>
                <input
                  type="range"
                  min={-OFFSET_LIMIT_MS}
                  max={OFFSET_LIMIT_MS}
                  step={5}
                  value={prefs.offsetMs}
                  onChange={(e) => updatePrefs({ offsetMs: Number(e.target.value) })}
                  className="mt-2 block w-full"
                />
                <span className="mt-1 block text-xs text-muted-foreground">
                  소리에 맞춰 쳤는데 늘 늦게(GOOD·BAD) 나오면 + 쪽으로 옮기세요.
                </span>
              </label>
            </div>

            <p className="mt-5 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
              <Keyboard className="h-4 w-4" aria-hidden="true" />
              키:
              {RHYTHM_KEY_LABELS[prefs.keys].map((label, i) => (
                <kbd
                  key={i}
                  className="rounded-md border border-border bg-muted px-2 py-0.5 font-mono text-xs text-foreground"
                >
                  {label === "␣" ? "Space" : label}
                </kbd>
              ))}
              <span>· 휴대폰은 레인을 직접 터치</span>
            </p>

            {loadError && (
              <p role="alert" className="mt-4 text-sm text-destructive">
                {loadError}
              </p>
            )}

            <button
              type="button"
              onClick={() => void start()}
              disabled={!selected}
              className="mt-5 inline-flex items-center gap-2 rounded-full bg-sky-500 px-6 py-3 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
            >
              <Play className="h-4 w-4" aria-hidden="true" />
              시작하기
            </button>
          </section>

          <RhythmRankingList
            challengeId={challengeId}
            keys={prefs.keys}
            difficulty={prefs.difficulty}
            refreshKey={rankingKey}
          />
        </div>
      )}

      {phase === "finished" && result && sheet && (
        <div className="mt-5 space-y-5">
          <RhythmResultPanel
            keys={sheet.keys}
            difficulty={sheet.difficulty}
            result={result}
            server={server}
            sending={sending}
            error={sendError}
            onResend={() => void submit(sheet, pressesRef.current)}
            onRetry={() => void start()}
            onChangeSheet={() => setPhase("setup")}
          />
          <RhythmRankingList
            challengeId={challengeId}
            keys={sheet.keys}
            difficulty={sheet.difficulty}
            refreshKey={rankingKey}
          />
        </div>
      )}
    </Shell>
  )
}

type ShellProps = {
  challengeId: number
  children: React.ReactNode
}

function Shell({ challengeId, children }: ShellProps) {
  return (
    <main className="min-h-[calc(100vh-4rem)] min-w-0 overflow-x-hidden bg-background text-foreground">
      <div className="mx-auto max-w-3xl px-4 py-8 md:py-12">
        <Link
          href={`/music-challenge/${challengeId}`}
          className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          챌린지로 돌아가기
        </Link>
        {children}
      </div>
    </main>
  )
}
