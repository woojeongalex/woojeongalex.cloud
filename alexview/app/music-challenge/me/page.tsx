"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { ArrowLeft, ArrowRight, TrendingUp } from "lucide-react"
import { StatCard } from "@/components/common/stat-card"
import { LoadingBlock, StatusNote } from "@/components/common/status-note"
import { ScoreTrend } from "@/components/music/score-trend"
import { useUserSession } from "@/hooks/use-user-session"
import {
  CHALLENGE_TYPE_LABEL,
  fetchMyHistory,
  type HistoryItem,
} from "@/lib/music-challenge-api"
import { toUserFacingMessage, UI_ERRORS } from "@/lib/user-facing-error"

type ScoredItem = HistoryItem & { score: number }

export default function MyHistoryPage() {
  const user = useUserSession()
  const [mounted, setMounted] = useState(false)
  const [items, setItems] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => setMounted(true), [])

  useEffect(() => {
    if (!mounted) return
    if (!user) {
      setLoading(false)
      return
    }
    let alive = true
    fetchMyHistory()
      .then((data) => {
        if (alive) setItems(data.items)
      })
      .catch((e) => {
        if (alive) setError(toUserFacingMessage(e, UI_ERRORS.challengeLoadFailed))
      })
      .finally(() => {
        if (alive) setLoading(false)
      })
    return () => {
      alive = false
    }
  }, [mounted, user])

  const scored = items.filter((i): i is ScoredItem => i.score !== null)
  const best = scored.length ? Math.max(...scored.map((i) => i.score)) : null
  const average = scored.length
    ? Math.round(scored.reduce((sum, i) => sum + i.score, 0) / scored.length)
    : null
  // 서버는 최신순으로 주므로, 추이는 오래된 것부터 그린다.
  const trend = scored.map((i) => i.score).reverse()

  return (
    <main className="min-h-[calc(100vh-4rem)] min-w-0 overflow-x-hidden bg-background text-foreground">
      <div className="mx-auto max-w-4xl px-4 py-10 md:py-14">
        <Link
          href="/music-challenge"
          className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          챌린지 목록
        </Link>

        <p
          aria-hidden="true"
          className="mt-6 font-orbitron text-xs font-bold tracking-[0.25em] text-neon-cyan animate-in fade-in slide-in-from-bottom-4 duration-700"
        >
          MY HISTORY
        </p>
        <h1
          className="neon-text mt-2 font-display text-4xl text-white animate-in fade-in slide-in-from-bottom-6 duration-700 fill-mode-both sm:text-5xl"
          style={{ animationDelay: "120ms" }}
        >
          내 도전 기록
        </h1>
        <p
          className="mt-4 text-base leading-8 text-foreground/85 animate-in fade-in slide-in-from-bottom-6 duration-700 fill-mode-both"
          style={{ animationDelay: "240ms" }}
        >
          제출할 때마다 점수가 쌓입니다. 같은 곡을 다시 불러 얼마나 나아졌는지
          확인해 보세요.
        </p>

        {!mounted && (
          <LoadingBlock label="기록을 불러오는 중입니다." className="mt-8 h-40" />
        )}

        {mounted && !user && (
          <StatusNote className="mt-8">
            도전 기록은 로그인한 뒤에 볼 수 있습니다. 비로그인으로 참여한 제출은
            기록에 남지 않습니다.
          </StatusNote>
        )}

        {mounted && user && loading && (
          <LoadingBlock label="기록을 불러오는 중입니다." className="mt-8 h-40" />
        )}

        {mounted && user && !loading && error && (
          <StatusNote className="mt-8">{error}</StatusNote>
        )}

        {mounted && user && !loading && !error && items.length === 0 && (
          <div className="mt-8 rounded-3xl border border-dashed border-neon-pink/40 bg-card px-5 py-8 text-center">
            <p className="text-sm text-muted-foreground">아직 도전 기록이 없습니다.</p>
            <Link
              href="/music-challenge"
              className="mt-5 inline-flex items-center gap-2 glow-button rounded-full bg-primary px-5 py-3 text-sm font-bold text-primary-foreground"
            >
              첫 챌린지 시작하기
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          </div>
        )}

        {mounted && user && !loading && !error && items.length > 0 && (
          <>
            <section className="mt-8 grid gap-4 sm:grid-cols-3">
              <StatCard label="총 도전" value={`${items.length}회`} />
              <StatCard label="평균 점수" value={average === null ? "—" : `${average}`} />
              <StatCard label="최고 점수" value={best === null ? "—" : `${best}`} />
            </section>

            {trend.length >= 2 && (
              <section className="mt-6 rounded-3xl border border-border bg-card p-6">
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-neon-pink" aria-hidden="true" />
                  <h2 className="font-display text-base text-white">점수 추이</h2>
                  <span className="ml-auto font-orbitron text-xs text-muted-foreground">
                    오래된 순 → 최근
                  </span>
                </div>
                <ScoreTrend scores={trend} />
              </section>
            )}

            <section className="mt-6 space-y-3">
              {items.map((item) => (
                <Link
                  key={item.submission_id}
                  href={`/music-challenge/${item.challenge_id}`}
                  className="glow-card flex items-center gap-4 rounded-2xl border border-border bg-card p-4"
                >
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-white">{item.challenge_title}</p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {CHALLENGE_TYPE_LABEL[item.challenge_type] ?? item.challenge_type}
                      {" · "}
                      {new Date(item.created_at).toLocaleDateString("ko-KR")}
                      {item.pitch_score !== null && (
                        <>
                          {" · 음정 "}
                          {item.pitch_score}
                          {" · 박자 "}
                          {item.rhythm_score}
                        </>
                      )}
                    </p>
                  </div>
                  <span className="shrink-0 font-orbitron text-xl font-bold text-neon-cyan">
                    {item.score ?? "—"}
                  </span>
                </Link>
              ))}
            </section>
          </>
        )}
      </div>
    </main>
  )
}
