"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Crown, Trophy } from "lucide-react"
import { LoadingBlock, StatusNote } from "@/components/common/status-note"
import { useUserSession } from "@/hooks/use-user-session"
import { fetchChallengeRanking, type ChallengeRanking } from "@/lib/music-challenge-api"
import { toUserFacingMessage, UI_ERRORS } from "@/lib/user-facing-error"
import { cn } from "@/lib/utils"

type ChallengeRankingSectionProps = {
  challengeId: number
}

/**
 * 곡별 노래방·연주 랭킹. 한 사람은 자기 최고 기록 하나로만 오른다.
 * 점수는 서버가 녹음을 정답 음표와 다시 맞춰 본 값이라 화면 점수와 조금 다를 수 있다.
 */
export function ChallengeRankingSection({ challengeId }: ChallengeRankingSectionProps) {
  const user = useUserSession()
  const [ranking, setRanking] = useState<ChallengeRanking | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    fetchChallengeRanking(challengeId)
      .then((r) => {
        if (alive) setRanking(r)
      })
      .catch((e) => {
        if (alive) setError(toUserFacingMessage(e, UI_ERRORS.requestFailed))
      })
    return () => {
      alive = false
    }
    // 로그인 상태가 바뀌면 내 순위를 다시 받아 온다.
  }, [challengeId, user])

  const me = ranking?.me ?? null

  return (
    <section id="ranking" className="mt-6 scroll-mt-24 rounded-3xl border border-border bg-card p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Trophy className="h-5 w-5 text-neon-yellow" aria-hidden="true" />
          <h2 className="font-display text-xl text-white">이 곡 랭킹</h2>
        </div>
        {me && (
          <p className="text-sm">
            내 순위 <strong className="font-orbitron text-neon-pink">{me.rank}위</strong>
            <span className="text-muted-foreground"> · 최고 {me.best_score}점</span>
          </p>
        )}
      </div>

      {!ranking && !error && (
        <LoadingBlock label="랭킹을 불러오는 중입니다." className="mt-5 h-32" />
      )}
      {error && <StatusNote className="mt-5">{error}</StatusNote>}

      {ranking && ranking.items.length === 0 && (
        <StatusNote className="mt-5">
          아직 노래방 기록이 없습니다. 첫 번째 주인공이 되어 보세요.
        </StatusNote>
      )}

      {ranking && ranking.items.length > 0 && (
        <ol className="mt-5 space-y-1.5">
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
                    "flex h-7 w-7 shrink-0 items-center justify-center rounded-md font-orbitron text-xs font-bold tabular-nums",
                    entry.rank === 1
                      ? "bg-neon-yellow text-night-950 shadow-[0_0_12px_-2px_#ffd23f]"
                      : entry.rank <= 3
                        ? "border border-neon-cyan/50 text-neon-cyan"
                        : "text-muted-foreground"
                  )}
                >
                  {entry.rank}
                </span>
                <span className="min-w-0 flex-1 truncate font-medium">
                  {entry.nickname}
                  {isMe && <span className="ml-1.5 text-xs text-neon-pink">나</span>}
                </span>
                <span className="hidden shrink-0 font-orbitron text-xs text-muted-foreground sm:inline">
                  음정 {entry.pitch_accuracy ?? "—"}% · 박자 {entry.timing_accuracy ?? "—"}%
                </span>
                <span className="w-12 shrink-0 text-right font-orbitron font-bold tabular-nums text-white">
                  {entry.score}
                </span>
                {entry.rank === 1 && <Crown className="h-4 w-4 shrink-0 text-neon-yellow" aria-hidden="true" />}
              </li>
            )
          })}
        </ol>
      )}

      {!user && (
        <p className="mt-4 text-xs text-muted-foreground">
          <Link href="/auth" className="text-neon-cyan underline underline-offset-2">
            로그인
          </Link>
          하고 노래방 모드로 도전하면 랭킹에 이름이 올라갑니다.
        </p>
      )}
    </section>
  )
}
