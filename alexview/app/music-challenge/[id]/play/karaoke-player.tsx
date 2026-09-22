"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import Link from "next/link"
import { ArrowLeft, Headphones, Mic, Play, Square } from "lucide-react"
import { LoadingBlock, StatusNote } from "@/components/common/status-note"
import { drawHighway, highwayRange, type TrailPoint } from "@/components/music/note-highway"
import { usePitchInput } from "@/hooks/use-pitch-input"
import {
  JUDGEMENT_LABEL,
  createKaraokeScorer,
  foldToTarget,
  type FinalScore,
  type KaraokeScorer,
  type LiveScore,
} from "@/lib/karaoke-scoring"
import {
  INSTRUMENT_LABEL,
  fetchChallenge,
  fetchChart,
  type Challenge,
  type Chart,
  type ChartNote,
} from "@/lib/music-challenge-api"
import { toUserFacingMessage, UI_ERRORS } from "@/lib/user-facing-error"
import { cn } from "@/lib/utils"
import { LyricsDisplay } from "./lyrics-display"
import { ResultPanel } from "./result-panel"

type Phase = "setup" | "countdown" | "playing" | "finished"

const COUNTDOWN_FROM = 3
// 점수·가사 같은 글자는 초당 10번이면 충분하다. 매 프레임 React 를 돌리면 끊긴다.
const UI_REFRESH_MS = 100
// 판정 간격 — 서버 재채점(20ms 프레임)과 맞춘다
const SAMPLE_MS = 20
const TRAIL_SEC = 2.5
const OFFSET_KEY = "iuem-karaoke-offset-ms"
const OFFSET_LIMIT_MS = 300

type KaraokePlayerProps = {
  challengeId: number
}

function readSavedOffset(): number {
  try {
    const v = Number(localStorage.getItem(OFFSET_KEY))
    return Number.isFinite(v) ? Math.max(-OFFSET_LIMIT_MS, Math.min(OFFSET_LIMIT_MS, v)) : 0
  } catch {
    return 0
  }
}

/** 내 목소리 선을 어느 음표 옆에 그릴지 — 지금 음표, 없으면 시간상 가장 가까운 음표 */
function nearestNote(notes: ChartNote[], t: number): ChartNote | null {
  let best: ChartNote | null = null
  let bestGap = Infinity
  for (const n of notes) {
    const gap = t < n.start ? n.start - t : t > n.end ? t - n.end : 0
    if (gap < bestGap) {
      best = n
      bestGap = gap
      if (gap === 0) break
    }
    if (n.start > t + 2) break
  }
  return best
}

