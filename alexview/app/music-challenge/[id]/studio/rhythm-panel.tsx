"use client"

import { useEffect, useState } from "react"
import { Gamepad2, Loader2 } from "lucide-react"
import { StatusNote } from "@/components/common/status-note"
import {
  RHYTHM_DIFFICULTIES,
  RHYTHM_DIFFICULTY_LABEL,
  RHYTHM_KEYS,
  buildRhythmChart,
  fetchRhythmChart,
  type RhythmChart,
} from "@/lib/rhythm-api"
import { toUserFacingMessage, UI_ERRORS } from "@/lib/user-facing-error"

const POLL_MS = 3000

type RhythmPanelProps = {
  challengeId: number
}

/** 관리자 — 원곡으로 리듬 게임 채보 6개를 만든다. 분석은 서버에서 10~20초 걸린다. */
export function RhythmPanel({ challengeId }: RhythmPanelProps) {
  const [chart, setChart] = useState<RhythmChart | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [requesting, setRequesting] = useState(false)

  useEffect(() => {
    let alive = true
    fetchRhythmChart(challengeId)
      .then((c) => {
        if (alive) setChart(c)
      })
      .catch((e) => {
        if (alive) setError(toUserFacingMessage(e, UI_ERRORS.requestFailed))
      })
    return () => {
      alive = false
    }
  }, [challengeId])

  const processing = chart?.status === "processing"
  useEffect(() => {
    if (!processing) return
    const id = setInterval(() => {
      fetchRhythmChart(challengeId)
        .then(setChart)
        .catch(() => {
          // 한 번 실패해도 다음 주기에 다시 묻는다.
        })
    }, POLL_MS)
    return () => clearInterval(id)
  }, [processing, challengeId])

  const build = async () => {
    setRequesting(true)
    setError(null)
    try {
      setChart(await buildRhythmChart(challengeId))
    } catch (e) {
      setError(toUserFacingMessage(e, UI_ERRORS.requestFailed))
    } finally {
      setRequesting(false)
    }
  }

  const hasSheets = (chart?.sheets.length ?? 0) > 0

  return (
    <section className="rounded-3xl border border-border bg-card p-6">
      <div className="flex items-center gap-2">
        <Gamepad2 className="h-5 w-5 text-sky-500" aria-hidden="true" />
        <h2 className="text-xl font-semibold">리듬 게임 채보</h2>
      </div>
      <p className="mt-2 text-sm leading-6 text-muted-foreground">
        원곡에서 박자와 소리가 시작되는 순간을 찾아 4키·7키 × 쉬움·보통·어려움 채보를
        자동으로 만듭니다. 스템은 필요 없습니다.
      </p>

      {chart && hasSheets && (
        <table className="mt-4 w-full text-sm">
          <thead>
            <tr className="text-left text-muted-foreground">
              <th className="py-1 font-medium">키</th>
              {RHYTHM_DIFFICULTIES.map((d) => (
                <th key={d} className="py-1 font-medium">
                  {RHYTHM_DIFFICULTY_LABEL[d]}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="font-mono">
            {RHYTHM_KEYS.map((k) => (
              <tr key={k} className="border-t border-border">
                <td className="py-1.5">{k}키</td>
                {RHYTHM_DIFFICULTIES.map((d) => {
                  const s = chart.sheets.find((x) => x.keys === k && x.difficulty === d)
                  return (
                    <td key={d} className="py-1.5">
                      {s ? `Lv.${s.level} · ${s.note_count}` : "—"}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {chart?.bpm && hasSheets && (
        <p className="mt-2 text-xs text-muted-foreground">
          BPM {Math.round(chart.bpm)} · 곡 길이 {Math.round(chart.duration ?? 0)}초
        </p>
      )}

      {chart?.error && <StatusNote className="mt-4">{chart.error}</StatusNote>}
      {error && (
        <p role="alert" className="mt-4 text-sm text-destructive">
          {error}
        </p>
      )}

      <button
        type="button"
        onClick={() => void build()}
        disabled={requesting || processing || !chart}
        className="mt-5 inline-flex items-center gap-2 rounded-full bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-80 disabled:opacity-50"
      >
        {(requesting || processing) && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />}
        {processing ? "채보를 만드는 중…" : hasSheets ? "채보 다시 만들기" : "채보 만들기"}
      </button>
    </section>
  )
}
