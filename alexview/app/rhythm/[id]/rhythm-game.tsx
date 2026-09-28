"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import Link from "next/link"
import { ArrowLeft, Loader2, Play, Square } from "lucide-react"
import { LoadingBlock, StatusNote } from "@/components/common/status-note"
import { RhythmRankingList } from "@/components/music/rhythm-ranking"
import {
  beatGridOf,
  drawRhythmStage,
  resetRhythmStage,
  stageLayout,
  type RhythmBeat,
} from "@/components/music/rhythm-stage"
import { fetchChallenge, type Challenge } from "@/lib/music-challenge-api"
import {
  RHYTHM_DIFFICULTIES,
  RHYTHM_DIFFICULTY_LABEL,
  RHYTHM_KEYS,
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
import {
  DEFAULT_BINDINGS,
  keyLabel,
  keyNameFor,
  normalizeBindings,
  type KeyBindings,
} from "@/lib/rhythm-keys"
import { toUserFacingMessage, UI_ERRORS } from "@/lib/user-facing-error"
import { cn } from "@/lib/utils"
import { KeyBindingEditor } from "./key-binding-editor"
import { RhythmResultPanel } from "./rhythm-result-panel"

type Phase = "setup" | "loading" | "playing" | "finished"

// 곡을 틀기 전 노트가 위에서 내려올 시간(초). 이 동안 곡 위치는 음수다.
const PREROLL_SEC = 2
const TICK_MS = 10
// 창이 포커스를 잃고 이만큼 지나도 돌아오지 않으면 곡을 멈춘다(ms).
const BLUR_GRACE_MS = 600
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
  // 4키·7키 각각 레인별 키(KeyboardEvent.code)
  bindings: KeyBindings
}

