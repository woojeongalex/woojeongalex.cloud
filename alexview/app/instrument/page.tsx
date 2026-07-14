"use client"

import { useEffect, useState } from "react"
import { Guitar, Mic, Piano, StopCircle, Wrench } from "lucide-react"
import { PageBackButton } from "@/components/page-back-button"
import { useAsyncAction } from "@/hooks/use-async-action"
import { useMicRecording } from "@/hooks/use-mic-recording"
import { demoInstrumentTuning } from "@/lib/instrument-analyze"
import {
  fetchInstrumentCatalog,
  postInstrumentEvaluation,
  type InstrumentCatalogHit,
} from "@/lib/instrument-api"

export default function InstrumentPage() {
  const { loading, error, success, run } = useAsyncAction()
  const mic = useMicRecording()
  const [catalog, setCatalog] = useState<InstrumentCatalogHit[]>([])
  const [selectedId, setSelectedId] = useState<"guitar" | "piano" | null>(null)
  const [result, setResult] = useState<ReturnType<typeof demoInstrumentTuning> | null>(null)
  const [status, setStatus] = useState("악기를 선택한 뒤 마이크로 연주를 녹음해 주세요.")

  useEffect(() => {
    fetchInstrumentCatalog()
      .then((data) => setCatalog(data.hits))
      .catch(() => setStatus("악기 목록을 불러오지 못했습니다."))
  }, [])

  const handleStart = async () => {
    if (!selectedId) { setStatus("기타 또는 피아노를 먼저 선택해 주세요."); return }
    const ok = await mic.start()
    setStatus(ok ? "연주 중입니다. 멈추기를 눌러 분석하세요." : "마이크 권한이 필요합니다.")
  }

  const handleStop = () => {
    if (!selectedId) return
    void mic.stop(async (sec) => {
      const analysis = demoInstrumentTuning(selectedId, sec)
      setResult(analysis)
      setStatus("튜닝 결과를 Neon에 저장 중입니다.")
      await run(
        () =>
          postInstrumentEvaluation({
            instrumentId: selectedId,
            tuningAccuracy: analysis.tuningAccuracy,
            pitchDeviationCents: analysis.pitchDeviationCents,
            summary: analysis.summary,
            stringReadings: analysis.stringReadings,
            fileName: `${selectedId}-mic.webm`,
            durationSec: sec,
          }),
        { successMessage: "튜닝 결과가 저장되었습니다." }
      )
    })
  }

  return (
    <main className="min-h-[calc(100vh-4rem)] bg-background px-4 py-8 text-foreground sm:px-6">
      <div className="mx-auto max-w-3xl">
        <PageBackButton />

        {/* HERO */}
        <section className="mt-6 rounded-2xl border border-border bg-card px-6 py-8">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-muted px-3 py-1 text-[11px] font-semibold tracking-wide text-muted-foreground">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-foreground" />
            INSTRUMENT TUNING
          </span>
          <h1 className="mt-3 text-3xl font-semibold text-foreground">악기 튜닝</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            기타·피아노 연주를 녹음하고 튜닝·음정 피드백을 받습니다.
          </p>
        </section>

        {/* 악기 선택 */}
        <section className="mt-6 grid gap-3 sm:grid-cols-2">
          {catalog.map((item) => {
            const active = selectedId === item.instrument_id
            const Icon = item.instrument_id === "guitar" ? Guitar : Piano
            return (
              <button
                key={item.instrument_id}
                type="button"
                onClick={() => {
                  setSelectedId(item.instrument_id as "guitar" | "piano")
                  mic.reset()
                  setResult(null)
                  setStatus(`${item.label} 선택됨. 마이크 녹음을 시작하세요.`)
                }}
                className={`rounded-2xl border p-5 text-left transition-colors ${
                  active
                    ? "border-foreground bg-muted"
                    : "border-border bg-secondary hover:border-foreground/40"
                }`}
              >
                <div
                  className={`mb-3 flex h-11 w-11 items-center justify-center rounded-xl border ${
                    active ? "border-foreground/30 bg-background" : "border-border bg-background"
                  }`}
                >
                  <Icon
                    className={`h-5 w-5 ${active ? "text-foreground" : "text-muted-foreground"}`}
                    aria-hidden
                  />
                </div>
                <p className="font-semibold text-foreground">{item.label}</p>
                <p className="mt-1 text-xs text-muted-foreground">{item.standard_tuning}</p>
              </button>
            )
          })}
        </section>

        {/* 녹음 컨트롤 */}
        <section className="mt-6 rounded-2xl border border-border bg-secondary p-5">
          <p className="mb-4 text-sm font-medium text-foreground">마이크 녹음</p>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              disabled={loading || mic.recording === "recording"}
              onClick={handleStart}
              className="inline-flex items-center gap-2 rounded-full bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-80 disabled:opacity-40"
            >
              <Mic className="h-4 w-4" aria-hidden />
              녹음 시작
            </button>
            <button
              type="button"
              disabled={mic.recording !== "recording" || loading}
              onClick={handleStop}
              className="inline-flex items-center gap-2 rounded-full border border-border px-5 py-3 text-sm font-medium text-muted-foreground transition-colors disabled:opacity-40"
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
          <section className="mt-6 rounded-2xl border-2 border-foreground/15 bg-secondary p-6">
            <div className="flex items-center gap-2 text-sm font-medium text-foreground">
              <Wrench className="h-4 w-4" aria-hidden />
              튜닝 결과
            </div>
            <p className="mt-4 text-4xl font-semibold text-foreground">{result.tuningAccuracy}%</p>
            <p className="mt-1 text-sm text-muted-foreground">
              평균 편차 약 {result.pitchDeviationCents} cents · {mic.durationSec}초 녹음
            </p>
            <p className="mt-4 text-sm leading-7 text-foreground/90">{result.summary}</p>
            <ul className="mt-4 space-y-2">
              {result.stringReadings.map((row) => (
                <li key={row.label} className="flex justify-between text-sm font-mono">
                  <span className="text-muted-foreground">{row.label}</span>
                  <span className="font-medium text-foreground">{row.cents} cents</span>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </main>
  )
}
