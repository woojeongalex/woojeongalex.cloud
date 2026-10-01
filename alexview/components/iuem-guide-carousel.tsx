"use client"

import { useCallback, useEffect, useState } from "react"
import type { LucideIcon } from "lucide-react"
import {
  AudioLines,
  BarChart3,
  BookOpen,
  Brain,
  ChevronLeft,
  ChevronRight,
  FileVideo,
  Guitar,
  Home,
  ListChecks,
  Mic,
  Mic2,
  Music2,
  Music4,
  Piano,
  Radio,
  Search,
  Sparkles,
  Wrench,
} from "lucide-react"
import { cn } from "@/lib/utils"

const SLIDE_MS = 10_000

type GuideSlideId = "vocal" | "instrument" | "speech"

type GuideStep = {
  step: string
  title: string
  icon: LucideIcon
  secondaryIcon?: LucideIcon
}

type GuideSlide = {
  id: GuideSlideId
  badge: string
  title: string
  intro: string
  icon: LucideIcon
  steps: GuideStep[]
}

const GUIDE_SLIDES: GuideSlide[] = [
  {
    id: "vocal",
    badge: "보컬 분석",
    title: "가요·뮤지컬 보컬 분석",
    intro: "MR 선택 → 녹음·영상 → AI 피드백까지 4단계",
    icon: AudioLines,
    steps: [
      { step: "1", title: "분석 화면", icon: Home },
      { step: "2", title: "MR 선택", icon: Search },
      { step: "3", title: "녹음·영상", icon: Mic, secondaryIcon: FileVideo },
      { step: "4", title: "AI 결과", icon: Sparkles },
    ],
  },
  {
    id: "instrument",
    badge: "악기 분석",
    title: "기타 · 피아노",
    intro: "악기 선택 → 연주 입력 → 튜닝·음정 확인",
    icon: Music4,
    steps: [
      { step: "1", title: "악기 화면", icon: Music2 },
      { step: "2", title: "기타·피아노", icon: Guitar, secondaryIcon: Piano },
      { step: "3", title: "튜닝 측정", icon: Wrench },
      { step: "4", title: "연습 가이드", icon: BarChart3 },
    ],
  },
  {
    id: "speech",
    badge: "스피치",
    title: "발표·대화 스피치 코칭",
    intro: "고민 선택 → 마이크 녹음 → AI 말하기 피드백",
    icon: Mic2,
    steps: [
      { step: "1", title: "MENU·스피치", icon: Radio },
      { step: "2", title: "고민 선택", icon: Brain },
      { step: "3", title: "마이크 녹음", icon: Mic },
      { step: "4", title: "발성 코칭", icon: ListChecks },
    ],
  },
]

function GuideStepCard({
  item,
  slideId,
  showArrow,
}: {
  item: GuideStep
  slideId: GuideSlideId
  showArrow: boolean
}) {
  const StepIcon = item.icon
  const SecondaryIcon = item.secondaryIcon
  const isWhiteKey = Number(item.step) % 2 === 1

  return (
    <li className="flex min-w-0 flex-1 items-center gap-1">
      <div
        className={cn(
          "flex w-full flex-col items-center rounded-2xl border px-2 py-4 sm:px-3 sm:py-5",
          slideId === "instrument"
            ? isWhiteKey
              ? "border-neon-cyan/50 bg-night-900 text-white"
              : "border-neon-pink/50 bg-night-800 text-white"
            : isWhiteKey
              ? "border-neon-pink/50 bg-night-800 text-white"
              : "border-neon-cyan/50 bg-night-900 text-white"
        )}
      >
        <div
          className={cn(
            "flex h-12 w-12 items-center justify-center rounded-xl border sm:h-14 sm:w-14",
            isWhiteKey ? "border-neon-pink/40 bg-neon-pink/10" : "border-neon-cyan/40 bg-neon-cyan/10"
          )}
          aria-hidden
        >
          <div className="flex items-center gap-1">
            <StepIcon
              className={cn(
                SecondaryIcon ? "h-5 w-5 sm:h-6 sm:w-6" : "h-6 w-6 sm:h-7 sm:w-7",
                isWhiteKey ? "text-neon-pink" : "text-neon-cyan"
              )}
              strokeWidth={1.75}
            />
            {SecondaryIcon ? (
              <SecondaryIcon
                className={cn(
                  "h-5 w-5 sm:h-6 sm:w-6",
                  isWhiteKey ? "text-neon-violet" : "text-neon-yellow"
                )}
                strokeWidth={1.75}
              />
            ) : null}
          </div>
        </div>
        <span
          className={cn(
            "mt-3 font-orbitron text-[10px] font-bold tracking-[0.2em]",
            isWhiteKey ? "text-neon-pink" : "text-neon-cyan"
          )}
        >
          STEP {item.step}
        </span>
        <p className="mt-1 text-center text-xs font-semibold leading-tight sm:text-sm">
          {item.title}
        </p>
      </div>
      {showArrow && (
        <ChevronRight
          className="hidden h-4 w-4 shrink-0 text-neon-violet sm:block"
          aria-hidden
        />
      )}
    </li>
  )
}

