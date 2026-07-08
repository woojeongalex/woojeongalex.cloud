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
      { step: "4", title: "AI 코칭", icon: ListChecks },
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
              ? "border-zinc-600 bg-zinc-900 text-white"
              : "border-zinc-300 bg-white text-zinc-950"
            : isWhiteKey
              ? "border-zinc-300 bg-white text-zinc-950"
              : "border-zinc-600 bg-zinc-900 text-white"
        )}
      >
        <div
          className={cn(
            "flex h-12 w-12 items-center justify-center rounded-xl border sm:h-14 sm:w-14",
            isWhiteKey ? "border-zinc-200 bg-zinc-50" : "border-zinc-500 bg-zinc-800"
          )}
          aria-hidden
        >
          <div className="flex items-center gap-1">
            <StepIcon
              className={cn(
                SecondaryIcon ? "h-5 w-5 sm:h-6 sm:w-6" : "h-6 w-6 sm:h-7 sm:w-7",
                isWhiteKey ? "text-zinc-900" : "text-white"
              )}
              strokeWidth={1.75}
            />
            {SecondaryIcon ? (
              <SecondaryIcon
                className={cn(
                  "h-5 w-5 sm:h-6 sm:w-6",
                  isWhiteKey ? "text-zinc-700" : "text-zinc-300"
                )}
                strokeWidth={1.75}
              />
            ) : null}
          </div>
        </div>
        <span
          className={cn(
            "mt-3 text-[10px] font-bold tracking-wider",
            isWhiteKey ? "text-zinc-500" : "text-zinc-400"
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
          className="hidden h-4 w-4 shrink-0 text-zinc-600 sm:block"
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
      className="relative flex h-full w-full flex-col rounded-3xl border border-zinc-200 bg-zinc-950 px-6 py-7 text-white shadow-[0_20px_60px_rgba(0,0,0,0.12)] sm:px-7 sm:py-8"
      aria-roledescription="carousel"
      aria-label="이음 사용 설명서"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 items-center gap-2">
          <BookOpen className="h-5 w-5 shrink-0 text-white" aria-hidden />
          <p className="text-sm font-bold tracking-wide text-white sm:text-base">
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
                  i === index ? "bg-white" : "bg-zinc-600"
                )}
              />
            ))}
          </div>
          <button
            type="button"
            onClick={() => goTo(index - 1)}
            className="rounded-lg border border-zinc-700 p-1.5 text-zinc-400 hover:border-zinc-500 hover:text-white"
            aria-label="이전 설명"
          >
            <ChevronLeft className="h-4 w-4" aria-hidden />
          </button>
          <button
            type="button"
            onClick={() => goTo(index + 1)}
            className="rounded-lg border border-zinc-700 p-1.5 text-zinc-400 hover:border-zinc-500 hover:text-white"
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
                  ? "border-zinc-300 bg-white text-zinc-900"
                  : "border-zinc-600 bg-zinc-900 text-zinc-200"
              )}
            >
              {slide.badge}
            </span>
            <h2 className="mt-3 text-2xl font-semibold leading-tight sm:text-[1.65rem]">
              {slide.title}
            </h2>
            <p className="mt-2 text-sm leading-6 text-zinc-400">{slide.intro}</p>
          </div>
          <div
            className={cn(
              "flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border sm:h-14 sm:w-14",
              accentWhite ? "border-white bg-white text-zinc-950" : "border-zinc-600 bg-zinc-800"
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
