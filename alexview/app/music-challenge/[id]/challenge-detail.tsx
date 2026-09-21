"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { ArrowLeft, ArrowRight, Mic, Sparkles, Square, Upload } from "lucide-react"
import { useAsyncAction } from "@/hooks/use-async-action"
import { useMicRecording } from "@/hooks/use-mic-recording"
import { blobToWav } from "@/lib/audio-wav"
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

type SubmitMode = "record" | "upload"

const SUBMIT_MODES: SubmitMode[] = ["record", "upload"]

const SUBMIT_MODE_LABEL: Record<SubmitMode, string> = {
  record: "바로 녹음하기",
  upload: "파일 올리기",
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
  const [submitMode, setSubmitMode] = useState<SubmitMode>("record")
  const [recordedWav, setRecordedWav] = useState<Blob | null>(null)
  const [recordedUrl, setRecordedUrl] = useState<string | null>(null)
  const [micError, setMicError] = useState<string | null>(null)
  const { loading: submitting, error: submitError, run } = useAsyncAction()
  const mic = useMicRecording()

  // 미리듣기용 object URL 은 새 녹음마다 교체하고 언마운트 때 해제한다.
  useEffect(() => {
    if (!recordedWav) {
      setRecordedUrl(null)
      return
    }
    const url = URL.createObjectURL(recordedWav)
    setRecordedUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [recordedWav])

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

  const handleStartRecording = async () => {
    setMicError(null)
    setRecordedWav(null)
    setEvaluation(null)
    const ok = await mic.start()
    if (!ok) setMicError(UI_ERRORS.micStartFailed)
  }

  const handleStopRecording = () => {
    void mic.stop(async (_sec, recorded) => {
      // 브라우저는 webm/mp4 로만 녹음하는데 백엔드는 그걸 디코딩하지 못한다.
      // WAV 로 바꿔 보내야 음정·박자 지표가 나온다.
      const wav = await blobToWav(recorded)
      if (!wav) {
        setMicError(UI_ERRORS.challengeSubmitFailed)
        return
      }
      setRecordedWav(wav)
    })
  }

  const handleSubmitRecording = async () => {
    if (!recordedWav) return
    const file = new File([recordedWav], "recording.wav", { type: "audio/wav" })
    setEvaluation(null)
    await run(() => submitChallenge({ challengeId, mediaType: "audio", file }), {
      fallbackError: UI_ERRORS.challengeSubmitFailed,
      onSuccess: (result) => setEvaluation(result),
    })
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
                바로 불러서 녹음하거나, 준비한 파일을 올리면 AI가 채점합니다.
              </p>

              <div className="mt-6 flex gap-2">
                {SUBMIT_MODES.map((mode) => (
                  <button
                    key={mode}
                    type="button"
                    aria-pressed={submitMode === mode}
                    onClick={() => {
                      setSubmitMode(mode)
                      mic.reset()
                      setRecordedWav(null)
                    }}
                    className={`rounded-full border px-4 py-2 text-sm transition-colors ${
                      submitMode === mode
                        ? "border-foreground bg-foreground text-background"
                        : "border-border bg-background text-muted-foreground hover:bg-accent"
                    }`}
                  >
                    {SUBMIT_MODE_LABEL[mode]}
                  </button>
                ))}
              </div>

              {submitMode === "record" ? (
                <div className="mt-6 space-y-5">
                  <p className="rounded-2xl border border-border bg-muted/40 px-4 py-3 text-sm leading-6 text-muted-foreground">
                    위의 AI 음악을 재생해 들으면서 따라 부르세요. 스피커로 들으면
                    원곡이 함께 녹음되니 <strong>이어폰 사용을 권장</strong>합니다.
                  </p>

                  {mic.recording === "recording" ? (
                    <button
                      type="button"
                      onClick={handleStopRecording}
                      className="inline-flex items-center gap-2 rounded-full border border-foreground bg-foreground px-6 py-3.5 text-sm font-semibold text-background"
                    >
                      <Square className="h-4 w-4" aria-hidden="true" />
                      녹음 중지
                      <span className="ml-1 h-2 w-2 animate-pulse rounded-full bg-background/70" />
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={handleStartRecording}
                      className="inline-flex items-center gap-2 rounded-full border border-border bg-background px-6 py-3.5 text-sm font-medium transition-colors hover:bg-accent"
                    >
                      <Mic className="h-4 w-4" aria-hidden="true" />
                      {mic.recording === "done" ? "다시 녹음하기" : "녹음 시작"}
                    </button>
                  )}

                  {micError && (
                    <p role="status" className="text-sm text-muted-foreground">
                      {micError}
                    </p>
                  )}

                  {recordedWav && (
                    <div className="rounded-2xl border border-border bg-background/60 p-4">
                      <p className="text-sm font-medium">
                        녹음 완료 · {mic.durationSec}초
                      </p>
                      <audio
                        className="mt-3 w-full"
                        controls
                        src={recordedUrl ?? undefined}
                      />
                    </div>
                  )}

                  <button
                    type="button"
                    onClick={handleSubmitRecording}
                    disabled={submitting || !recordedWav}
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
                </div>
              ) : (
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
                    <label htmlFor="media_file" className="text-sm font-medium">
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
              )}
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

                {(evaluation.pitch_score !== null ||
                  evaluation.rhythm_score !== null) && (
                  <div className="mt-8 grid gap-4 sm:grid-cols-2">
                    <MetricBar
                      label="음정 안정성"
                      value={evaluation.pitch_score}
                    />
                    <MetricBar
                      label="박자 일관성"
                      value={evaluation.rhythm_score}
                    />
                  </div>
                )}

                {evaluation.tempo !== null && evaluation.tempo > 0 && (
                  <p className="mt-4 font-mono text-xs text-muted-foreground">
                    측정 템포 {evaluation.tempo.toFixed(1)} BPM
                  </p>
                )}

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

type MetricBarProps = {
  label: string
  value: number | null
}

/**
 * 신호 분석으로 측정한 객관 지표. 종합 점수(AI 판단)와 달리 같은 파일이면
 * 항상 같은 값이 나오므로, 사용자가 연습 효과를 비교할 수 있는 기준이 된다.
 */
function MetricBar({ label, value }: MetricBarProps) {
  if (value === null) return null
  const clamped = Math.min(100, Math.max(0, value))
  return (
    <div className="rounded-2xl border border-border bg-background/60 p-4">
      <div className="flex items-baseline justify-between">
        <span className="text-sm text-muted-foreground">{label}</span>
        <span className="font-mono text-lg font-semibold">{clamped}</span>
      </div>
      <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-foreground transition-all"
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  )
}
