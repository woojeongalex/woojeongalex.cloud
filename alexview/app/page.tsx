"use client"

import { useEffect, useRef, useState } from "react"
import Link from "next/link"
import { ArrowRight, AudioLines, Music4, Circle } from "lucide-react"
import { GeminiChat } from "@/components/gemini-chat"
import { IuemGuideCarousel } from "@/components/iuem-guide-carousel"
import { WeeklyKingBanner } from "@/components/weekly-king-banner"

const LOG_LINES = [
  { time: "00:00:01", level: "INFO", msg: "IUEM AI Engine initializing..." },
  { time: "00:00:02", level: "INFO", msg: "FastAPI backend connection established" },
  { time: "00:00:03", level: "OK",   msg: "Vocal analysis model loaded — pitch detector v2.1" },
  { time: "00:00:04", level: "OK",   msg: "Rhythm model ready — BPM comparator active" },
  { time: "00:00:05", level: "INFO", msg: "Instrument tuning module standby" },
  { time: "00:00:06", level: "OK",   msg: "Speech coaching pipeline connected" },
  { time: "00:00:07", level: "INFO", msg: "Awaiting user audio input..." },
  { time: "00:00:08", level: "INFO", msg: "Gemini AI coach on standby" },
  { time: "00:00:09", level: "OK",   msg: "All systems nominal — ready to analyze" },
  { time: "00:00:10", level: "INFO", msg: "Session active. Select a song to begin." },
]

const ACCENT = "#00FF88"

