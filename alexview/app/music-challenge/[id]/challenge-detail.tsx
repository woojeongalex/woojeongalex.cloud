"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { ArrowLeft, ArrowRight, Sparkles, Upload } from "lucide-react"
import { useAsyncAction } from "@/hooks/use-async-action"
import {
  CHALLENGE_TYPE_LABEL,
  MEDIA_TYPE_LABEL,
  fetchChallenge,
  submitChallenge,
  type Challenge,
  type Evaluation,
  type MediaType,
} from "@/lib/music-challenge-api"
import { toUserFacingMessage, UI_ERRORS } from "@/lib/user-facing-error"

const MEDIA_TYPES: MediaType[] = ["audio", "video"]

const ACCEPT: Record<MediaType, string> = {
  audio: "audio/*",
  video: "video/*",
}

type ChallengeDetailProps = {
  challengeId: number
}

export function ChallengeDetail({ challengeId }: ChallengeDetailProps) {
  const [challenge, setChallenge] = useState<Challenge | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [mediaType, setMediaType] = useState<MediaType>("audio")
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null)
  const { loading: submitting, error: submitError, run } = useAsyncAction()

  useEffect(() => {
    let alive = true
    fetchChallenge(challengeId)
      .then((data) => {
        if (alive) setChallenge(data)
      })
      .catch((e) => {
        if (alive) setLoadError(toUserFacingMessage(e, UI_ERRORS.challengeLoadFailed))
      })
      .finally(() => {
        if (alive) setLoading(false)
      })
    return () => {
      alive = false
    }
  }, [challengeId])

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const file = formData.get("media_file")

    if (!(file instanceof File) || file.size === 0) return

    setEvaluation(null)
    await run(
      () => submitChallenge({ challengeId, mediaType, file }),
      {
        fallbackError: UI_ERRORS.challengeSubmitFailed,
        onSuccess: (result) => setEvaluation(result),
      }
    )
  }

  return (
    <main className="min-h-[calc(100vh-4rem)] min-w-0 overflow-x-hidden bg-background text-foreground">
      <div className="mx-auto max-w-4xl px-4 py-10 md:py-14">
        <Link
          href="/music-challenge"
          className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          챌린지 목록
        </Link>

        {loading && (
          <div className="mt-8 space-y-4" role="status">
            <span className="sr-only">챌린지를 불러오는 중입니다.</span>
            <div className="h-10 w-2/3 animate-pulse rounded-xl bg-muted/50" />
            <div className="h-32 animate-pulse rounded-3xl bg-muted/40" />
          </div>
        )}

        {!loading && loadError && (
          <p
            role="status"
            className="mt-8 rounded-2xl border border-border bg-muted/40 px-5 py-6 text-sm text-muted-foreground"
          >
            {loadError}
          </p>
        )}

        {!loading && !loadError && challenge && (
          <>
            {/* 챌린지 정보 */}
            <header className="mt-6">
              <span className="rounded-full border border-border bg-muted px-3 py-1 text-xs text-muted-foreground">
                {CHALLENGE_TYPE_LABEL[challenge.challenge_type] ??
                  challenge.challenge_type}
              </span>
              <h1 className="mt-4 text-3xl font-semibold tracking-tight sm:text-4xl">
                {challenge.title}
              </h1>
              <p className="mt-4 text-base leading-8 text-muted-foreground">
                {challenge.description}
              </p>
            </header>

            {/* AI 음악 재생 */}
            <section className="mt-8 rounded-3xl border border-border bg-card p-6">
              <h2 className="text-sm font-medium text-muted-foreground">AI 생성 음악</h2>
              {challenge.music_url ? (
                <audio
                  className="mt-4 w-full"
                  controls
                  preload="none"
                  src={challenge.music_url}
                >
                  브라우저가 오디오 재생을 지원하지 않습니다.
                </audio>
              ) : (
                <p className="mt-4 text-sm text-muted-foreground">
                  등록된 음원이 없습니다.
                </p>
              )}
            </section>

            {/* 제출 폼 */}
            <section className="mt-6 rounded-3xl border border-border bg-card p-6">
              <h2 className="text-xl font-semibold">내 챌린지 제출</h2>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                노래하거나 연주한 파일을 올리면 AI가 바로 채점합니다.
              </p>

              <form className="mt-6 space-y-6" onSubmit={handleSubmit}>
                <fieldset>
                  <legend className="text-sm font-medium">제출 형식</legend>
                  <div className="mt-3 flex gap-2">
                    {MEDIA_TYPES.map((type) => (
                      <button
                        key={type}
                        type="button"
                        aria-pressed={mediaType === type}
                        onClick={() => setMediaType(type)}
                        className={`rounded-full border px-4 py-2 text-sm transition-colors ${
                          mediaType === type
                            ? "border-foreground bg-foreground text-background"
                            : "border-border bg-background text-muted-foreground hover:bg-accent"
                        }`}
                      >
                        {MEDIA_TYPE_LABEL[type]}
                      </button>
                    ))}
                  </div>
                </fieldset>

                <div>
                  <label
                    htmlFor="media_file"
                    className="text-sm font-medium"
                  >
                    파일 선택
                  </label>
                  <input
                    id="media_file"
                    name="media_file"
                    type="file"
                    required
                    accept={ACCEPT[mediaType]}
                    className="mt-3 block w-full cursor-pointer rounded-xl border border-border bg-background px-4 py-3 text-sm text-muted-foreground file:mr-4 file:rounded-full file:border-0 file:bg-foreground file:px-4 file:py-2 file:text-sm file:font-medium file:text-background"
                  />
                </div>

                <button
                  type="submit"
                  disabled={submitting}
                  className="inline-flex items-center justify-center gap-2 rounded-full bg-primary px-6 py-3.5 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-80 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <Upload className="h-4 w-4" aria-hidden="true" />
                  {submitting ? "AI가 채점하는 중…" : "제출하고 채점받기"}
                </button>

                {submitError && (
                  <p role="status" className="text-sm text-muted-foreground">
                    {submitError}
                  </p>
                )}
              </form>
            </section>

            {/* 평가 결과 */}
            {evaluation && (
              <section
                className="mt-6 rounded-3xl border-2 border-foreground/15 bg-secondary p-6"
                role="status"
              >
                <div className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5" aria-hidden="true" />
                  <h2 className="text-xl font-semibold">AI 채점 결과</h2>
                </div>

                <div className="mt-6 flex items-baseline gap-2">
                  <span className="font-mono text-5xl font-semibold">
                    {evaluation.score}
                  </span>
                  <span className="text-sm text-muted-foreground">/ 100</span>
                </div>
                <div
                  className="mt-3 h-2 w-full overflow-hidden rounded-full bg-muted"
                  role="presentation"
                >
                  <div
                    className="h-full rounded-full bg-foreground transition-all"
                    style={{
                      width: `${Math.min(100, Math.max(0, evaluation.score))}%`,
                    }}
                  />
                </div>

                <p className="mt-6 whitespace-pre-line text-sm leading-7 text-muted-foreground">
                  {evaluation.feedback}
                </p>

                {evaluation.next_challenge_id !== null && (
                  <Link
                    href={`/music-challenge/${evaluation.next_challenge_id}`}
                    className="mt-6 inline-flex items-center gap-2 rounded-full border border-border bg-background px-5 py-3 text-sm font-medium transition-colors hover:bg-accent"
                  >
                    추천받은 다음 챌린지
                    <ArrowRight className="h-4 w-4" aria-hidden="true" />
                  </Link>
                )}
              </section>
            )}
          </>
        )}
      </div>
    </main>
  )
}
