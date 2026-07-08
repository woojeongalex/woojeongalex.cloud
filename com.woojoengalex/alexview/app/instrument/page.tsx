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

const ACCENT = "#00FF88"

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
    <main
      className="min-h-[calc(100vh-4rem)] px-4 py-8 sm:px-6"
      style={{ background: "#0A0A0A", color: "#e5e7eb" }}
    >
      <div className="mx-auto max-w-3xl">
        <PageBackButton />

        {/* HERO */}
        <section className="mt-6 rounded-2xl border px-6 py-8" style={{ borderColor: "#1f1f1f", background: "#0d0d0d" }}>
          <p className="text-xs font-mono tracking-widest uppercase" style={{ color: ACCENT }}>
            // Instrument Tuning
          </p>
          <h1 className="mt-3 text-3xl font-semibold text-white">악기 튜닝</h1>
          <p className="mt-2 text-sm" style={{ color: "#9ca3af" }}>
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
                className="rounded-2xl border p-5 text-left transition-colors"
                style={{
                  borderColor: active ? ACCENT + "88" : "#1f1f1f",
                  background: active ? "#0d1a12" : "#111111",
                }}
              >
                <Icon className="mb-3 h-6 w-6" style={{ color: active ? ACCENT : "#9ca3af" }} aria-hidden />
                <p className="font-semibold text-white">{item.label}</p>
                <p className="mt-1 text-xs" style={{ color: "#6b7280" }}>{item.standard_tuning}</p>
              </button>
            )
          })}
        </section>

        {/* 녹음 컨트롤 */}
        <section className="mt-6 rounded-2xl border p-5" style={{ borderColor: "#1f1f1f", background: "#111111" }}>
          <p className="mb-4 text-sm font-medium text-white">마이크 녹음</p>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              disabled={loading || mic.recording === "recording"}
              onClick={handleStart}
              className="inline-flex items-center gap-2 rounded-xl px-5 py-3 text-sm font-medium transition-opacity hover:opacity-80 disabled:opacity-40"
              style={{ background: ACCENT, color: "#0A0A0A" }}
            >
              <Mic className="h-4 w-4" aria-hidden />
              녹음 시작
            </button>
            <button
              type="button"
              disabled={mic.recording !== "recording" || loading}
              onClick={handleStop}
              className="inline-flex items-center gap-2 rounded-xl border px-5 py-3 text-sm font-medium transition-colors disabled:opacity-40"
              style={{ borderColor: "#2a2a2a", color: "#9ca3af" }}
            >
              <StopCircle className="h-4 w-4" aria-hidden />
              멈추고 분석
            </button>
          </div>
          <p className="mt-4 text-sm font-mono" style={{ color: "#9ca3af" }} role="status">
            {error ?? success ?? status}
          </p>
        </section>

        {/* 결과 */}
        {result && (
          <section className="mt-6 rounded-2xl border p-6" style={{ borderColor: ACCENT + "33", background: "#0d1a12" }}>
            <div className="flex items-center gap-2 text-sm font-medium" style={{ color: ACCENT }}>
              <Wrench className="h-4 w-4" aria-hidden />
              튜닝 결과
            </div>
            <p className="mt-4 text-4xl font-semibold text-white">{result.tuningAccuracy}%</p>
            <p className="mt-1 text-sm" style={{ color: "#9ca3af" }}>
              평균 편차 약 {result.pitchDeviationCents} cents · {mic.durationSec}초 녹음
            </p>
            <p className="mt-4 text-sm leading-7" style={{ color: "#d1d5db" }}>{result.summary}</p>
            <ul className="mt-4 space-y-2">
              {result.stringReadings.map((row) => (
                <li key={row.label} className="flex justify-between text-sm font-mono">
                  <span style={{ color: "#6b7280" }}>{row.label}</span>
                  <span style={{ color: ACCENT }}>{row.cents} cents</span>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </main>
  )
}
