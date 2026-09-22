"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { ArrowRight, Crown, Trophy } from "lucide-react"
import { fetchWeeklyRanking, type WeeklyRankingEntry } from "@/lib/music-challenge-api"
import { cn } from "@/lib/utils"

type RankRowProps = {
  entry: WeeklyRankingEntry
}

function RankRow({ entry }: RankRowProps) {
  return (
    <li>
      <Link
        href={`/music-challenge/${entry.challenge_id}#ranking`}
        className={cn(
          "flex items-center gap-2 rounded-lg border px-2.5 py-1.5 text-xs transition-colors hover:border-zinc-500 sm:gap-3 sm:px-3 sm:py-2 sm:text-sm",
          entry.rank <= 3 ? "border-zinc-500/40 bg-zinc-700/30" : "border-zinc-800 bg-zinc-900/50"
        )}
      >
        <span
          className={cn(
            "flex h-6 w-6 shrink-0 items-center justify-center rounded-md text-[11px] font-bold tabular-nums sm:h-7 sm:w-7",
            entry.rank === 1
              ? "bg-white text-zinc-950"
              : entry.rank <= 3
                ? "bg-zinc-200 text-zinc-950"
                : "bg-zinc-800 text-zinc-300"
          )}
        >
          {entry.rank}
        </span>
        <span className="min-w-0 flex-1">
          <span className="block truncate font-medium text-zinc-100">{entry.nickname}</span>
          <span className="block truncate text-[11px] text-zinc-500">{entry.challenge_title}</span>
        </span>
        <span className="hidden shrink-0 tabular-nums text-zinc-400 sm:inline">
          음정 {entry.pitch_accuracy ?? "—"}% · 박자 {entry.timing_accuracy ?? "—"}%
        </span>
        <span className="shrink-0 font-semibold tabular-nums text-white">{entry.score}점</span>
        {entry.rank === 1 && (
          <Crown className="h-3.5 w-3.5 shrink-0 text-white sm:h-4 sm:w-4" aria-hidden />
        )}
      </Link>
    </li>
  )
}

/**
 * 홈의 "이번 주 스타" — 이번 주(한국 시간 월요일 0시부터) 노래방·연주 기록 중
 * 사람마다 가장 높은 한 곡을 서버 채점 점수로 줄 세운다.
 *
 * 예전에는 곡별 가짜 순위표(weekly-king-mock)를 돌려 보여 줬다. 실제 기록이 쌓이는
 * 지금은 빈 표라도 진짜를 보여 주는 편이 낫다.
 */
export function WeeklyKingBanner() {
  const [entries, setEntries] = useState<WeeklyRankingEntry[] | null>(null)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    let alive = true
    fetchWeeklyRanking(10)
      .then((items) => {
        if (alive) setEntries(items)
      })
      .catch(() => {
        if (alive) setFailed(true)
      })
    return () => {
      alive = false
    }
  }, [])

  return (
    <div
      className="h-full w-full rounded-3xl border border-zinc-200 bg-zinc-950 px-5 py-5 text-white shadow-[0_20px_60px_rgba(0,0,0,0.12)] sm:px-6 sm:py-6 dark:border-zinc-800"
      aria-label="이번 주 스타"
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex min-w-0 items-center gap-2">
          <Trophy className="h-5 w-5 shrink-0 text-white" aria-hidden />
          <p className="text-sm font-bold text-white sm:text-base">이번 주 스타</p>
        </div>
        <p className="shrink-0 text-[10px] text-zinc-500">노래방·연주 최고 기록 TOP 10</p>
      </div>

      {entries === null && !failed && (
        <div className="mt-4 space-y-1.5" role="status">
          <span className="sr-only">이번 주 랭킹을 불러오는 중입니다.</span>
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-9 animate-pulse rounded-lg bg-zinc-900" />
          ))}
        </div>
      )}

      {failed && (
        <p role="status" className="mt-4 text-sm text-zinc-400">
          랭킹을 불러오지 못했습니다. 잠시 후 다시 확인해 주세요.
        </p>
      )}

      {entries && entries.length === 0 && (
        <div className="mt-4 rounded-2xl border border-zinc-800 px-4 py-6 text-center">
          <p className="text-sm text-zinc-300">이번 주 첫 기록의 주인공이 되어 보세요.</p>
          <Link
            href="/music-challenge"
            className="mt-3 inline-flex items-center gap-1.5 text-sm font-medium text-sky-400 hover:text-sky-300"
          >
            노래방 모드로 도전하기
            <ArrowRight className="h-4 w-4" aria-hidden />
          </Link>
        </div>
      )}

      {entries && entries.length > 0 && (
        <ol className="mt-4 max-h-[17rem] space-y-1 overflow-y-auto pr-0.5 sm:space-y-1.5">
          {entries.map((entry) => (
            <RankRow key={`${entry.rank}-${entry.nickname}-${entry.challenge_id}`} entry={entry} />
          ))}
        </ol>
      )}

      <p className="mt-3 text-[10px] text-zinc-500">
        서버가 녹음을 원곡의 정답 음표와 맞춰 본 점수 기준 · 한 사람당 최고 기록 하나
      </p>
    </div>
  )
}
