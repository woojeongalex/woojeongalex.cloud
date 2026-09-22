"use client"

import { Loader2, RotateCcw, Settings2, Trophy } from "lucide-react"
import { useUserSession } from "@/hooks/use-user-session"
import {
  RHYTHM_DIFFICULTY_LABEL,
  type RhythmDifficulty,
  type RhythmKeys,
  type RhythmPlayResult,
} from "@/lib/rhythm-api"
import {
  RHYTHM_JUDGEMENT_LABEL,
  rhythmGrade,
  type RhythmJudgement,
  type RhythmResult,
} from "@/lib/rhythm-scoring"
import { cn } from "@/lib/utils"

const JUDGEMENTS: RhythmJudgement[] = ["cool", "good", "bad", "miss"]

const JUDGEMENT_TEXT: Record<RhythmJudgement, string> = {
  cool: "text-sky-500",
  good: "text-green-500",
  bad: "text-amber-500",
  miss: "text-red-500",
}

type RhythmResultPanelProps = {
  keys: RhythmKeys
  difficulty: RhythmDifficulty
  /** 화면에서 계산한 결과 — 서버 결과가 오기 전까지 보여 준다 */
  result: RhythmResult
  /** 서버가 입력 기록으로 다시 채점한 결과 */
  server: RhythmPlayResult | null
  sending: boolean
  error: string | null
  onResend: () => void
  onRetry: () => void
  onChangeSheet: () => void
}

export function RhythmResultPanel({
  keys,
  difficulty,
  result,
  server,
  sending,
  error,
  onResend,
  onRetry,
  onChangeSheet,
}: RhythmResultPanelProps) {
  const user = useUserSession()
  const score = server?.score ?? result.score
  const accuracy = server?.accuracy ?? result.accuracy
  const maxCombo = server?.max_combo ?? result.maxCombo
  const counts: Record<RhythmJudgement, number> = server
    ? { cool: server.cool, good: server.good, bad: server.bad, miss: server.miss }
    : result.counts
  const fullCombo = counts.bad === 0 && counts.miss === 0

  return (
    <section className="rounded-3xl border border-border bg-card p-6">
      <div className="flex flex-wrap items-end justify-between gap-6">
        <div className="flex items-end gap-5">
          <span className="font-mono text-7xl font-black leading-none text-sky-500">
            {rhythmGrade(accuracy)}
          </span>
          <div>
            <p className="text-sm font-medium text-muted-foreground">
              {keys}키 {RHYTHM_DIFFICULTY_LABEL[difficulty]} · {server ? "서버 채점" : "이번 점수"}
            </p>
            <p className="mt-1 font-mono text-5xl font-semibold tabular-nums">
              {score.toLocaleString()}
            </p>
          </div>
        </div>
        <dl className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <dt className="text-muted-foreground">정확도</dt>
            <dd className="font-mono text-xl font-semibold">{accuracy.toFixed(2)}%</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">최대 콤보</dt>
            <dd className="font-mono text-xl font-semibold">{maxCombo}</dd>
          </div>
        </dl>
      </div>

      {fullCombo && counts.cool + counts.good > 0 && (
        <p className="mt-4 font-mono text-sm font-semibold text-sky-500">FULL COMBO!</p>
      )}

      <ul className="mt-5 grid grid-cols-4 gap-2 font-mono text-sm">
        {JUDGEMENTS.map((j) => (
          <li key={j} className="rounded-2xl border border-border px-3 py-2 text-center">
            <span className={cn("block text-xs font-semibold", JUDGEMENT_TEXT[j])}>
              {RHYTHM_JUDGEMENT_LABEL[j]}
            </span>
            <span className="text-lg font-semibold tabular-nums">{counts[j]}</span>
          </li>
        ))}
      </ul>

      <div className="mt-5 min-h-6 text-sm" aria-live="polite">
        {sending && (
          <p className="inline-flex items-center gap-2 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            기록을 저장하는 중입니다…
          </p>
        )}
        {server && server.rank !== null && (
          <p className="inline-flex items-center gap-2">
            <Trophy className="h-4 w-4 text-sky-500" aria-hidden="true" />
            랭킹 <strong className="font-mono">{server.rank}위</strong>
            {server.is_personal_best
              ? " · 개인 최고 기록!"
              : ` · 내 최고 ${server.best_score?.toLocaleString()}점`}
          </p>
        )}
        {server && !user && (
          <p className="text-muted-foreground">
            로그인하지 않아 이번 기록은 랭킹에 오르지 않습니다.
          </p>
        )}
        {error && (
          <p role="alert" className="text-destructive">
            {error}{" "}
            <button type="button" onClick={onResend} className="underline underline-offset-4">
              다시 저장
            </button>
          </p>
        )}
      </div>

      <div className="mt-4 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={onRetry}
          className="inline-flex items-center gap-2 rounded-full bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-80"
        >
          <RotateCcw className="h-4 w-4" aria-hidden="true" />
          다시 하기
        </button>
        <button
          type="button"
          onClick={onChangeSheet}
          className="inline-flex items-center gap-2 rounded-full border border-border bg-background px-5 py-3 text-sm font-medium transition-colors hover:bg-accent"
        >
          <Settings2 className="h-4 w-4" aria-hidden="true" />
          난이도·설정 바꾸기
        </button>
      </div>
    </section>
  )
}
