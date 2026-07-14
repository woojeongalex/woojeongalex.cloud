"use client"

import Link from "next/link"
import { ArrowRight, AudioLines, Music4 } from "lucide-react"
import { GeminiChat } from "@/components/gemini-chat"
import { IuemGuideCarousel } from "@/components/iuem-guide-carousel"
import { WeeklyKingBanner } from "@/components/weekly-king-banner"

const feedbackSamples = [
  {
    n: "01",
    icon: AudioLines,
    title: "음정 정확도 분석",
    description:
      "구간별 피치 안정성을 추적해 흔들리는 음, 밀리는 음, 지나치게 높은 음을 잡아냅니다.",
  },
  {
    n: "02",
    icon: AudioLines,
    title: "박자 정밀도 분석",
    description:
      "원곡 BPM과 사용자의 발성을 비교해 박자가 빨라지는 구간과 늦어지는 구간을 알려줍니다.",
  },
  {
    n: "03",
    icon: AudioLines,
    title: "AI 코칭 피드백",
    description:
      "호흡, 발성, 강세, 프레이징을 함께 분석해 다음 연습 포인트를 자연어로 제안합니다.",
  },
]

export default function HomePage() {
  return (
    <main className="min-h-[calc(100vh-4rem)] min-w-0 overflow-x-hidden bg-background text-foreground">
      {/* HERO */}
      <section className="border-b border-border">
        <div className="mx-auto flex max-w-6xl flex-col gap-10 px-4 py-12 md:flex-row md:items-start md:justify-between md:py-16">
          {/* left */}
          <div className="max-w-[34rem]">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-muted px-3 py-1 text-[11px] font-semibold tracking-wide text-muted-foreground">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-foreground" />
              IUEM AI AGENT
            </span>
            <h1 className="mt-5 text-4xl font-semibold leading-[1.08] tracking-tight text-foreground sm:text-5xl md:text-6xl">
              노래를 고르고,
              <br />
              부르면서 AI로
              <br />
              음정과 박자를 분석하세요.
            </h1>
            <p className="mt-6 max-w-lg text-base leading-8 text-muted-foreground">
              사용자가 선택한 가요나 뮤지컬 넘버를 AI가 분석하고,
              내장 마이크로 부른 결과를 바탕으로 음정·박자 정확도,
              그리고 다음 연습을 위한 코칭 피드백까지 제공합니다.
            </p>

            <div className="mt-10 grid gap-4 sm:grid-cols-2">
              {/* vocal card */}
              <Link
                href="/analyze"
                className="group rounded-2xl border border-border bg-card p-5 transition-colors hover:border-foreground/40 hover:bg-muted/40"
              >
                <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-border bg-muted">
                  <AudioLines className="h-5 w-5 text-foreground" aria-hidden="true" />
                </div>
                <p className="mt-4 text-xs font-medium text-muted-foreground">보컬 배너</p>
                <h3 className="mt-1 text-2xl font-semibold text-foreground">가요 + 뮤지컬</h3>
                <p className="mt-3 text-sm leading-7 text-muted-foreground">
                  선택한 곡 기반으로 음정, 박자,
                  발성 안정성을 분석하고 AI 피드백을 받으세요.
                </p>
                <div className="mt-4 flex flex-wrap gap-2 text-xs text-muted-foreground">
                  {["K-Pop Analysis", "Musical Number", "Vocal Feedback"].map((t) => (
                    <span
                      key={t}
                      className="rounded-full border border-border bg-muted px-3 py-1"
                    >
                      {t}
                    </span>
                  ))}
                </div>
                <div className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-foreground">
                  보컬 상세 보기
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </div>
              </Link>

              {/* instrument card */}
              <Link
                href="/instrument"
                className="group rounded-2xl border border-border bg-card p-5 transition-colors hover:border-foreground/40 hover:bg-muted/40"
              >
                <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-border bg-muted">
                  <Music4 className="h-5 w-5 text-foreground" aria-hidden="true" />
                </div>
                <p className="mt-4 text-xs font-medium text-muted-foreground">악기 배너</p>
                <h3 className="mt-1 text-2xl font-semibold text-foreground">기타 + 피아노</h3>
                <p className="mt-3 text-sm leading-7 text-muted-foreground">
                  기타와 피아노의 음정 상태와 튜닝 정확도를 확인하고
                  점수를 받아보세요.
                </p>
                <div className="mt-4 flex flex-wrap gap-2 text-xs text-muted-foreground">
                  {["Guitar Tuning", "Piano Pitch Check", "Instrument Support"].map((t) => (
                    <span
                      key={t}
                      className="rounded-full border border-border bg-muted px-3 py-1"
                    >
                      {t}
                    </span>
                  ))}
                </div>
                <div className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-foreground">
                  악기 상세 보기
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </div>
              </Link>
            </div>
          </div>

          {/* right — chat */}
          <div className="mt-8 w-full max-w-xl md:mt-4 md:sticky md:top-32">
            <GeminiChat layout="sidebar" />
          </div>
        </div>
      </section>

      {/* WEEKLY + GUIDE */}
      <section className="border-b border-border">
        <div className="mx-auto max-w-6xl px-4 py-8 md:py-10">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-5 md:items-start">
            <WeeklyKingBanner />
            <IuemGuideCarousel />
          </div>
        </div>
      </section>

      {/* AI FEEDBACK CARDS */}
      <section className="border-b border-border bg-muted/30">
        <div className="mx-auto max-w-6xl px-4 py-14">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div className="max-w-2xl">
              <p className="text-sm font-medium text-muted-foreground">AI가 제공할 분석</p>
              <h2 className="mt-2 text-3xl font-semibold tracking-tight text-foreground">
                단순 점수만이 아니라, 왜 흔들렸는지까지 설명하는 보컬 피드백
              </h2>
            </div>
            <div className="rounded-full border border-border px-4 py-2 text-sm font-mono text-muted-foreground">
              백엔드 연동 예정 기능
            </div>
          </div>

          <div className="mt-8 grid gap-5 md:grid-cols-3">
            {feedbackSamples.map((item) => (
              <article
                key={item.title}
                className="relative rounded-3xl border border-border bg-card p-6"
              >
                <span className="absolute right-6 top-6 font-mono text-xs text-muted-foreground/50">
                  {item.n}
                </span>
                <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-border bg-muted">
                  <item.icon className="h-5 w-5 text-foreground" aria-hidden="true" />
                </div>
                <h3 className="mt-5 text-xl font-semibold text-foreground">{item.title}</h3>
                <p className="mt-3 text-sm leading-6 text-muted-foreground">
                  {item.description}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-6xl px-4 py-14">
        <div className="rounded-[2rem] border-2 border-foreground/15 bg-secondary px-6 py-10 sm:px-10">
          <p className="text-xs font-mono tracking-widest uppercase text-muted-foreground">
            // 다음 단계
          </p>
          <div className="mt-3 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <h2 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
                선택한 노래, 사용자 음성, 분석 결과가 하나의 경험으로 이어지는 홈 화면
              </h2>
              <p className="mt-4 text-sm leading-7 text-muted-foreground sm:text-base">
                추후 백엔드가 연결되면 가요와 뮤지컬 넘버를 아우르는 곡 선택 API, 마이크 입력
                업로드, 음정/박자 정확도 분석, 그리고 자연어 피드백 결과를 이 홈 화면에서 바로
                보여줄 수 있도록 설계했습니다.
              </p>
            </div>
            <Link
              href="/analyze"
              className="inline-flex items-center justify-center gap-2 rounded-full bg-primary px-6 py-3.5 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-80"
            >
              기능 시나리오 확인
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Link>
          </div>
        </div>
      </section>
    </main>
  )
}
