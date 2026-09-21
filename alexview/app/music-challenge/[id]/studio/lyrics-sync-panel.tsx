"use client"

import { useCallback, useEffect, useState } from "react"
import { Loader2, RotateCcw, Save, Undo2 } from "lucide-react"
import { useAsyncAction } from "@/hooks/use-async-action"
import {
  activeLyricIndex,
  formatSeconds,
  mergeLyricTimings,
  parseLyricsText,
} from "@/lib/lyrics"
import { saveLyrics, type Chart, type LyricLine } from "@/lib/music-challenge-api"
import { UI_ERRORS } from "@/lib/user-facing-error"
import { cn } from "@/lib/utils"

const NUDGE_SEC = 0.1

type LyricsSyncPanelProps = {
  challengeId: number
  savedLines: LyricLine[]
  audioRef: React.RefObject<HTMLAudioElement | null>
  currentTime: number
  onChartChange: (chart: Chart) => void
}

function firstUnstamped(lines: LyricLine[]): number {
  const i = lines.findIndex((l) => l.start === null)
  return i === -1 ? lines.length : i
}

/** 입력 중인 칸에서 누른 스페이스·백스페이스는 탭으로 가로채지 않는다. */
function isTypingTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false
  return (
    target.isContentEditable ||
    ["INPUT", "TEXTAREA", "SELECT"].includes(target.tagName)
  )
}

