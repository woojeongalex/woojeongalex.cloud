"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { History, Mic2, Music4, Plus, Sparkles } from "lucide-react"
import { EyebrowBadge, SectionHeading } from "@/components/common/section-heading"
import { LoadingBlock, StatusNote } from "@/components/common/status-note"
import { SynthBackdrop } from "@/components/common/synth-backdrop"
import { ChallengeCard } from "@/components/music/challenge-card"
import { useUserSession } from "@/hooks/use-user-session"
import {
  fetchChallenges,
  fetchMyHistory,
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
    title: "녹음 · 녹화 제출",
    description: "브라우저에서 바로 녹음하거나, 녹화해 둔 영상을 올립니다.",
  },
  {
    n: "03",
    icon: Sparkles,
    title: "AI 채점 · 다음 추천",
    description: "음정·박자 수치와 AI 피드백을 받고, 실력에 맞는 다음 곡을 추천받습니다.",
  },
]

export default function MusicChallengePage() {
  const user = useUserSession()
  const [challenges, setChallenges] = useState<Challenge[]>([])
  const [attemptedIds, setAttemptedIds] = useState<Set<number>>(new Set())
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

  // 이미 도전한 곡을 표시하기 위한 보조 조회. 실패해도 목록은 그대로 보여준다.
  useEffect(() => {
    if (!user) {
      setAttemptedIds(new Set())
      return
    }
    let alive = true
    fetchMyHistory(100)
      .then((data) => {
        if (alive) setAttemptedIds(new Set(data.items.map((i) => i.challenge_id)))
      })
      .catch(() => {
        if (alive) setAttemptedIds(new Set())
      })
    return () => {
      alive = false
    }
  }, [user])

  return (
    <main className="min-h-[calc(100vh-4rem)] min-w-0 overflow-x-hidden bg-background text-foreground">
      {/* HERO — 석양과 격자 바닥 위에 챌린지 소개 */}
      <section className="relative overflow-hidden border-b border-border">
        <SynthBackdrop sunSize={300} horizon={0.5} />
        <div className="relative mx-auto flex min-h-[380px] max-w-6xl flex-col items-center px-4 pb-12 pt-12 text-center md:pt-16">
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
            <EyebrowBadge>AI MUSIC CHALLENGE</EyebrowBadge>
          </div>
          <h1
            className="neon-text mt-5 max-w-3xl font-display text-4xl leading-[1.1] text-white animate-in fade-in slide-in-from-bottom-6 duration-700 fill-mode-both sm:text-5xl"
            style={{ animationDelay: "120ms" }}
          >
            AI가 만든 음악에 도전하고,
            <br />
            AI에게 채점받으세요.
          </h1>
          <p
            className="mt-6 max-w-2xl text-base leading-8 text-foreground/85 animate-in fade-in slide-in-from-bottom-6 duration-700 fill-mode-both"
            style={{ animationDelay: "240ms" }}
          >
            원하는 챌린지를 골라 노래하거나 연주한 영상·음성을 올리면, AI가 점수와
            피드백을 남기고 다음에 도전할 챌린지를 추천합니다.
          </p>

          <div className="mt-24 grid w-full gap-5 text-left md:mt-32 md:grid-cols-3">
            {STEPS.map((step, i) => (
              <article
                key={step.n}
                className="relative rounded-3xl border border-border bg-card/85 p-6 backdrop-blur animate-in fade-in slide-in-from-bottom-6 duration-700 fill-mode-both"
                style={{ animationDelay: `${360 + i * 120}ms` }}
              >
                <span className="absolute right-6 top-6 font-orbitron text-xs font-bold text-neon-cyan">
                  {step.n}
                </span>
                <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-neon-pink/40 bg-neon-pink/10 text-neon-pink">
                  <step.icon className="h-5 w-5" aria-hidden="true" />
                </div>
                <h2 className="mt-5 font-display text-xl text-white">{step.title}</h2>
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
        <SectionHeading
          label="진행 중인 챌린지"
          title="지금 도전할 수 있는 곡"
          action={
            <>
              {!loading && !error && (
                <p className="font-orbitron text-sm text-muted-foreground">
                  총 {challenges.length}개
                </p>
              )}
              {user && (
                <Link
                  href="/music-challenge/me"
                  className="inline-flex items-center gap-1.5 rounded-full border border-neon-cyan/60 px-4 py-2 text-sm font-medium text-neon-cyan transition-colors hover:bg-neon-cyan/10"
                >
                  <History className="h-4 w-4" aria-hidden="true" />
                  내 기록
                </Link>
              )}
              {user?.role === "admin" && (
                <Link
                  href="/music-challenge/new"
                  className="inline-flex items-center gap-1.5 rounded-full border border-neon-cyan/60 px-4 py-2 text-sm font-medium text-neon-cyan transition-colors hover:bg-neon-cyan/10"
                >
                  <Plus className="h-4 w-4" aria-hidden="true" />
                  챌린지 등록
                </Link>
              )}
            </>
          }
        />

        {loading && (
          <div className="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {[0, 1, 2].map((i) => (
              <LoadingBlock key={i} label="챌린지를 불러오는 중입니다." className="h-52" />
            ))}
          </div>
        )}

        {!loading && error && <StatusNote className="mt-8">{error}</StatusNote>}

        {!loading && !error && challenges.length === 0 && (
          <StatusNote className="mt-8">
            아직 등록된 챌린지가 없습니다. 새로운 챌린지가 올라오면 여기에 표시됩니다.
          </StatusNote>
        )}

        {!loading && !error && challenges.length > 0 && (
          <div className="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {challenges.map((challenge) => (
              <ChallengeCard
                key={challenge.id}
                challenge={challenge}
                attempted={attemptedIds.has(challenge.id)}
              />
            ))}
          </div>
        )}
      </section>
    </main>
  )
}