function headerBadgeWhite(slideId: GuideSlideId): boolean {
  return slideId === "vocal" || slideId === "speech"
}

export function IuemGuideCarousel() {
  const [index, setIndex] = useState(0)

  const slide = GUIDE_SLIDES[index]
  const Icon = slide.icon

  const goTo = useCallback((next: number) => {
    setIndex((next + GUIDE_SLIDES.length) % GUIDE_SLIDES.length)
  }, [])

  useEffect(() => {
    const timer = window.setInterval(() => {
      setIndex((i) => (i + 1) % GUIDE_SLIDES.length)
    }, SLIDE_MS)
    return () => window.clearInterval(timer)
  }, [])

  const accentWhite = headerBadgeWhite(slide.id)

  return (
    <div
      className="relative flex h-full w-full flex-col rounded-3xl border border-border bg-night-950 px-6 py-7 text-white shadow-[0_0_40px_rgba(46,230,255,0.12)] sm:px-7 sm:py-8"
      aria-roledescription="carousel"
      aria-label="이음 사용 설명서"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 items-center gap-2">
          <BookOpen className="h-5 w-5 shrink-0 text-neon-cyan" aria-hidden />
          <p className="font-display text-base text-white sm:text-lg">
            이음 사용 설명서
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <div className="flex gap-1" aria-hidden>
            {GUIDE_SLIDES.map((s, i) => (
              <span
                key={s.id}
                className={cn(
                  "h-1.5 w-1.5 rounded-full transition-colors",
                  i === index ? "bg-neon-pink shadow-[0_0_8px_rgba(255,46,151,0.8)]" : "bg-night-600"
                )}
              />
            ))}
          </div>
          <button
            type="button"
            onClick={() => goTo(index - 1)}
            className="rounded-lg border border-neon-cyan/60 p-1.5 text-neon-cyan hover:bg-neon-cyan/10"
            aria-label="이전 설명"
          >
            <ChevronLeft className="h-4 w-4" aria-hidden />
          </button>
          <button
            type="button"
            onClick={() => goTo(index + 1)}
            className="rounded-lg border border-neon-cyan/60 p-1.5 text-neon-cyan hover:bg-neon-cyan/10"
            aria-label="다음 설명"
          >
            <ChevronRight className="h-4 w-4" aria-hidden />
          </button>
        </div>
      </div>

      <div
        key={slide.id}
        className="mt-5 animate-in fade-in duration-500"
        aria-live="polite"
      >
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <span
              className={cn(
                "inline-block rounded-full border px-2.5 py-0.5 text-[11px] font-semibold",
                accentWhite
                  ? "border-neon-pink/60 bg-neon-pink/15 text-neon-pink"
                  : "border-neon-cyan/60 bg-neon-cyan/10 text-neon-cyan"
              )}
            >
              {slide.badge}
            </span>
            <h2 className="mt-3 font-display text-2xl leading-tight text-white sm:text-[1.65rem]">
              {slide.title}
            </h2>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">{slide.intro}</p>
          </div>
          <div
            className={cn(
              "flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border sm:h-14 sm:w-14",
              accentWhite ? "border-neon-pink/60 bg-neon-pink/15 text-neon-pink" : "border-neon-cyan/60 bg-neon-cyan/10 text-neon-cyan"
            )}
          >
            <Icon className="h-6 w-6 sm:h-7 sm:w-7" aria-hidden />
          </div>
        </div>

        <ol className="mt-6 flex list-none flex-col gap-0 sm:mt-7 sm:flex-row sm:items-stretch">
          {slide.steps.map((item, i) => (
            <GuideStepCard
              key={item.step}
              item={item}
              slideId={slide.id}
              showArrow={i < slide.steps.length - 1}
            />
          ))}
        </ol>
      </div>

      <div className="sr-only">
        {GUIDE_SLIDES.map((s, i) => (
          <button
            key={s.id}
            type="button"
            tabIndex={-1}
            onClick={() => goTo(i)}
            aria-current={i === index ? "true" : undefined}
          >
            {s.badge}
          </button>
        ))}
      </div>
    </div>
  )
}