function TerminalWidget() {
  const [visibleCount, setVisibleCount] = useState(0)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (visibleCount >= LOG_LINES.length) return
    const t = setTimeout(() => setVisibleCount((c) => c + 1), 420)
    return () => clearTimeout(t)
  }, [visibleCount])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [visibleCount])

  return (
    <div
      className="w-full rounded-2xl border overflow-hidden"
      style={{ borderColor: "#1f1f1f", background: "#0d0d0d" }}
    >
      {/* title bar */}
      <div
        className="flex items-center gap-2 px-4 py-3 border-b"
        style={{ borderColor: "#1f1f1f", background: "#111111" }}
      >
        <span className="h-3 w-3 rounded-full bg-red-500/70" />
        <span className="h-3 w-3 rounded-full bg-yellow-500/70" />
        <span className="h-3 w-3 rounded-full bg-green-500/70" />
        <span className="ml-3 text-xs font-mono" style={{ color: "#555" }}>
          iuem-agent — AI status monitor
        </span>
        <Circle
          className="ml-auto h-2 w-2 animate-pulse"
          fill={ACCENT}
          style={{ color: ACCENT }}
        />
      </div>

      {/* log body */}
      <div className="h-56 overflow-y-auto px-4 py-3 font-mono text-xs leading-6">
        {LOG_LINES.slice(0, visibleCount).map((line, i) => (
          <div key={i} className="flex gap-3">
            <span style={{ color: "#444" }}>{line.time}</span>
            <span
              style={{
                color: line.level === "OK" ? ACCENT : line.level === "INFO" ? "#6b7280" : "#f87171",
                minWidth: "2.5rem",
              }}
            >
              [{line.level}]
            </span>
            <span style={{ color: "#d1d5db" }}>{line.msg}</span>
          </div>
        ))}
        {visibleCount < LOG_LINES.length && (
          <span className="animate-pulse" style={{ color: ACCENT }}>
            ▋
          </span>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}

const feedbackSamples = [
  {
    title: "음정 정확도 분석",
    description:
      "구간별 피치 안정성을 추적해 흔들리는 음, 밀리는 음, 지나치게 높은 음을 잡아냅니다.",
  },
  {
    title: "박자 정밀도 분석",
    description:
      "원곡 BPM과 사용자의 발성을 비교해 박자가 빨라지는 구간과 늦어지는 구간을 알려줍니다.",
  },
  {
    title: "AI 코칭 피드백",
    description:
      "호흡, 발성, 강세, 프레이징을 함께 분석해 다음 연습 포인트를 자연어로 제안합니다.",
  },
]

export default function HomePage() {
  return (
    <main
      className="min-h-[calc(100vh-4rem)] min-w-0 overflow-x-hidden"
      style={{ background: "#0A0A0A", color: "#e5e7eb" }}
    >
      {/* HERO */}
      <section className="border-b" style={{ borderColor: "#1a1a1a" }}>
        <div className="mx-auto flex max-w-6xl flex-col gap-10 px-4 py-12 md:flex-row md:items-start md:justify-between md:py-16">
          {/* left */}
          <div className="max-w-[34rem]">
            <p className="mb-4 text-xs font-mono tracking-widest uppercase" style={{ color: ACCENT }}>
              // IUEM AI Agent
            </p>
            <h1 className="text-4xl font-semibold leading-[1.08] tracking-tight text-white sm:text-5xl md:text-6xl">
              노래를 고르고,
              <br />
              부르면서 AI로
              <br />
              음정과 박자를 분석하세요.
            </h1>
            <p className="mt-6 max-w-lg text-base leading-8" style={{ color: "#9ca3af" }}>
              사용자가 선택한 가요나 뮤지컬 넘버를 AI가 분석하고,
              내장 마이크로 부른 결과를 바탕으로 음정·박자 정확도,
              그리고 다음 연습을 위한 코칭 피드백까지 제공합니다.
            </p>

            <div className="mt-10 grid gap-4 sm:grid-cols-2">
              {/* vocal card */}
              <Link
                href="/analyze"
                className="group rounded-2xl border p-5 transition-colors"
                style={{ borderColor: "#1f1f1f", background: "#111111" }}
                onMouseEnter={(e) => {
                  ;(e.currentTarget as HTMLElement).style.borderColor = ACCENT + "55"
                }}
                onMouseLeave={(e) => {
                  ;(e.currentTarget as HTMLElement).style.borderColor = "#1f1f1f"
                }}
              >
                <div className="flex items-center gap-2 text-sm font-medium" style={{ color: "#6b7280" }}>
                  <AudioLines className="h-4 w-4" aria-hidden="true" />
                  보컬 배너
                </div>
                <h3 className="mt-3 text-2xl font-semibold text-white">가요 + 뮤지컬</h3>
                <p className="mt-3 text-sm leading-7" style={{ color: "#9ca3af" }}>
                  선택한 곡 기반으로 음정, 박자,
                  발성 안정성을 분석하고 AI 피드백을 받으세요.
                </p>
                <div className="mt-4 flex flex-wrap gap-2 text-xs" style={{ color: "#6b7280" }}>
                  {["K-Pop Analysis", "Musical Number", "Vocal Feedback"].map((t) => (
                    <span
                      key={t}
                      className="rounded-full border px-3 py-1"
                      style={{ borderColor: "#2a2a2a", background: "#0d0d0d" }}
                    >
                      {t}
                    </span>
                  ))}
                </div>
                <div
                  className="mt-5 inline-flex items-center gap-2 text-sm font-medium"
                  style={{ color: ACCENT }}
                >
                  보컬 상세 보기
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </div>
              </Link>

              {/* instrument card */}
              <Link
                href="/instrument"
                className="group rounded-2xl border p-5 transition-colors"
                style={{ borderColor: "#1f1f1f", background: "#111111" }}
                onMouseEnter={(e) => {
                  ;(e.currentTarget as HTMLElement).style.borderColor = "#ffffff22"
                }}
                onMouseLeave={(e) => {
                  ;(e.currentTarget as HTMLElement).style.borderColor = "#1f1f1f"
                }}
              >
                <div className="flex items-center gap-2 text-sm font-medium" style={{ color: "#6b7280" }}>
                  <Music4 className="h-4 w-4" aria-hidden="true" />
                  악기 배너
                </div>
                <h3 className="mt-3 text-2xl font-semibold text-white">기타 + 피아노</h3>
                <p className="mt-3 text-sm leading-7" style={{ color: "#9ca3af" }}>
                  기타와 피아노의 음정 상태와 튜닝 정확도를 확인하고
                  점수를 받아보세요.
                </p>
                <div className="mt-4 flex flex-wrap gap-2 text-xs" style={{ color: "#6b7280" }}>
                  {["Guitar Tuning", "Piano Pitch Check", "Instrument Support"].map((t) => (
                    <span
                      key={t}
                      className="rounded-full border px-3 py-1"
                      style={{ borderColor: "#2a2a2a", background: "#0d0d0d" }}
                    >
                      {t}
                    </span>
                  ))}
                </div>
                <div className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-white">
                  악기 상세 보기
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </div>
              </Link>
            </div>
          </div>

          {/* right — terminal + chat */}
          <div className="mt-8 w-full max-w-xl space-y-4 md:mt-4 md:sticky md:top-32">
            <TerminalWidget />
            <GeminiChat layout="sidebar" />
          </div>
        </div>
      </section>

      {/* WEEKLY + GUIDE */}
      <section className="border-b" style={{ borderColor: "#1a1a1a" }}>
        <div className="mx-auto max-w-6xl px-4 py-8 md:py-10">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 md:gap-5 md:items-start">
            <WeeklyKingBanner />
            <IuemGuideCarousel />
          </div>
        </div>
      </section>

      {/* AI FEEDBACK CARDS */}
      <section className="border-b" style={{ borderColor: "#1a1a1a", background: "#0d0d0d" }}>
        <div className="mx-auto max-w-6xl px-4 py-14">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div className="max-w-2xl">
              <p className="text-sm font-medium" style={{ color: "#6b7280" }}>AI가 제공할 분석</p>
              <h2 className="mt-2 text-3xl font-semibold tracking-tight text-white">
                단순 점수만이 아니라, 왜 흔들렸는지까지 설명하는 보컬 피드백
              </h2>
            </div>
            <div
              className="rounded-full border px-4 py-2 text-sm font-mono"
              style={{ borderColor: "#1f1f1f", color: ACCENT }}
            >
              백엔드 연동 예정 기능
            </div>
          </div>

          <div className="mt-8 grid gap-5 md:grid-cols-3">
            {feedbackSamples.map((item) => (
              <article
                key={item.title}
                className="rounded-3xl border p-6"
                style={{ borderColor: "#1f1f1f", background: "#111111" }}
              >
                <AudioLines className="h-5 w-5" style={{ color: ACCENT }} aria-hidden="true" />
                <h3 className="mt-5 text-xl font-semibold text-white">{item.title}</h3>
                <p className="mt-3 text-sm leading-6" style={{ color: "#9ca3af" }}>
                  {item.description}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-6xl px-4 py-14">
        <div
          className="rounded-[2rem] border px-6 py-10 sm:px-10"
          style={{ borderColor: ACCENT + "33", background: "#0d1a12" }}
        >
          <p className="text-xs font-mono tracking-widest uppercase" style={{ color: ACCENT }}>
            // 다음 단계
          </p>
          <div className="mt-3 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="max-w-3xl">
              <h2 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">
                선택한 노래, 사용자 음성, 분석 결과가 하나의 경험으로 이어지는 홈 화면
              </h2>
              <p className="mt-4 text-sm leading-7 sm:text-base" style={{ color: "#9ca3af" }}>
                추후 백엔드가 연결되면 가요와 뮤지컬 넘버를 아우르는 곡 선택 API, 마이크 입력
                업로드, 음정/박자 정확도 분석, 그리고 자연어 피드백 결과를 이 홈 화면에서 바로
                보여줄 수 있도록 설계했습니다.
              </p>
            </div>
            <Link
              href="/analyze"
              className="inline-flex items-center justify-center gap-2 rounded-xl px-5 py-3 text-sm font-medium transition-opacity hover:opacity-80"
              style={{ background: ACCENT, color: "#0A0A0A" }}
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
