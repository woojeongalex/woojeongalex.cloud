"use client"

import Link from "next/link"
import {
  ArrowRight,
  AudioLines,
  Gamepad2,
  Guitar,
  Mic2,
  MessageSquare,
  Music4,
  Sparkles,
} from "lucide-react"
import { EyebrowBadge, SectionHeading } from "@/components/common/section-heading"
import { SynthBackdrop } from "@/components/common/synth-backdrop"
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
      {/* HERO — 석양과 격자 바닥 위에 핵심 메시지 */}
      <section className="relative overflow-hidden border-b border-border">
        <SynthBackdrop sunSize={400} horizon={0.74} />
        <div className="relative mx-auto flex min-h-[640px] max-w-6xl flex-col items-center px-4 pb-16 pt-16 text-center md:min-h-[720px] md:pt-20">
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
            <EyebrowBadge>NEON NIGHT SESSION</EyebrowBadge>
          </div>
          <h1
            className="neon-text mt-6 max-w-4xl font-display text-5xl leading-[1.05] text-white animate-in fade-in slide-in-from-bottom-6 duration-700 fill-mode-both sm:text-6xl md:text-7xl"
            style={{ animationDelay: "120ms" }}
          >
            부르고, 치고,
            <br />
            랭킹에 오르고.
          </h1>
          <p
            className="mt-6 max-w-2xl text-base font-medium leading-8 text-white [text-shadow:0_1px_14px_#0d0619,0_0_3px_#0d0619] animate-in fade-in slide-in-from-bottom-6 duration-700 fill-mode-both"
            style={{ animationDelay: "240ms" }}
          >
            AI가 만든 곡을 노래방처럼 부르면 음정·박자를 재서 AI 코칭까지 돌려주고, 리듬 게임으로
            치면 판정이 바로 터집니다. 점수는 곡마다 랭킹에 쌓입니다.
          </p>

          <div
            className="mt-9 flex flex-wrap items-center justify-center gap-3 animate-in fade-in slide-in-from-bottom-6 duration-700 fill-mode-both"
            style={{ animationDelay: "360ms" }}
          >
            <Link
              href="/rhythm"
              className="glow-button inline-flex items-center gap-2 rounded-full bg-primary px-7 py-3.5 text-sm font-bold text-primary-foreground"
            >
              <Gamepad2 className="h-4 w-4" aria-hidden="true" />
              리듬 게임 시작
            </Link>
            <Link
              href="/music-challenge"
              className="inline-flex items-center gap-2 rounded-full border border-neon-cyan/70 bg-night-950/70 px-7 py-3.5 text-sm font-semibold text-neon-cyan backdrop-blur transition-colors hover:bg-neon-cyan/10"
            >
              <Music4 className="h-4 w-4" aria-hidden="true" />
              노래방 챌린지
            </Link>
            <Link
              href={user ? "/music-challenge/me" : "/auth"}
              className="inline-flex items-center gap-2 rounded-full px-5 py-3.5 text-sm font-medium text-foreground/80 transition-colors hover:text-white"
            >
              {user ? "내 기록 보기" : "로그인하고 기록 쌓기"}
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          </div>
        </div>
      </section>

      <section className="border-b border-border">
        <div className="mx-auto grid max-w-6xl gap-5 px-4 py-14 md:grid-cols-3">
          {LOOP_STEPS.map((step, i) => (
            <article
              key={step.n}
              className="glow-card relative rounded-3xl border border-border bg-card/80 p-6 backdrop-blur animate-in fade-in slide-in-from-bottom-6 duration-700 fill-mode-both"
              style={{ animationDelay: `${480 + i * 120}ms` }}
            >
              <span className="absolute right-6 top-6 font-orbitron text-xs font-bold text-neon-pink/70">
                {step.n}
              </span>
              <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-neon-pink/40 bg-neon-pink/10 text-neon-pink shadow-[0_0_18px_-6px_#ff2e97]">
                <step.icon className="h-5 w-5" aria-hidden="true" />
              </div>
              <h2 className="mt-5 font-display text-2xl text-white">{step.title}</h2>
              <p className="mt-3 text-sm leading-6 text-muted-foreground">{step.description}</p>
            </article>
          ))}
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
                className="glow-card group flex flex-col rounded-3xl border border-dashed border-border bg-card/70 p-6"
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
          <div className="mt-8">
            <GeminiChat layout="sidebar" />
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
