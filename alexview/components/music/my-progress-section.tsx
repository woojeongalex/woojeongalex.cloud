"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { ArrowRight, TrendingUp } from "lucide-react"
import { SectionHeading } from "@/components/common/section-heading"
import { StatCard } from "@/components/common/stat-card"
import { LoadingBlock } from "@/components/common/status-note"
import { ScoreTrend } from "@/components/music/score-trend"
import { useUserSession } from "@/hooks/use-user-session"
import { fetchMyHistory, type HistoryItem } from "@/lib/music-challenge-api"

const PREVIEW_LIMIT = 10

type ScoredItem = HistoryItem & { score: number }

/**
 * 로그인한 사람에게만 보이는 내 진척도 요약.
 *
 * 기록 페이지까지 들어가지 않아도 "나아지고 있다"가 홈에서 보이게 한다.
 * 실패하더라도 홈 전체가 깨지면 안 되므로 에러는 조용히 섹션을 숨긴다.
 */
export function MyProgressSection() {
  const user = useUserSession()
  const [items, setItems] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    if (!user) return
    let alive = true
    setLoading(true)
    fetchMyHistory(PREVIEW_LIMIT)
      .then((data) => {
        if (alive) setItems(data.items)
      })
      .catch(() => {
        if (alive) setFailed(true)
      })
      .finally(() => {
        if (alive) setLoading(false)
      })
    return () => {
      alive = false
    }
  }, [user])

  if (!user || failed) return null

  const scored = items.filter((i): i is ScoredItem => i.score !== null)
  const best = scored.length ? Math.max(...scored.map((i) => i.score)) : null
  const average = scored.length
    ? Math.round(scored.reduce((sum, i) => sum + i.score, 0) / scored.length)
    : null
  // 서버는 최신순으로 주므로, 추이는 오래된 것부터 그린다.
  const trend = scored.map((i) => i.score).reverse()

  return (
    <section className="border-b border-border bg-night-900">
      <div className="mx-auto max-w-6xl px-4 py-12 md:py-14">
        <SectionHeading
          label="내 진척도"
          title="얼마나 나아졌는지 보기"
          action={
            <Link
              href="/music-challenge/me"
              className="inline-flex items-center gap-1.5 rounded-full border border-neon-cyan/60 px-4 py-2 text-sm font-medium text-neon-cyan transition-colors hover:bg-neon-cyan/10"
            >
              전체 기록
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          }
        />

        {loading && <LoadingBlock label="기록을 불러오는 중입니다." className="mt-8 h-32" />}

        {!loading && items.length === 0 && (
          <div className="mt-8 rounded-3xl border border-dashed border-neon-pink/40 bg-card px-5 py-8 text-center">
            <p className="text-sm text-muted-foreground">
              아직 도전 기록이 없습니다. 한 곡만 불러도 점수가 쌓이기 시작합니다.
            </p>
          </div>
        )}

        {!loading && items.length > 0 && (
          <div className="mt-8 grid gap-4 lg:grid-cols-[1fr_1.2fr] lg:items-stretch">
            <div className="grid grid-cols-3 gap-3 sm:gap-4 lg:grid-cols-1">
              <StatCard label="총 도전" value={`${items.length}회`} />
              <StatCard label="평균 점수" value={average === null ? "—" : `${average}`} />
              <StatCard label="최고 점수" value={best === null ? "—" : `${best}`} />
            </div>
            <div className="rounded-3xl border border-border bg-card p-6">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-neon-pink" aria-hidden="true" />
                <h3 className="font-display text-base text-white">점수 추이</h3>
                <span className="ml-auto font-orbitron text-xs text-muted-foreground">
                  오래된 순 → 최근
                </span>
              </div>
              {trend.length >= 2 ? (
                <ScoreTrend scores={trend} className="mt-4 h-28 w-full" />
              ) : (
                <p className="mt-4 text-sm text-muted-foreground">
                  두 번째 도전부터 추이가 그려집니다.
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </section>
  )
}
