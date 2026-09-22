"use client"

import { useState } from "react"
import { Loader2, Upload } from "lucide-react"
import { MelodyPreview } from "@/components/music/melody-preview"
import { useAsyncAction } from "@/hooks/use-async-action"
import {
  INSTRUMENT_LABEL,
  MELODY_SOURCE_LABEL,
  uploadStems,
  type Chart,
  type ChartStatus,
  type InstrumentKind,
  type MelodySource,
} from "@/lib/music-challenge-api"
import { formatSeconds } from "@/lib/lyrics"
import { midiToName } from "@/lib/music-notes"
import { UI_ERRORS } from "@/lib/user-facing-error"
import { cn } from "@/lib/utils"

const STATUS_LABEL: Record<ChartStatus, string> = {
  empty: "스템 없음",
  processing: "정답 멜로디 추출 중",
  ready: "준비 완료",
  failed: "추출 실패",
}

const MELODY_SOURCES: MelodySource[] = ["vocal", "instrument"]
const INSTRUMENTS: InstrumentKind[] = ["piano", "guitar", "violin", "flute", "saxophone", "other"]

/** 어떤 스템을 올려야 하는지는 노래냐 연주곡이냐에 따라 다르다. */
const GUIDE: Record<MelodySource, { melodyLabel: string; text: string }> = {
  vocal: {
    melodyLabel: "보컬 스템",
    text: "Suno의 Get Stems로 받은 보컬 트랙에서 정답 멜로디를 뽑고, 반주는 도전 화면에서 틀어 줍니다. 완성곡을 보컬 자리에 올리면 악기 소리까지 음표로 잡혀 판정이 틀어집니다.",
  },
  instrument: {
    melodyLabel: "멜로디 악기 스템",
    text: "멜로디를 연주하는 악기 하나만 담긴 스템(예: 피아노 스템)을 올리세요. 나머지 악기를 합친 트랙은 반주로 올립니다. 한 번에 한 음씩 이어지는 멜로디만 판정할 수 있고, 화음(여러 음을 동시에 누르는 것)은 판정하지 않습니다.",
  },
}

type StemsPanelProps = {
  challengeId: number
  chart: Chart
  currentTime: number
  onChartChange: (chart: Chart) => void
}