export function KaraokePlayer({ challengeId }: KaraokePlayerProps) {
  const [challenge, setChallenge] = useState<Challenge | null>(null)
  const [chart, setChart] = useState<Chart | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [phase, setPhase] = useState<Phase>("setup")
  const [countdown, setCountdown] = useState(COUNTDOWN_FROM)
  const [live, setLive] = useState<LiveScore | null>(null)
  const [final, setFinal] = useState<FinalScore | null>(null)
  const [recording, setRecording] = useState<Blob | null>(null)
  const [startOffset, setStartOffset] = useState(0)
  const [uiTime, setUiTime] = useState(0)
  const [offsetMs, setOffsetMs] = useState(0)

  const { state: micState, open, startRecording, read, stop, latencyRef } = usePitchInput()
  const audioRef = useRef<HTMLAudioElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const scorerRef = useRef<KaraokeScorer | null>(null)
  const trailRef = useRef<TrailPoint[]>([])
  const rafRef = useRef(0)
  const sampleTimerRef = useRef<number | undefined>(undefined)
  // 판정이 마지막으로 본 곡 위치 — 그리기가 이 값을 읽는다
  const timeRef = useRef(0)
  const lastUiRef = useRef(0)
  const offsetRef = useRef(0)
  const finishingRef = useRef(false)

  useEffect(() => {
    const saved = readSavedOffset()
    setOffsetMs(saved)
    offsetRef.current = saved
  }, [])

  useEffect(() => {
    let alive = true
    Promise.all([fetchChallenge(challengeId), fetchChart(challengeId)])
      .then(([c, ch]) => {
        if (!alive) return
        setChallenge(c)
        setChart(ch)
      })
      .catch((e) => {
        if (alive) setLoadError(toUserFacingMessage(e, UI_ERRORS.challengeLoadFailed))
      })
    return () => {
      alive = false
    }
  }, [challengeId])

  const notes = chart?.notes ?? []
  const range = highwayRange(notes)

  const changeOffset = (ms: number) => {
    const v = Math.max(-OFFSET_LIMIT_MS, Math.min(OFFSET_LIMIT_MS, ms))
    setOffsetMs(v)
    offsetRef.current = v
    try {
      localStorage.setItem(OFFSET_KEY, String(v))
    } catch {
      // 저장 못 해도 이번 판에는 적용된다.
    }
  }

  /** 판정 기준 곡 위치 = 들리는 위치 − 기기 지연 − 사용자 보정 */
  const latencySec = useCallback(
    () => latencyRef.current + offsetRef.current / 1000,
    [latencyRef]
  )

  const stopLoops = () => {
    clearInterval(sampleTimerRef.current)
    cancelAnimationFrame(rafRef.current)
  }

  const finish = useCallback(async () => {
    if (finishingRef.current) return
    finishingRef.current = true
    stopLoops()
    audioRef.current?.pause()
    const blob = await stop()
    setFinal(scorerRef.current?.finish() ?? null)
    setRecording(blob)
    setPhase("finished")
  }, [stop])

  /**
   * 판정 — 화면 갱신과 떼어 20ms 마다 한다.
   *
   * requestAnimationFrame 에 묶어 두면 탭을 옮기거나 폰 화면이 꺼지는 순간 멈춘다.
   * 곡은 계속 나오는데 판정이 끊기고, "곡이 끝났다"는 확인도 그 안에 있어서 게임이
   * 영영 끝나지 않았다. 20ms 는 서버 재채점의 프레임 간격과 같아 두 점수도 가까워진다.
   */
  const sample = useCallback(() => {
    const audio = audioRef.current
    const scorer = scorerRef.current
    if (!audio || !scorer || !chart) return

    const t = audio.currentTime - latencySec()
    timeRef.current = t
    const reading = read()
    scorer.push(t, reading?.midi ?? null)

    const target = reading ? nearestNote(chart.notes, t) : null
    const trail = trailRef.current
    trail.push({ t, midi: reading && target ? foldToTarget(reading.midi, target.midi) : null })
    while (trail.length && trail[0].t < t - TRAIL_SEC) trail.shift()

    const now = performance.now()
    if (now - lastUiRef.current >= UI_REFRESH_MS) {
      lastUiRef.current = now
      setLive(scorer.live())
      setUiTime(t)
    }
  }, [chart, read, latencySec])

  /** 그리기 — 화면이 실제로 그려질 때만. 멈춰도 판정에는 영향이 없다. */
  const draw = useCallback(() => {
    const canvas = canvasRef.current
    const scorer = scorerRef.current
    if (canvas && scorer && chart) {
      drawHighway(canvas, {
        notes: chart.notes,
        time: timeRef.current,
        lo: range.lo,
        hi: range.hi,
        trail: trailRef.current,
        progress: (i) => scorer.progress(i),
      })
    }
    rafRef.current = requestAnimationFrame(draw)
  }, [chart, range.lo, range.hi])

  const begin = useCallback(async () => {
    const audio = audioRef.current
    if (!audio) return
    audio.currentTime = 0
    try {
      await audio.play()
    } catch {
      setLoadError("곡을 재생하지 못했습니다. 다시 시도해 주세요.")
      await stop()
      setPhase("setup")
      return
    }
    startRecording()
    // 녹음이 곡의 몇 초 지점에서 시작됐는지. 서버가 이 값으로 녹음을 음표에 맞춘다.
    setStartOffset(audio.currentTime - latencySec())
    setPhase("playing")
    // 곡이 끝나면 오디오가 직접 알려 준다. 판정 루프가 느려지거나 멈춰도 게임은 끝난다.
    audio.onended = () => void finish()
    sampleTimerRef.current = window.setInterval(sample, SAMPLE_MS)
    rafRef.current = requestAnimationFrame(draw)
  }, [draw, finish, sample, stop, startRecording, latencySec])

  const start = async () => {
    const audio = audioRef.current
    if (!chart || !audio) return
    // 곡은 카운트다운 3초 뒤에 튼다. Safari 는 클릭 순간에만 소리 재생을 허락하므로
    // 지금 소리 없이 한 번 재생해 두어야 나중에 play() 가 막히지 않는다.
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
    const ok = await open()
    await unlock
    if (!ok) return
    scorerRef.current = createKaraokeScorer(chart.notes)
    trailRef.current = []
    finishingRef.current = false
    setLive(null)
    setFinal(null)
    setRecording(null)
    setPhase("countdown")
    setCountdown(COUNTDOWN_FROM)
  }

  // 카운트다운이 끝나면 곡을 튼다.
  useEffect(() => {
    if (phase !== "countdown") return
    if (countdown === 0) {
      void begin()
      return
    }
    const id = setTimeout(() => setCountdown((c) => c - 1), 1000)
    return () => clearTimeout(id)
  }, [phase, countdown, begin])

  // 화면을 떠나면 마이크와 곡을 멈춘다. <audio> 는 악보를 불러온 뒤에 생기므로
  // 마운트 시점이 아니라 떠나는 시점의 ref 를 읽어야 한다.
  useEffect(() => {
    const ref = audioRef
    return () => {
      clearInterval(sampleTimerRef.current)
      cancelAnimationFrame(rafRef.current)
      if (ref.current) ref.current.onended = null
      ref.current?.pause()
      void stop()
    }
  }, [stop])

  const retry = () => {
    setPhase("setup")
    setFinal(null)
    setRecording(null)
  }

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
        <LoadingBlock label="악보를 불러오는 중입니다." className="mt-8 h-64" />
      </Shell>
    )
  }
  if (chart.status !== "ready" || chart.notes.length === 0) {
    return (
      <Shell challengeId={challengeId}>
        <StatusNote className="mt-8">
          이 곡은 아직 노래방 악보가 준비되지 않았습니다. 챌린지 화면에서 녹음해 제출할 수
          있습니다.
        </StatusNote>
      </Shell>
    )
  }

  const isInstrument = chart.melody_source === "instrument"
  const partLabel = isInstrument
    ? `${chart.instrument ? INSTRUMENT_LABEL[chart.instrument] : "악기"} 연주`
    : "노래"
  const hasLyrics = !isInstrument && chart.lyric_lines.some((l) => l.start !== null)

  return (
    <Shell challengeId={challengeId}>
      <div className="mt-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-muted-foreground">
            {isInstrument ? "연주 모드" : "노래방 모드"} · {partLabel}
          </p>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight">{challenge.title}</h1>
        </div>
        {phase === "playing" && (
          <button
            type="button"
            onClick={() => void finish()}
            className="inline-flex items-center gap-2 rounded-full border border-border bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent"
          >
            <Square className="h-4 w-4" aria-hidden="true" />
            그만하고 채점
          </button>
        )}
      </div>

      {/* 반주 — 없으면 원곡을 튼다 */}
      <audio ref={audioRef} src={chart.backing_url ?? challenge.music_url} preload="auto" />

      <div className="relative mt-5 overflow-hidden rounded-3xl bg-zinc-950 text-white">
        <div className="flex items-center justify-between px-5 pt-4 font-mono text-sm">
          <span className="text-white/60">SCORE</span>
          <span className="text-3xl font-semibold tabular-nums">{live?.score ?? 0}</span>
        </div>
        <div className="flex items-center justify-between px-5 pb-2 font-mono text-xs text-white/50">
          <span>COMBO {live?.combo ?? 0}</span>
          <span
            key={live?.last?.index ?? -1}
            className={cn(
              "text-base font-semibold transition-opacity",
              live?.last?.judgement === "perfect" && "text-sky-400",
              live?.last?.judgement === "great" && "text-green-400",
              live?.last?.judgement === "good" && "text-yellow-400",
              live?.last?.judgement === "miss" && "text-red-400"
            )}
          >
            {phase === "playing" && live?.last ? JUDGEMENT_LABEL[live.last.judgement] : " "}
          </span>
        </div>

        <canvas ref={canvasRef} className="block h-64 w-full sm:h-80" aria-label="음표 흐름" />

        {hasLyrics && (
          <div className="border-t border-white/10 py-4">
            <LyricsDisplay lines={chart.lyric_lines} time={uiTime} />
          </div>
        )}

        {phase === "countdown" && (
          <div className="absolute inset-0 flex items-center justify-center bg-zinc-950/70">
            <span className="font-mono text-7xl font-semibold" role="status">
              {countdown}
            </span>
          </div>
        )}

        {phase === "setup" && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 bg-zinc-950/85 px-6 text-center">
            <Headphones className="h-8 w-8 text-sky-400" aria-hidden="true" />
            <p className="max-w-md text-sm leading-6 text-white/80">
              <strong className="text-white">이어폰을 끼고 시작하세요.</strong> 스피커로 틀면
              마이크가 {chart.backing_url ? "반주" : "원곡 목소리"}를 같이 들어서 판정이
              틀어집니다.
              {!chart.backing_url && " 이 곡은 반주 스템이 없어 원곡이 재생됩니다."}
            </p>
            {micState === "denied" && (
              <p role="alert" className="text-sm text-red-400">
                마이크 권한이 필요합니다. 브라우저 주소창의 권한 설정에서 마이크를 허용해 주세요.
              </p>
            )}
            {loadError && (
              <p role="alert" className="text-sm text-red-400">
                {loadError}
              </p>
            )}
            <button
              type="button"
              onClick={() => void start()}
              disabled={micState === "requesting"}
              className="inline-flex items-center gap-2 rounded-full bg-sky-500 px-6 py-3 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
            >
              {micState === "requesting" ? (
                <Mic className="h-4 w-4 animate-pulse" aria-hidden="true" />
              ) : (
                <Play className="h-4 w-4" aria-hidden="true" />
              )}
              {micState === "requesting" ? "마이크 연결 중…" : "시작하기"}
            </button>
          </div>
        )}
      </div>

      {phase !== "finished" && (
        <div className="mt-4 flex flex-wrap items-center gap-3 text-sm">
          <label htmlFor="sync-offset" className="font-medium">
            싱크 보정
          </label>
          <input
            id="sync-offset"
            type="range"
            min={-OFFSET_LIMIT_MS}
            max={OFFSET_LIMIT_MS}
            step={10}
            value={offsetMs}
            onChange={(e) => changeOffset(Number(e.target.value))}
            className="w-48"
          />
          <span className="w-16 font-mono tabular-nums">
            {offsetMs > 0 ? "+" : ""}
            {offsetMs}ms
          </span>
          <span className="text-xs text-muted-foreground">
            제때 불렀는데 내 선이 음표보다 늦게 따라오면 +, 앞서가면 − 쪽으로 옮기세요.
          </span>
        </div>
      )}

      {phase === "finished" && final && (
        <ResultPanel
          challengeId={challengeId}
          final={final}
          recording={recording}
          startOffset={startOffset}
          onRetry={retry}
        />
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
      <div className="mx-auto max-w-5xl px-4 py-8 md:py-12">
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
