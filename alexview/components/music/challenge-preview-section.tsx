"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { ArrowRight } from "lucide-react"
import { SectionHeading } from "@/components/common/section-heading"
import { LoadingBlock, StatusNote } from "@/components/common/status-note"
import { ChallengeCard } from "@/components/music/challenge-card"
import { fetchChallenges, type Challenge } from "@/lib/music-challenge-api"
import { toUserFacingMessage, UI_ERRORS } from "@/lib/user-facing-error"

const PREVIEW_COUNT = 3

/**
 * 홈에서 바로 도전할 곡을 보여주는 섹션.
 *
 * 예전 홈은 챌린지를 전혀 드러내지 않아 MENU 드롭다운을 열어야만
 * 핵심 기능에 닿을 수 있었다. 처음 온 사람이 무엇을 하는 서비스인지
 * 알 수 있도록 실제 목록을 그대로 꺼내 둔다.
 */
export function ChallengePreviewSection() {
  const [challenges, setChallenges] = useState<Challenge[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    fetchChallenges()
      .then((data) => {
        if (!alive) return
        setChallenges(data.items.slice(0, PREVIEW_COUNT))
        setTotal(data.total || data.items.length)
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
  }, [])

  return (
    <section className="border-b border-border">
      <div className="mx-auto max-w-6xl px-4 py-12 md:py-16">
        <SectionHeading
          label="지금 도전할 수 있는 곡"
          title="AI가 만든 음악, 골라서 불러보세요"
          action={
            <Link
              href="/music-challenge"
              className="inline-flex items-center gap-1.5 rounded-full border border-border bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent"
            >
              {total > 0 ? `전체 ${total}곡 보기` : "챌린지 전체 보기"}
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          }
        />

        {loading && (
          <div className="mt-8 grid gap-5 md:grid-cols-3">
            {[0, 1, 2].map((i) => (
              <LoadingBlock key={i} label="챌린지를 불러오는 중입니다." className="h-52" />
            ))}
          </div>
        )}

        {!loading && error && <StatusNote className="mt-8">{error}</StatusNote>}

        {!loading && !error && challenges.length === 0 && (
          <StatusNote className="mt-8">
            아직 등록된 챌린지가 없습니다. 새로운 곡이 올라오면 여기에 표시됩니다.
          </StatusNote>
        )}

        {!loading && !error && challenges.length > 0 && (
          <div className="mt-8 grid gap-5 md:grid-cols-3">
            {challenges.map((challenge) => (
              <ChallengeCard key={challenge.id} challenge={challenge} />
            ))}
          </div>
        )}
      </div>
    </section>
  )
}
