"use client"

import { useEffect, useState } from "react"
import { ListChecks, Mic, StopCircle } from "lucide-react"
import { PageBackButton } from "@/components/page-back-button"
import { useAsyncAction } from "@/hooks/use-async-action"
import { useMicRecording } from "@/hooks/use-mic-recording"
import { demoSpeechFeedback } from "@/lib/speech-analyze"
import {
  fetchSpeechTopics,
  postSpeechEvaluation,
  type SpeechTopicHit,
} from "@/lib/speech-api"

export default function SpeechPage() {
  const { loading, error, success, run } = useAsyncAction()
  const mic = useMicRecording()
  const [topics, setTopics] = useState<SpeechTopicHit[]>([])
  const [topicId, setTopicId] = useState<string | null>(null)
  const [result, setResult] = useState<ReturnType<typeof demoSpeechFeedback> | null>(null)
  const [status, setStatus] = useState("고민 주제를 선택한 뒤 마이크로 말해 보세요.")

  useEffect(() => {
    fetchSpeechTopics()
      .then((data) => setTopics(data.hits))
      .catch(() => setStatus("스피치 주제를 불러오지 못했습니다."))
  }, [])

  const handleStart = async () => {
    if (!topicId) { setStatus("먼저 고민 주제를 선택해 주세요."); return }
    const ok = await mic.start()
    setStatus(ok ? "녹음 중입니다. 멈추기를 눌러 AI 피드백을 받으세요." : "마이크 권한이 필요합니다.")
  }

  const handleStop = () => {
    if (!topicId) return
    void mic.stop(async (sec) => {
      const analysis = demoSpeechFeedback(topicId, sec)
      setResult(analysis)
      setStatus("스피치 피드백을 Neon에 저장 중입니다.")
      await run(
        () =>
          postSpeechEvaluation({
            topicId,
            clarityScore: analysis.clarityScore,
            paceScore: analysis.paceScore,
            toneScore: analysis.toneScore,
            summary: analysis.summary,
            feedbackPoints: analysis.feedbackPoints,
            fileName: "speech-mic.webm",
            durationSec: sec,
          }),
        { successMessage: "스피치 피드백이 저장되었습니다." }
      )
    })
  }

  return (
    <main className="min-h-[calc(100vh-4rem)] bg-background px-4 py-8 text-foreground sm:px-6">
      <div className="mx-auto max-w-3xl">
        <PageBackButton />

        {/* HERO */}
        <section className="mt-6 animate-in fade-in slide-in-from-bottom-6 duration-700 fill-mode-both rounded-2xl border border-border bg-card px-6 py-8 shadow-[0_0_40px_rgba(255,46,151,0.1)]">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-neon-cyan/50 bg-neon-cyan/10 px-3 py-1 font-orbitron text-[11px] font-semibold tracking-[0.2em] text-neon-cyan">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-neon-pink" />
            SPEECH COACHING
          </span>
          <h1 className="mt-3 font-display text-3xl text-white sm:text-4xl">스피치 코칭</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            발표·면접·일상 대화 연습 후 AI 말하기 피드백을 받습니다.
          </p>
        </section>

        {/* 주제 선택 */}
        <section className="mt-6 grid gap-3 sm:grid-cols-2">
          {topics.map((topic) => {
            const active = topicId === topic.topic_id
            return (
              <button
                key={topic.topic_id}
                type="button"
                onClick={() => {
                  setTopicId(topic.topic_id)
                  mic.reset()
                  setResult(null)
                  setStatus(`「${topic.label}」 주제 선택됨.`)
                }}
                className={`rounded-xl border p-4 text-left text-sm transition-colors ${
                  active
                    ? "border-neon-pink bg-neon-pink/10 shadow-[0_0_20px_rgba(255,46,151,0.35)]"
                    : "glow-card border-border bg-card"
                }`}
              >
                <p className="font-semibold text-foreground">{topic.label}</p>
                <p className="mt-1 text-xs text-muted-foreground">
                  {topic.description}
                </p>
              </button>
            )
          })}
        </section>

        {/* 녹음 컨트롤 */}
        <section className="mt-6 rounded-2xl border border-border bg-night-900 p-5">
          <p className="mb-4 font-orbitron text-xs tracking-[0.25em] text-neon-cyan">마이크 녹음</p>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              disabled={loading || mic.recording === "recording"}
              onClick={handleStart}
              className="inline-flex items-center gap-2 rounded-full bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground glow-button transition-opacity hover:opacity-90 disabled:opacity-40"
            >
              <Mic className="h-4 w-4" aria-hidden />
              녹음 시작
            </button>
            <button
              type="button"
              disabled={mic.recording !== "recording" || loading}
              onClick={handleStop}
              className="inline-flex items-center gap-2 rounded-full border border-neon-cyan/60 px-5 py-3 text-sm font-medium text-neon-cyan transition-colors hover:bg-neon-cyan/10 disabled:opacity-40"
            >
              <StopCircle className="h-4 w-4" aria-hidden />
              멈추고 분석
            </button>
          </div>
          <p className="mt-4 text-sm font-mono text-muted-foreground" role="status">
            {error ?? success ?? status}
          </p>
        </section>

        {/* 결과 */}
        {result && (
          <section className="mt-6 animate-in fade-in slide-in-from-bottom-6 duration-700 fill-mode-both rounded-2xl border-2 border-neon-pink/40 bg-night-900 p-6 shadow-[0_0_32px_rgba(255,46,151,0.15)]">
            <div className="flex items-center gap-2 text-sm font-medium text-foreground">
              <ListChecks className="h-4 w-4 text-neon-pink" aria-hidden />
              AI 피드백
            </div>
            <div className="mt-5 grid grid-cols-3 gap-3 text-center">
              {[
                { label: "명확도", value: result.clarityScore },
                { label: "속도", value: result.paceScore },
                { label: "톤", value: result.toneScore },
              ].map(({ label, value }) => (
                <div key={label} className="rounded-xl border border-border bg-card p-4">
                  <p className="font-orbitron text-2xl font-semibold text-neon-cyan">{value}</p>
                  <p className="mt-1 text-xs text-muted-foreground">{label}</p>
                </div>
              ))}
            </div>
            <p className="mt-5 text-sm leading-7 text-foreground/90">{result.summary}</p>
            <ul className="mt-4 space-y-2">
              {result.feedbackPoints.map((point) => (
                <li key={point} className="flex items-start gap-2 text-sm text-muted-foreground">
                  <span className="text-neon-pink">›</span>
                  {point}
                </li>
              ))}
            </ul>
            <p className="mt-4 text-xs font-mono text-muted-foreground">{mic.durationSec}초 녹음 기준</p>
          </section>
        )}
      </div>
    </main>
  )
}
