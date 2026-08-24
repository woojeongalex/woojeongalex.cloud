"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { ArrowRight, Mic2, Music4, Sparkles } from "lucide-react"
import {
  CHALLENGE_TYPE_LABEL,
  fetchChallenges,
  type Challenge,
} from "@/lib/music-challenge-api"
import { toUserFacingMessage, UI_ERRORS } from "@/lib/user-facing-error"

const STEPS = [
  {
    n: "01",
    icon: Music4,
    title: "AI 음악 듣기",
    description: "운영자가 올린 AI 생성 음악을 듣고 따라 부를 곡을 고릅니다.",
  },
  {
    n: "02",
    icon: Mic2,
    title: "영상 · 음성 제출",
    description: "노래하거나 연주하는 모습을 녹음·녹화해서 그대로 올립니다.",
  },
  {
    n: "03",
    icon: Sparkles,
    title: "AI 채점 · 다음 추천",
    description: "AI가 점수와 피드백을 주고, 실력에 맞는 다음 챌린지를 추천합니다.",
  },
]

export default function MusicChallengePage() {
  const [challenges, setChallenges] = useState<Challenge[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let alive = true
    fetchChallenges()
      .then((data) => {
        if (alive) setChallenges(data.items)
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
    <main className="min-h-[calc(100vh-4rem)] min-w-0 overflow-x-hidden bg-background text-foreground">
      {/* HERO */}
      <section className="border-b border-border">
        <div className="mx-auto max-w-6xl px-4 py-12 md:py-16">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-muted px-3 py-1 text-[11px] font-semibold tracking-wide text-muted-foreground">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-foreground" />
            AI MUSIC CHALLENGE
          </span>
          <h1 className="mt-5 max-w-3xl text-4xl font-semibold leading-[1.1] tracking-tight sm:text-5xl">
            AI가 만든 음악에 도전하고,
            <br />
            AI에게 채점받으세요.
          </h1>
          <p className="mt-6 max-w-2xl text-base leading-8 text-muted-foreground">
            원하는 챌린지를 골라 노래하거나 연주한 영상·음성을 올리면, AI가 점수와
            피드백을 남기고 다음에 도전할 챌린지를 추천합니다.
          </p>

          <div className="mt-10 grid gap-5 md:grid-cols-3">
            {STEPS.map((step) => (
              <article
                key={step.n}
                className="relative rounded-3xl border border-border bg-card p-6"
              >
                <span className="absolute right-6 top-6 font-mono text-xs text-muted-foreground/50">
                  {step.n}
                </span>
                <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-border bg-muted">
                  <step.icon className="h-5 w-5" aria-hidden="true" />
                </div>
                <h2 className="mt-5 text-xl font-semibold">{step.title}</h2>
                <p className="mt-3 text-sm leading-6 text-muted-foreground">
                  {step.description}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* LIST */}
      <section className="mx-auto max-w-6xl px-4 py-12 md:py-14">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">진행 중인 챌린지</p>
            <h2 className="mt-2 text-3xl font-semibold tracking-tight">
              지금 도전할 수 있는 곡
            </h2>
          </div>
          {!loading && !error && (
            <p className="font-mono text-sm text-muted-foreground">
              총 {challenges.length}개
            </p>
          )}
        </div>

        {loading && (
          <div className="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-3" role="status">
            <span className="sr-only">챌린지를 불러오는 중입니다.</span>
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="h-52 animate-pulse rounded-3xl border border-border bg-muted/40"
              />
            ))}
          </div>
        )}

        {!loading && error && (
          <p
            role="status"
            className="mt-8 rounded-2xl border border-border bg-muted/40 px-5 py-6 text-sm text-muted-foreground"
          >
            {error}
          </p>
        )}

        {!loading && !error && challenges.length === 0 && (
          <p
            role="status"
            className="mt-8 rounded-2xl border border-border bg-muted/40 px-5 py-6 text-sm text-muted-foreground"
          >
            아직 등록된 챌린지가 없습니다. 새로운 챌린지가 올라오면 여기에 표시됩니다.
          </p>
        )}

        {!loading && !error && challenges.length > 0 && (
          <div className="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {challenges.map((challenge) => (
              <Link
                key={challenge.id}
                href={`/music-challenge/${challenge.id}`}
                className="group flex flex-col rounded-3xl border border-border bg-card p-6 transition-colors hover:border-foreground/40 hover:bg-muted/40"
              >
                <span className="w-fit rounded-full border border-border bg-muted px-3 py-1 text-xs text-muted-foreground">
                  {CHALLENGE_TYPE_LABEL[challenge.challenge_type] ??
                    challenge.challenge_type}
                </span>
                <h3 className="mt-4 text-xl font-semibold">{challenge.title}</h3>
                <p className="mt-3 line-clamp-3 flex-1 text-sm leading-6 text-muted-foreground">
                  {challenge.description}
                </p>
                <span className="mt-5 inline-flex items-center gap-2 text-sm font-medium">
                  도전하기
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </span>
              </Link>
            ))}
          </div>
        )}
      </section>
    </main>
  )
}
