"use client"

import { useState } from "react"
import Link from "next/link"
import { ArrowRight, Loader2, RotateCcw, Trophy, Upload } from "lucide-react"
import { useAsyncAction } from "@/hooks/use-async-action"
import { useUserSession } from "@/hooks/use-user-session"
import { blobToWav } from "@/lib/audio-wav"
import { JUDGEMENT_LABEL, type FinalScore, type Judgement } from "@/lib/karaoke-scoring"
import { submitChallenge, type Evaluation } from "@/lib/music-challenge-api"
import { UI_ERRORS, UserFacingError } from "@/lib/user-facing-error"

const JUDGEMENTS: Judgement[] = ["perfect", "great", "good", "miss"]

type ResultPanelProps = {
  challengeId: number
  final: FinalScore
  recording: Blob | null
  startOffset: number
  onRetry: () => void
}

export function ResultPanel({ challengeId, final, recording, startOffset, onRetry }: ResultPanelProps) {
  const user = useUserSession()
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null)
  const { loading, error, run } = useAsyncAction()

  const submit = async () => {
    if (!recording) return
    await run(
      async () => {
        // 서버에는 ffmpeg 가 없어 브라우저 녹음(webm)을 읽지 못한다. WAV 로 바꿔 보낸다.
        const wav = await blobToWav(recording, { sampleRate: 16000 })
        if (!wav) throw new UserFacingError("녹음을 변환하지 못했습니다. 다시 도전해 주세요.")
        return submitChallenge({
          challengeId,
          mediaType: "audio",
          file: new File([wav], "karaoke.wav", { type: "audio/wav" }),
          karaokeStartOffset: startOffset,
        })
      },
      { fallbackError: UI_ERRORS.requestFailed, onSuccess: setEvaluation }
    )
  }

  const karaoke = evaluation?.karaoke ?? null
  const shownScore = karaoke?.score ?? final.score

  return (
    <section className="mt-6 rounded-3xl border border-border bg-card p-6 shadow-[0_0_40px_-18px_#ff2e97] animate-in fade-in slide-in-from-bottom-6 duration-700">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="font-orbitron text-xs font-bold tracking-[0.2em] text-neon-cyan">
            {karaoke ? "최종 점수 (서버 채점)" : "이번 점수"}
          </p>
          <p className="neon-text mt-1 font-orbitron text-6xl font-black tabular-nums text-white">{shownScore}</p>
        </div>
        <dl className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <dt className="text-muted-foreground">음정</dt>
            <dd className="font-orbitron text-xl font-bold text-neon-cyan">
              {karaoke?.pitch_accuracy ?? final.pitchAccuracy}%
            </dd>
          </div>
          <div>
            <dt className="text-muted-foreground">박자</dt>
            <dd className="font-orbitron text-xl font-bold text-neon-cyan">
              {karaoke?.timing_accuracy ?? final.timingAccuracy}%
            </dd>
          </div>
          <div>
            <dt className="text-muted-foreground">최대 콤보</dt>
            <dd className="font-orbitron text-xl font-bold text-neon-cyan">{final.maxCombo}</dd>
          </div>
        </dl>
      </div>

      <ul className="mt-5 flex flex-wrap gap-2 font-orbitron text-xs">
        {JUDGEMENTS.map((j) => (
          <li key={j} className="rounded-full border border-border bg-night-950 px-3 py-1">
            {JUDGEMENT_LABEL[j]} {final.counts[j]}
          </li>
        ))}
        <li className="rounded-full border border-border bg-night-950 px-3 py-1 text-muted-foreground">
          음표 {final.noteCount}개
        </li>
      </ul>

      {!evaluation && (
        <div className="mt-6 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={() => void submit()}
            disabled={loading || !recording}
            className="inline-flex items-center gap-2 glow-button rounded-full bg-primary px-5 py-3 text-sm font-bold text-primary-foreground disabled:opacity-50"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            ) : (
              <Upload className="h-4 w-4" aria-hidden="true" />
            )}
            {loading ? "채점 중… (AI 코칭까지 30초 정도)" : user ? "제출하고 랭킹 등록" : "제출하고 AI 코칭 받기"}
          </button>
          <button
            type="button"
            onClick={onRetry}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-full border border-neon-cyan/60 px-5 py-3 text-sm font-medium text-neon-cyan transition-colors hover:bg-neon-cyan/10"
          >
            <RotateCcw className="h-4 w-4" aria-hidden="true" />
            다시 도전
          </button>
          {!user && (
            <p className="w-full text-xs text-muted-foreground">
              로그인하지 않으면 점수는 랭킹과 기록에 남지 않습니다.
            </p>
          )}
          {error && (
            <p role="alert" className="w-full text-sm text-destructive">
              {error}
            </p>
          )}
        </div>
      )}

      {evaluation && (
        <div className="mt-6 space-y-5">
          {/* 로그인 상태로 보이는데 순위가 없다 = 서버가 익명으로 받았다.
              아무 말도 안 하면 기록이 사라진 걸 알아챌 방법이 없다. */}
          {user && karaoke && karaoke.rank === null && (
            <p className="rounded-2xl border border-destructive/40 bg-destructive/5 px-5 py-4 text-sm">
              로그인이 풀려 이 점수는 랭킹과 기록에 남지 않았습니다. 다시 로그인한 뒤 한 번 더
              도전해 주세요.
            </p>
          )}
          {karaoke && karaoke.rank !== null && (
            <div className="flex flex-wrap items-center gap-3 rounded-2xl border border-neon-yellow/40 bg-neon-yellow/5 px-5 py-4">
              <Trophy className="h-5 w-5 text-neon-yellow" aria-hidden="true" />
              <p className="text-sm">
                이 곡 랭킹 <strong className="font-orbitron text-lg text-neon-yellow">{karaoke.rank}위</strong>
                {karaoke.is_personal_best ? " · 개인 최고 기록!" : ` · 내 최고 ${karaoke.best_score}점`}
              </p>
              <Link
                href={`/music-challenge/${challengeId}#ranking`}
                className="ml-auto text-sm font-medium text-neon-cyan underline underline-offset-4"
              >
                랭킹 보기
              </Link>
            </div>
          )}
          <div>
            <p className="font-orbitron text-xs font-bold tracking-[0.25em] text-neon-cyan">AI 코칭</p>
            <p className="mt-2 whitespace-pre-line text-sm leading-7 text-foreground/90">{evaluation.feedback}</p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={onRetry}
              className="inline-flex items-center gap-2 rounded-full border border-neon-cyan/60 px-5 py-3 text-sm font-medium text-neon-cyan transition-colors hover:bg-neon-cyan/10"
            >
              <RotateCcw className="h-4 w-4" aria-hidden="true" />
              다시 도전
            </button>
            {evaluation.next_challenge_id && (
              <Link
                href={`/music-challenge/${evaluation.next_challenge_id}`}
                className="inline-flex items-center gap-2 glow-button rounded-full bg-primary px-5 py-3 text-sm font-bold text-primary-foreground"
              >
                다음 추천곡 도전
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Link>
            )}
          </div>
        </div>
      )}
    </section>
  )
}
