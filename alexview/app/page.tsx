"use client"

import Link from "next/link"
import {
  ArrowRight,
  AudioLines,
  Guitar,
  Mic2,
  MessageSquare,
  Music4,
  Sparkles,
} from "lucide-react"
import { EyebrowBadge, SectionHeading } from "@/components/common/section-heading"
import { ExaoneChatBanner } from "@/components/exaone-chat-banner"
import { GeminiChat } from "@/components/gemini-chat"
import { IuemGuideCarousel } from "@/components/iuem-guide-carousel"
import { ChallengePreviewSection } from "@/components/music/challenge-preview-section"
import { MyProgressSection } from "@/components/music/my-progress-section"
import { WeeklyKingBanner } from "@/components/weekly-king-banner"
import { useUserSession } from "@/hooks/use-user-session"

const LOOP_STEPS = [
  {
    n: "01",
    icon: Mic2,
    title: "부른다",
    description:
      "AI가 만든 곡을 고르고, 브라우저에서 바로 녹음하거나 녹화한 파일을 올립니다.",
  },
  {
    n: "02",
    icon: AudioLines,
    title: "분석한다",
    description:
      "음정과 박자는 신호 분석으로 수치를 내고, 그 수치를 근거로 AI가 무엇을 고칠지 짚어줍니다.",
  },
  {
    n: "03",
    icon: Sparkles,
    title: "다음 곡을 받는다",
    description:
      "점수가 낮으면 같은 유형으로 한 번 더, 잘했으면 다른 유형으로. 이미 부른 곡은 빼고 고릅니다.",
  },
]

const LAB_TOOLS = [
  {
    href: "/analyze",
    icon: AudioLines,
    title: "보컬 분석",
    description: "가요·뮤지컬 넘버를 골라 부르고 구간별 발성을 살펴보는 실험 화면입니다.",
  },
  {
    href: "/instrument",
    icon: Guitar,
    title: "악기 튜닝",
    description: "기타·피아노의 음정 상태를 확인하는 화면입니다.",
  },
  {
    href: "/speech",
    icon: MessageSquare,
    title: "스피치",
    description: "발표·낭독 속도와 전달력을 점검하는 화면입니다.",
  },
]

export default function HomePage() {
  const user = useUserSession()

  return (
    <main className="min-h-[calc(100vh-4rem)] min-w-0 overflow-x-hidden bg-background text-foreground">
      {/* HERO — 핵심 루프 */}
      <section className="border-b border-border">
        <div className="mx-auto max-w-6xl px-4 py-14 md:py-20">
          <EyebrowBadge>IUEM AI MUSIC CHALLENGE</EyebrowBadge>
          <h1 className="mt-6 max-w-4xl text-4xl font-semibold leading-[1.08] tracking-tight sm:text-5xl md:text-6xl">
            부르면 AI가 채점하고,
            <br />
            다음에 부를 곡까지 골라줍니다.
          </h1>
          <p className="mt-7 max-w-2xl text-base leading-8 text-muted-foreground">
            AI가 만든 곡을 골라 노래하거나 연주하면, 음정·박자를 수치로 재고 그
            근거 위에 AI 코칭을 붙여 돌려줍니다. 점수에 맞춰 다음 챌린지까지
            이어지도록 설계했습니다.
          </p>

          <div className="mt-9 flex flex-wrap items-center gap-3">
            <Link
              href="/music-challenge"
              className="inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3.5 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-80"
            >
              <Music4 className="h-4 w-4" aria-hidden="true" />
              챌린지 시작하기
            </Link>
            <Link
              href={user ? "/music-challenge/me" : "/auth"}
              className="inline-flex items-center gap-2 rounded-full border border-border bg-background px-6 py-3.5 text-sm font-semibold transition-colors hover:bg-accent"
            >
              {user ? "내 기록 보기" : "로그인하고 기록 쌓기"}
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          </div>

          <div className="mt-14 grid gap-5 md:grid-cols-3">
            {LOOP_STEPS.map((step) => (
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

      <ChallengePreviewSection />

      <MyProgressSection />

      {/* 실험 중인 도구들 */}
      <section className="border-b border-border">
        <div className="mx-auto max-w-6xl px-4 py-12 md:py-14">
          <SectionHeading
            label="실험실"
            title="따로 만들어 보고 있는 화면"
            action={
              <p className="max-w-xs text-xs leading-5 text-muted-foreground sm:text-right">
                챌린지와 달리 아직 실측 분석이 붙지 않았습니다. 화면과 흐름을
                먼저 잡아 둔 단계입니다.
              </p>
            }
          />
          <div className="mt-8 grid gap-5 md:grid-cols-3">
            {LAB_TOOLS.map((tool) => (
              <Link
                key={tool.href}
                href={tool.href}
                className="group flex flex-col rounded-3xl border border-dashed border-border bg-card p-6 transition-colors hover:border-foreground/40 hover:bg-muted/40"
              >
                <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-border bg-muted">
                  <tool.icon className="h-5 w-5" aria-hidden="true" />
                </div>
                <h3 className="mt-5 text-xl font-semibold">{tool.title}</h3>
                <p className="mt-3 flex-1 text-sm leading-6 text-muted-foreground">
                  {tool.description}
                </p>
                <span className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-muted-foreground">
                  둘러보기
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* AI 에게 물어보기 */}
      <section className="border-b border-border">
        <div className="mx-auto max-w-6xl px-4 py-12 md:py-14">
          <SectionHeading label="AI 에게 물어보기" title="연습이 막히면 대화로" />
          <div className="mt-8 grid gap-5 lg:grid-cols-2 lg:items-start">
            <GeminiChat layout="sidebar" />
            <ExaoneChatBanner />
          </div>
        </div>
      </section>

      {/* WEEKLY + GUIDE */}
      <section>
        <div className="mx-auto max-w-6xl px-4 py-10 md:py-14">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-5 md:items-start">
            <WeeklyKingBanner />
            <IuemGuideCarousel />
          </div>
        </div>
      </section>
    </main>
  )
}