export function LyricsSyncPanel({
  challengeId,
  savedLines,
  audioRef,
  currentTime,
  onChartChange,
}: LyricsSyncPanelProps) {
  // 악보 상태를 주기적으로 다시 불러와도 편집 중인 내용이 덮이지 않도록 처음 한 번만 받는다.
  const [lines, setLines] = useState<LyricLine[]>(savedLines)
  const [cursor, setCursor] = useState(() => firstUnstamped(savedLines))
  const [draft, setDraft] = useState(() => savedLines.map((l) => l.text).join("\n"))
  const [dirty, setDirty] = useState(false)
  const [hint, setHint] = useState<string | null>(null)
  const { loading, error, success, run } = useAsyncAction()

  const stamp = useCallback(() => {
    const audio = audioRef.current
    if (!audio || cursor >= lines.length) return
    const t = Math.round(audio.currentTime * 100) / 100
    const prev = lines.slice(0, cursor).reverse().find((l) => l.start !== null)
    if (prev?.start != null && t < prev.start) {
      setHint("앞 줄보다 이른 시간입니다. 재생 위치를 확인하거나 앞 줄을 다시 찍어 주세요.")
      return
    }
    setHint(null)
    setLines((ls) => ls.map((l, i) => (i === cursor ? { ...l, start: t } : l)))
    setCursor((c) => c + 1)
    setDirty(true)
  }, [audioRef, cursor, lines])

  const undo = useCallback(() => {
    if (cursor === 0) return
    const target = cursor - 1
    setLines((ls) => ls.map((l, i) => (i === target ? { ...l, start: null } : l)))
    setCursor(target)
    setDirty(true)
    setHint(null)
  }, [cursor])

  useEffect(() => {
    const isSpace = (e: KeyboardEvent) => e.code === "Space" || e.key === " "
    const onKeyDown = (e: KeyboardEvent) => {
      if (isTypingTarget(e.target) || e.repeat) return
      if (isSpace(e)) {
        e.preventDefault()
        stamp()
      } else if (e.code === "Backspace" || e.key === "Backspace") {
        e.preventDefault()
        undo()
      }
    }
    // 브라우저는 포커스된 버튼을 스페이스를 "뗄 때" 누른다. 방금 클릭한 "지금 탭"
    // 버튼에 포커스가 남아 있으면 한 번 눌렀는데 두 줄이 찍히므로 여기서 막는다.
    const onKeyUp = (e: KeyboardEvent) => {
      if (!isTypingTarget(e.target) && isSpace(e)) e.preventDefault()
    }
    window.addEventListener("keydown", onKeyDown)
    window.addEventListener("keyup", onKeyUp)
    return () => {
      window.removeEventListener("keydown", onKeyDown)
      window.removeEventListener("keyup", onKeyUp)
    }
  }, [stamp, undo])

  const applyDraft = () => {
    const merged = mergeLyricTimings(parseLyricsText(draft), lines)
    setLines(merged)
    setCursor(firstUnstamped(merged))
    setDirty(true)
    setHint(null)
  }

  const resetTimings = () => {
    setLines((ls) => ls.map((l) => ({ ...l, start: null })))
    setCursor(0)
    setDirty(true)
    const audio = audioRef.current
    if (audio) audio.currentTime = 0
  }

  const nudgeAll = (delta: number) => {
    setLines((ls) =>
      ls.map((l) =>
        l.start === null ? l : { ...l, start: Math.max(0, Math.round((l.start + delta) * 100) / 100) }
      )
    )
    setDirty(true)
  }

  const selectLine = (i: number) => {
    setCursor(i)
    const audio = audioRef.current
    const start = lines[i]?.start
    // 다시 찍기 편하게 그 줄 조금 앞에서부터 들려준다.
    if (audio && start !== null && start !== undefined) {
      audio.currentTime = Math.max(0, start - 2)
    }
  }

  const handleSave = async () => {
    await run(() => saveLyrics(challengeId, lines), {
      fallbackError: UI_ERRORS.requestFailed,
      successMessage: "가사를 저장했습니다.",
      onSuccess: (chart) => {
        onChartChange(chart)
        setDirty(false)
      },
    })
  }

  const stampedCount = lines.filter((l) => l.start !== null).length
  const playingIndex = activeLyricIndex(lines, currentTime)

  return (
    <section className="rounded-3xl border border-border bg-card p-6">
      <div>
        <p className="text-sm font-medium text-muted-foreground">2단계</p>
        <h2 className="mt-1 text-xl font-semibold">가사 · 줄별 타이밍</h2>
      </div>

      <label className="mt-5 grid gap-2 text-sm">
        <span className="font-medium">가사 붙여넣기</span>
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          rows={8}
          placeholder={"[Verse 1]\n첫 번째 줄\n두 번째 줄\n\n[Chorus]\n…"}
          className="rounded-xl border border-border bg-background px-3 py-2 font-mono text-sm leading-6"
        />
        <span className="text-xs text-muted-foreground">
          Suno 가사를 그대로 붙여넣어도 됩니다. [Verse], [Chorus] 같은 구간 표시 줄과 빈 줄은
          자동으로 빠집니다. 문장이 그대로인 줄은 찍어 둔 시간이 유지됩니다.
        </span>
      </label>
      <button
        type="button"
        onClick={applyDraft}
        className="mt-3 rounded-full border border-border bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent"
      >
        가사 적용
      </button>

      {lines.length > 0 && (
        <>
          <div className="mt-6 rounded-2xl border border-border bg-muted/40 p-4 text-sm leading-6">
            <p className="font-medium">타이밍 찍는 법</p>
            <p className="mt-1 text-muted-foreground">
              아래 플레이어로 원곡을 틀고, 각 줄을 <strong className="text-foreground">부르기 시작하는
              순간</strong>에 <kbd className="rounded border border-border bg-background px-1.5 font-mono text-xs">Space</kbd>를
              누르세요. 잘못 찍었으면{" "}
              <kbd className="rounded border border-border bg-background px-1.5 font-mono text-xs">Backspace</kbd>로
              한 줄 되돌립니다. 줄을 누르면 그 줄부터 다시 찍을 수 있습니다.
            </p>
          </div>

          <div className="mt-4 flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={stamp}
              disabled={cursor >= lines.length}
              className="rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-80 disabled:opacity-40"
            >
              지금 탭 (Space)
            </button>
            <button
              type="button"
              onClick={undo}
              disabled={cursor === 0}
              className="inline-flex items-center gap-1.5 rounded-full border border-border bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent disabled:opacity-40"
            >
              <Undo2 className="h-4 w-4" aria-hidden="true" />
              되돌리기
            </button>
            <button
              type="button"
              onClick={() => nudgeAll(-NUDGE_SEC)}
              className="rounded-full border border-border bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent"
            >
              전체 0.1초 앞당기기
            </button>
            <button
              type="button"
              onClick={() => nudgeAll(NUDGE_SEC)}
              className="rounded-full border border-border bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent"
            >
              전체 0.1초 늦추기
            </button>
            <button
              type="button"
              onClick={resetTimings}
              className="inline-flex items-center gap-1.5 rounded-full border border-border bg-background px-4 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
            >
              <RotateCcw className="h-4 w-4" aria-hidden="true" />
              처음부터
            </button>
            <span className="ml-auto font-mono text-sm text-muted-foreground" role="status">
              {stampedCount}/{lines.length}줄
            </span>
          </div>

          {hint && (
            <p role="alert" className="mt-3 text-sm text-destructive">
              {hint}
            </p>
          )}

          <ol className="mt-4 max-h-96 space-y-1 overflow-y-auto rounded-2xl border border-border p-2">
            {lines.map((line, i) => (
              <li key={i}>
                <button
                  type="button"
                  onClick={() => selectLine(i)}
                  className={cn(
                    "flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm transition-colors hover:bg-muted/60",
                    i === cursor && "ring-2 ring-foreground/60",
                    i === playingIndex && "bg-muted"
                  )}
                >
                  <span className="w-14 shrink-0 font-mono text-xs text-muted-foreground">
                    {formatSeconds(line.start)}
                  </span>
                  <span className={cn(line.start === null && "text-muted-foreground")}>
                    {line.text}
                  </span>
                  {i === cursor && (
                    <span className="ml-auto shrink-0 text-xs font-medium">다음 탭</span>
                  )}
                </button>
              </li>
            ))}
          </ol>
        </>
      )}

      <div className="mt-5 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={handleSave}
          disabled={loading || !dirty}
          className="inline-flex items-center gap-2 rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-80 disabled:opacity-40"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          ) : (
            <Save className="h-4 w-4" aria-hidden="true" />
          )}
          가사 저장
        </button>
        {dirty && <span className="text-xs text-muted-foreground">저장하지 않은 변경이 있습니다.</span>}
        {success && !dirty && (
          <span role="status" className="text-xs text-muted-foreground">
            {success}
          </span>
        )}
        {error && (
          <span role="alert" className="text-sm text-destructive">
            {error}
          </span>
        )}
      </div>
    </section>
  )
}