const DEFAULT_PREFS: Prefs = {
  keys: 4,
  difficulty: "normal",
  speed: 2.5,
  offsetMs: 0,
  bindings: DEFAULT_BINDINGS,
}

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
      bindings: normalizeBindings(raw.bindings),
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
  // 무대 키 자리에 쓸 글자 — 판을 시작할 때 설정에서 정해 둔다
  const labelsRef = useRef<string[]>([])
  const timesRef = useRef<number[]>([])
  const beatRef = useRef<RhythmBeat | null>(null)
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
  // 일시정지한 순간의 게임 시계(초). 곡 시작 전 준비 시간에는 음수다.
  const pausedClockRef = useRef(0)
  // 멈춘 동안에도 "그만하기"는 되어야 해서 상태와 별도로 ref 로도 들고 있다.
  const pausedRef = useRef(false)
  const [paused, setPaused] = useState(false)

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
    if (!playingRef.current && !pausedRef.current) return
    playingRef.current = false
    pausedRef.current = false
    setPaused(false)
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

  /** 곡과 루프를 멈춘다. 멈춘 위치를 기억해 두었다가 그대로 이어서 시작한다. */
  const pauseGame = useCallback(() => {
    if (!playingRef.current) return
    playingRef.current = false
    stopLoops()
    pausedClockRef.current = (performance.now() - zeroRef.current) / 1000
    audioRef.current?.pause()
    // 멈춘 동안에는 keyup 이 오지 않으므로, 누르고 있던 레인은 지금 뗀 것으로 본다.
    const now = performance.now()
    const s = sheetRef.current
    if (s) for (let lane = 0; lane < s.keys; lane++) releaseLane(lane, now)
    pausedRef.current = true
    setPaused(true)
  }, [releaseLane])

  useEffect(() => {
    if (phase !== "playing" || !sheet) return
    const codes = prefs.bindings[sheet.keys]
    const keys = codes.map(keyNameFor)
    // 자판 배열과 상관없이 같은 자리를 쓰도록 code 로 찾고, code 가 비어 있는 입력기만 key 로 찾는다.
    const laneOf = (e: KeyboardEvent) =>
      e.code ? codes.indexOf(e.code) : keys.indexOf(e.key.toLowerCase()) // 대체 비교값이 빈 레인은 -1 로 남는다
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
    // 창을 벗어나면 어차피 칠 수 없고 keyup 도 오지 않으니 곡째로 멈춘다.
    // 다른 앱으로 전환하면 visibilitychange 가 뜨지 않으므로 blur 도 함께 본다.
    // 다만 브라우저 UI 를 잠깐 누르는 정도로도 blur 는 뜬다. 바로 돌아오면 멈추지 않게
    // 잠깐 기다렸다가, 그때도 포커스가 없으면 그제야 멈춘다.
    let blurTimer: number | undefined
    const onBlur = () => {
      const now = performance.now()
      for (let lane = 0; lane < sheet.keys; lane++) releaseLane(lane, now)
      window.clearTimeout(blurTimer)
      blurTimer = window.setTimeout(() => {
        if (!document.hasFocus()) pauseGame()
      }, BLUR_GRACE_MS)
    }
    const onFocus = () => window.clearTimeout(blurTimer)
    window.addEventListener("keydown", onDown)
    window.addEventListener("keyup", onUp)
    window.addEventListener("blur", onBlur)
    window.addEventListener("focus", onFocus)
    return () => {
      window.clearTimeout(blurTimer)
      window.removeEventListener("keydown", onDown)
      window.removeEventListener("keyup", onUp)
      window.removeEventListener("blur", onBlur)
      window.removeEventListener("focus", onFocus)
    }
  }, [phase, sheet, prefs.bindings, finish, pauseGame, pressLane, releaseLane])

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
        keyLabels: labelsRef.current,
        time: songTime(performance.now()),
        pixelsPerSecond: BASE_PPS * speedRef.current,
        judge,
        pressed: pressedRef.current,
        combo: judge.live().combo,
        beat: beatRef.current,
      })
    }
    rafRef.current = requestAnimationFrame(draw)
  }, [songTime])

  /** 멈춘 자리에서 그대로 이어서 시작한다. */
  const resumeGame = useCallback(() => {
    if (playingRef.current || !sheetRef.current) return
    const clock = pausedClockRef.current
    zeroRef.current = performance.now() - clock * 1000
    const audio = audioRef.current
    if (audio && audioStartedRef.current) {
      audio.currentTime = Math.max(0, clock)
      void audio.play().catch(() => undefined)
    }
    playingRef.current = true
    pausedRef.current = false
    setPaused(false)
    tickRef.current = window.setInterval(tick, TICK_MS)
    rafRef.current = requestAnimationFrame(draw)
  }, [draw, tick])

  // 탭을 옮기거나 창을 내리면 곡을 멈춘다. 배경에서 노래만 계속 나오면 안 된다.
  useEffect(() => {
    if (phase !== "playing") return
    const onHide = () => {
      if (document.hidden) pauseGame()
    }
    document.addEventListener("visibilitychange", onHide)
    return () => document.removeEventListener("visibilitychange", onHide)
  }, [phase, pauseGame])

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
    labelsRef.current = prefs.bindings[s.keys].map(keyLabel)
    timesRef.current = s.notes.map((n) => n[0])
    beatRef.current = beatGridOf(s.bpm, timesRef.current)
    judgeRef.current = createRhythmJudge(s.notes, s.keys)
    // 이전 판의 파편·흔들림이 새 판 첫 화면에 남지 않게 지운다.
    if (canvasRef.current) resetRhythmStage(canvasRef.current)
    pressesRef.current = []
    openPressRef.current = new Array<number>(s.keys).fill(-1)
    pressedRef.current = new Array<boolean>(s.keys).fill(false)
    pointerLaneRef.current.clear()
    audioStartedRef.current = false
    zeroRef.current = performance.now() + PREROLL_SEC * 1000
    playingRef.current = true
    pausedRef.current = false
    setPaused(false)
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
      <Shell>
        <StatusNote className="mt-8">{loadError}</StatusNote>
      </Shell>
    )
  }
  if (!challenge || !chart) {
    return (
      <Shell>
        <LoadingBlock label="채보를 불러오는 중입니다." className="mt-8 h-64" />
      </Shell>
    )
  }
  if (chart.status !== "ready" && chart.sheets.length === 0) {
    return (
      <Shell>
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
    <Shell>
      <div className="mt-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="font-orbitron text-xs font-bold tracking-[0.25em] text-neon-cyan">
            리듬 게임
            {chart.bpm ? ` · BPM ${Math.round(chart.bpm)}` : ""}
            {sheet && phase !== "setup"
              ? ` · ${sheet.keys}키 ${RHYTHM_DIFFICULTY_LABEL[sheet.difficulty]} Lv.${sheet.level}`
              : ""}
          </p>
          <h1 className="mt-2 font-display text-3xl text-white sm:text-4xl">{challenge.title}</h1>
        </div>
      </div>

      <audio ref={audioRef} src={chart.audio_url ?? challenge.music_url} preload="auto" />

      {/* 게임 중에는 무대가 화면 전체를 쓴다 — 판정선과 키 자리가 화면 밖으로 밀리지 않게. */}
      {(inGame || phase === "loading") && (
        <div className="fixed inset-0 z-50 flex flex-col bg-night-950 text-white">
          <div className="mx-auto flex w-full max-w-3xl items-center gap-4 px-4 pt-4">
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs text-muted-foreground">
                {challenge.title}
                {sheet ? ` · ${sheet.keys}키 ${RHYTHM_DIFFICULTY_LABEL[sheet.difficulty]} Lv.${sheet.level}` : ""}
              </p>
              <div className="mt-2 h-1 overflow-hidden rounded-full bg-night-700">
                <div className="h-full bg-neon-pink shadow-[0_0_10px_#ff2e97]" style={{ width: `${progress * 100}%` }} />
              </div>
            </div>
            <div className="text-right font-orbitron">
              <p className="neon-text-cyan text-2xl font-bold leading-none tabular-nums text-neon-cyan">
                {(live?.score ?? 0).toLocaleString()}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                {live ? `${live.accuracy.toFixed(2)}%` : "0.00%"}
              </p>
            </div>
            <button
              type="button"
              onClick={finish}
              disabled={!inGame}
              className="inline-flex items-center gap-1.5 rounded-full border border-neon-cyan/60 px-3 py-2 text-xs font-medium text-neon-cyan transition-colors hover:bg-neon-cyan/10"
            >
              <Square className="h-3.5 w-3.5" aria-hidden="true" />
              그만하기
              <span className="hidden text-neon-cyan/70 sm:inline">(Esc)</span>
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
            <div className="absolute inset-0 flex items-center justify-center bg-night-950/80">
              <Loader2 className="h-8 w-8 animate-spin text-neon-pink" aria-hidden="true" />
            </div>
          )}
          {paused && (
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-5 bg-night-950/85">
              <p className="neon-text font-orbitron text-3xl font-bold">일시정지</p>
              <p className="text-sm text-muted-foreground">
                다른 탭으로 가서 곡을 멈췄습니다. 멈춘 자리에서 이어집니다.
              </p>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={resumeGame}
                  className="rounded-full bg-neon-pink px-6 py-2.5 text-sm font-semibold text-night-950 transition-opacity hover:opacity-90"
                >
                  이어서 하기
                </button>
                <button
                  type="button"
                  onClick={finish}
                  className="rounded-full border border-neon-cyan/60 px-6 py-2.5 text-sm font-medium text-neon-cyan transition-colors hover:bg-neon-cyan/10"
                >
                  그만하기
                </button>
              </div>
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
                      ? "glow-button border-neon-pink bg-primary text-primary-foreground"
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
                        ? "border-neon-pink bg-neon-pink/10 shadow-[0_0_18px_-6px_#ff2e97]"
                        : "border-border bg-background hover:bg-accent"
                    )}
                  >
                    <span className="block text-sm font-semibold">{RHYTHM_DIFFICULTY_LABEL[d]}</span>
                    <span className="mt-1 block font-orbitron text-xs text-muted-foreground">
                      {info ? `Lv.${info.level} · 노트 ${info.note_count}` : "없음"}
                    </span>
                  </button>
                )
              })}
            </div>

            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <label className="block text-sm">
                <span className="font-medium">노트 속도</span>
                <span className="ml-2 font-orbitron text-neon-cyan">x{prefs.speed.toFixed(1)}</span>
                <input
                  type="range"
                  min={1}
                  max={5}
                  step={0.5}
                  value={prefs.speed}
                  onChange={(e) => updatePrefs({ speed: Number(e.target.value) })}
                  className="mt-2 block w-full accent-neon-pink"
                />
              </label>
              <label className="block text-sm">
                <span className="font-medium">싱크 보정</span>
                <span className="ml-2 font-orbitron text-neon-cyan">
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
                  className="mt-2 block w-full accent-neon-pink"
                />
                <span className="mt-1 block text-xs text-muted-foreground">
                  소리에 맞춰 쳤는데 늘 늦게(GOOD·BAD) 나오면 + 쪽으로 옮기세요.
                </span>
              </label>
            </div>

            <KeyBindingEditor
              keys={prefs.keys}
              bindings={prefs.bindings[prefs.keys]}
              onChange={(next) => updatePrefs({ bindings: { ...prefs.bindings, [prefs.keys]: next } })}
            />

            {loadError && (
              <p role="alert" className="mt-4 text-sm text-destructive">
                {loadError}
              </p>
            )}

            <button
              type="button"
              onClick={() => void start()}
              disabled={!selected}
              className="glow-button mt-5 inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3 text-sm font-bold text-primary-foreground disabled:opacity-50"
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
  children: React.ReactNode
}

function Shell({ children }: ShellProps) {
  return (
    <main className="min-h-[calc(100vh-4rem)] min-w-0 overflow-x-hidden bg-background text-foreground">
      <div className="mx-auto max-w-3xl px-4 py-8 md:py-12">
        <Link
          href="/rhythm"
          className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          곡 목록으로
        </Link>
        {children}
      </div>
    </main>
  )
}
