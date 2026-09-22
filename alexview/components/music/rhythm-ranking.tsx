"use client"

import { useEffect, useState } from "react"
import { Trophy } from "lucide-react"
import { LoadingBlock, StatusNote } from "@/components/common/status-note"
import { useUserSession } from "@/hooks/use-user-session"
import {
  RHYTHM_DIFFICULTY_LABEL,
  fetchRhythmRanking,
  type RhythmDifficulty,
  type RhythmKeys,
  type RhythmRanking,
} from "@/lib/rhythm-api"
import { toUserFacingMessage, UI_ERRORS } from "@/lib/user-facing-error"
import { cn } from "@/lib/utils"

type RhythmRankingListProps = {
  challengeId: number
  keys: RhythmKeys
  difficulty: RhythmDifficulty
  /** 값이 바뀌면 다시 불러온다 — 방금 제출한 기록을 바로 보여 줄 때 */
  refreshKey?: number
}

/** 채보(키 수·난이도)별 리듬 게임 랭킹. 한 사람은 자기 최고 기록 하나로만 오른다. */
export function RhythmRankingList({
  challengeId,
  keys,
  difficulty,
  refreshKey = 0,
}: RhythmRankingListProps) {
  const user = useUserSession()
  const [ranking, setRanking] = useState<RhythmRanking | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    setRanking(null)
    setError(null)
    fetchRhythmRanking(challengeId, keys, difficulty)
      .then((r) => {
        if (alive) setRanking(r)
      })
      .catch((e) => {
        if (alive) setError(toUserFacingMessage(e, UI_ERRORS.requestFailed))
      })
    return () => {
      alive = false
    }
  }, [challengeId, keys, difficulty, refreshKey, user])

  const me = ranking?.me ?? null

  return (
    <section className="rounded-3xl border border-border bg-card p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Trophy className="h-5 w-5 text-neon-yellow" aria-hidden="true" />
          <h2 className="font-display text-lg text-white">
            랭킹 · {keys}키 {RHYTHM_DIFFICULTY_LABEL[difficulty]}
          </h2>
        </div>
        {me && (
          <p className="text-sm">
            내 순위 <strong className="font-orbitron text-neon-pink">{me.rank}위</strong>
            <span className="text-muted-foreground">
              {" "}
              · 최고 {me.best_score.toLocaleString()}점
            </span>
          </p>
        )}
      </div>

      {!ranking && !error && <LoadingBlock label="랭킹을 불러오는 중입니다." className="mt-4 h-24" />}
      {error && <StatusNote className="mt-4">{error}</StatusNote>}
      {ranking && ranking.items.length === 0 && (
        <StatusNote className="mt-4">아직 기록이 없습니다. 첫 번째 기록을 남겨 보세요.</StatusNote>
      )}
      {ranking && ranking.items.length > 0 && (
        <ol className="mt-4 space-y-1.5">
          {ranking.items.map((entry, i) => {
            const isMe = !!me && entry.rank === me.rank && entry.score === me.best_score
            return (
              <li
                key={`${entry.rank}-${entry.nickname}-${i}`}
                className={cn(
                  "flex items-center gap-3 rounded-xl border px-3 py-2 text-sm",
                  isMe ? "border-neon-pink/60 bg-neon-pink/10 shadow-[0_0_16px_-6px_#ff2e97]" : "border-border bg-night-950/60"
                )}
              >
                <span
                  className={cn(
                    "w-8 text-center font-orbitron font-bold",
                    entry.rank === 1
                      ? "text-neon-yellow"
                      : entry.rank <= 3
                        ? "text-neon-cyan"
                        : "text-muted-foreground"
                  )}
                >
                  {entry.rank}
                </span>
                <span className="min-w-0 flex-1 truncate">{entry.nickname}</span>
                <span className="hidden font-orbitron text-xs text-muted-foreground sm:inline">
                  {entry.accuracy.toFixed(2)}% · {entry.max_combo} COMBO
                </span>
                <span className="font-orbitron font-bold tabular-nums text-white">
                  {entry.score.toLocaleString()}
                </span>
              </li>
            )
          })}
        </ol>
      )}
    </section>
  )
}