export function StemsPanel({ challengeId, chart, currentTime, onChartChange }: StemsPanelProps) {
  const [source, setSource] = useState<MelodySource>(chart.melody_source)
  const [instrument, setInstrument] = useState<InstrumentKind>(chart.instrument ?? "piano")
  const { loading, error, run } = useAsyncAction()

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const form = e.currentTarget
    const formData = new FormData(form)
    const melody = formData.get("melody_file")
    const backing = formData.get("backing_file")
    if (!(melody instanceof File) || melody.size === 0) return

    const result = await run(
      () =>
        uploadStems({
          challengeId,
          melodyFile: melody,
          backingFile: backing instanceof File && backing.size > 0 ? backing : null,
          melodySource: source,
          instrument: source === "instrument" ? instrument : null,
        }),
      { fallbackError: UI_ERRORS.requestFailed, onSuccess: onChartChange }
    )
    if (result) form.reset()
  }

  const midis = chart.notes.map((n) => n.midi)
  const busy = loading || chart.status === "processing"
  const guide = GUIDE[source]

  return (
    <section className="rounded-3xl border border-border bg-card p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-muted-foreground">1단계</p>
          <h2 className="mt-1 text-xl font-semibold">스템 올리기 · 정답 멜로디</h2>
        </div>
        <span
          role="status"
          className={cn(
            "inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium",
            chart.status === "ready" && "border-foreground/30 text-foreground",
            chart.status === "failed" && "border-destructive/40 text-destructive",
            (chart.status === "empty" || chart.status === "processing") &&
              "border-border text-muted-foreground"
          )}
        >
          {chart.status === "processing" && (
            <Loader2 className="h-3 w-3 animate-spin" aria-hidden="true" />
          )}
          {STATUS_LABEL[chart.status]}
        </span>
      </div>

      <fieldset className="mt-5" disabled={busy}>
        <legend className="text-sm font-medium">이 곡은</legend>
        <div className="mt-2 inline-flex rounded-full border border-border bg-muted/40 p-1">
          {MELODY_SOURCES.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setSource(s)}
              aria-pressed={source === s}
              className={cn(
                "rounded-full px-4 py-1.5 text-sm font-medium transition-colors",
                source === s
                  ? "bg-background text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              {MELODY_SOURCE_LABEL[s]}
            </button>
          ))}
        </div>
        {source === "instrument" && (
          <label className="mt-3 flex flex-wrap items-center gap-2 text-sm">
            <span className="font-medium">멜로디 악기</span>
            <select
              value={instrument}
              onChange={(e) => setInstrument(e.target.value as InstrumentKind)}
              className="rounded-lg border border-border bg-background px-3 py-1.5 text-sm"
            >
              {INSTRUMENTS.map((k) => (
                <option key={k} value={k}>
                  {INSTRUMENT_LABEL[k]}
                </option>
              ))}
            </select>
          </label>
        )}
      </fieldset>

      <p className="mt-4 text-sm leading-6 text-muted-foreground">{guide.text}</p>

      <form onSubmit={handleSubmit} className="mt-5 grid gap-4 sm:grid-cols-2">
        <label className="grid gap-2 text-sm">
          <span className="font-medium">
            {guide.melodyLabel} <span className="text-muted-foreground">(필수 · WAV/MP3)</span>
          </span>
          <input
            name="melody_file"
            type="file"
            accept="audio/*"
            required
            disabled={busy}
            className="rounded-xl border border-border bg-background px-3 py-2 text-sm file:mr-3 file:rounded-lg file:border-0 file:bg-muted file:px-3 file:py-1 file:text-sm"
          />
        </label>
        <label className="grid gap-2 text-sm">
          <span className="font-medium">
            반주 스템 <span className="text-muted-foreground">(선택 · 이미 있으면 유지)</span>
          </span>
          <input
            name="backing_file"
            type="file"
            accept="audio/*"
            disabled={busy}
            className="rounded-xl border border-border bg-background px-3 py-2 text-sm file:mr-3 file:rounded-lg file:border-0 file:bg-muted file:px-3 file:py-1 file:text-sm"
          />
        </label>
        <div className="sm:col-span-2">
          <button
            type="submit"
            disabled={busy}
            className="inline-flex items-center gap-2 rounded-full bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-80 disabled:opacity-50"
          >
            {busy ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            ) : (
              <Upload className="h-4 w-4" aria-hidden="true" />
            )}
            {loading ? "올리는 중…" : chart.status === "processing" ? "추출 중…" : "올리고 추출하기"}
          </button>
          {chart.status === "processing" && (
            <p className="mt-2 text-xs text-muted-foreground">
              3분 곡 기준 30초~1분 정도 걸립니다. 이 화면을 떠나도 계속 진행됩니다.
            </p>
          )}
        </div>
      </form>

      {error && (
        <p role="alert" className="mt-4 text-sm text-destructive">
          {error}
        </p>
      )}
      {chart.status === "failed" && chart.error && (
        <p role="alert" className="mt-4 text-sm text-destructive">
          {chart.error}
        </p>
      )}

      {chart.status === "ready" && chart.duration !== null && (
        <div className="mt-6">
          <dl className="grid grid-cols-2 gap-3 text-sm sm:grid-cols-5">
            <div>
              <dt className="text-muted-foreground">멜로디</dt>
              <dd className="font-semibold">
                {chart.melody_source === "instrument" && chart.instrument
                  ? INSTRUMENT_LABEL[chart.instrument]
                  : "보컬"}
              </dd>
            </div>
            <div>
              <dt className="text-muted-foreground">음표</dt>
              <dd className="font-mono font-semibold">{chart.notes.length}개</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">곡 길이</dt>
              <dd className="font-mono font-semibold">{formatSeconds(chart.duration)}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">음역</dt>
              <dd className="font-mono font-semibold">
                {midiToName(Math.min(...midis))} – {midiToName(Math.max(...midis))}
              </dd>
            </div>
            <div>
              <dt className="text-muted-foreground">반주</dt>
              <dd className="font-semibold">{chart.backing_url ? "있음" : "없음 (원곡 사용)"}</dd>
            </div>
          </dl>
          <MelodyPreview
            notes={chart.notes}
            duration={chart.duration}
            currentTime={currentTime}
            className="mt-4"
          />
          <p className="mt-2 text-xs text-muted-foreground">
            위 플레이어로 원곡을 틀면 재생선이 따라갑니다. 들리는 멜로디와 음표 모양이
            맞는지 확인해 주세요.
          </p>
        </div>
      )}
    </section>
  )
}
