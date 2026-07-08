"use client"

import { useCallback, useEffect, useState } from "react"
import { AudioLines, ChevronLeft, ChevronRight, Crown, Music4, Trophy } from "lucide-react"
import {
  WEEKLY_KING_SLIDES,
  entryTotalScore,
  type WeeklyKingEntry,
} from "@/lib/weekly-king-mock"
import { cn } from "@/lib/utils"

const SLIDE_MS = 10_000

function RankRow({ entry, highlight }: { entry: WeeklyKingEntry; highlight: boolean }) {
  const total = entryTotalScore(entry)

  return (
    <li
      className={cn(
        "flex items-center gap-2 rounded-lg border px-2.5 py-1.5 text-xs sm:gap-3 sm:px-3 sm:py-2 sm:text-sm",
        highlight
          ? "border-amber-500/40 bg-amber-500/10"
          : "border-zinc-800 bg-zinc-900/50"
      )}
    >
      <span
        className={cn(
          "flex h-6 w-6 shrink-0 items-center justify-center rounded-md text-[11px] font-bold tabular-nums sm:h-7 sm:w-7",
          entry.rank === 1
            ? "bg-amber-400 text-zinc-950"
            : entry.rank <= 3
              ? "bg-white text-zinc-950"
              : "bg-zinc-800 text-zinc-300"
        )}
      >
        {entry.rank}
      </span>
      <span className="min-w-0 flex-1 truncate font-medium text-zinc-100">
        {entry.username}
      </span>
      <span className="shrink-0 tabular-nums text-zinc-400">
        <span className="hidden sm:inline">음정 {entry.pitchScore}</span>
        <span className="hidden sm:inline text-zinc-600"> · </span>
        <span className="hidden sm:inline">박자 {entry.rhythmScore}</span>
        <span className="sm:hidden">{total}점</span>
      </span>
      <span className="hidden shrink-0 font-semibold tabular-nums text-white sm:inline">
        {total}점
      </span>
      {entry.rank === 1 ? (
        <Crown className="h-3.5 w-3.5 shrink-0 text-amber-400 sm:h-4 sm:w-4" aria-hidden />
      ) : null}
    </li>
  )
}

export function WeeklyKingBanner() {
  const [index, setIndex] = useState(0)
  const slide = WEEKLY_KING_SLIDES[index]
  const isVocal = slide.id === "vocal"

  const goTo = useCallback((next: number) => {
    setIndex((next + WEEKLY_KING_SLIDES.length) % WEEKLY_KING_SLIDES.length)
  }, [])

  useEffect(() => {
    const timer = window.setInterval(() => {
      setIndex((i) => (i + 1) % WEEKLY_KING_SLIDES.length)
    }, SLIDE_MS)
    return () => window.clearInterval(timer)
  }, [])

  return (
    <div
      className="h-full w-full rounded-3xl border border-zinc-200 bg-zinc-950 px-5 py-5 text-white shadow-[0_20px_60px_rgba(0,0,0,0.12)] sm:px-6 sm:py-6"
      aria-roledescription="carousel"
      aria-label="이번 주 스타"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex min-w-0 items-center gap-2">
          <Trophy className="h-5 w-5 shrink-0 text-amber-400" aria-hidden />
          <p className="text-sm font-bold text-white sm:text-base">이번 주 스타</p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <div className="flex gap-1" aria-hidden>
            {WEEKLY_KING_SLIDES.map((s, i) => (
              <span
                key={s.id}
                className={cn(
                  "h-1.5 w-1.5 rounded-full transition-colors",
                  i === index ? "bg-amber-400" : "bg-zinc-600"
                )}
              />
            ))}
          </div>
          <button
            type="button"
            onClick={() => goTo(index - 1)}
            className="rounded-lg border border-zinc-700 p-1.5 text-zinc-400 hover:border-zinc-500 hover:text-white"
            aria-label="이전 순위표"
          >
            <ChevronLeft className="h-4 w-4" aria-hidden />
          </button>
          <button
            type="button"
            onClick={() => goTo(index + 1)}
            className="rounded-lg border border-zinc-700 p-1.5 text-zinc-400 hover:border-zinc-500 hover:text-white"
            aria-label="다음 순위표"
          >
            <ChevronRight className="h-4 w-4" aria-hidden />
          </button>
        </div>
      </div>

      <div key={slide.id} className="mt-4 animate-in fade-in duration-500" aria-live="polite">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <span
              className={cn(
                "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-[11px] font-semibold",
                isVocal
                  ? "border-zinc-300 bg-white text-zinc-900"
                  : "border-zinc-600 bg-zinc-900 text-zinc-200"
              )}
            >
              {isVocal ? (
                <AudioLines className="h-3 w-3" aria-hidden />
              ) : (
                <Music4 className="h-3 w-3" aria-hidden />
              )}
              {slide.categoryLabel}
            </span>
            <p className="mt-2 truncate text-lg font-semibold">{slide.songTitle}</p>
            <p className="truncate text-sm text-zinc-400">{slide.songArtist}</p>
          </div>
          <p className="shrink-0 text-right text-[10px] leading-4 text-zinc-500">
            해당 곡
            <br />
            TOP 10
          </p>
        </div>

        <ol className="mt-3 max-h-[14.5rem] space-y-1 overflow-y-auto pr-0.5 sm:max-h-[15.5rem] sm:space-y-1.5">
          {slide.entries.map((entry) => (
            <RankRow key={`${slide.id}-${entry.rank}`} entry={entry} highlight={entry.rank <= 3} />
          ))}
        </ol>

        <p className="mt-3 text-[10px] text-zinc-500">
          음정·박자 평균 점수 기준 · API 연동 후 실제 순위가 표시됩니다.
        </p>
      </div>
    </div>
  )
}
