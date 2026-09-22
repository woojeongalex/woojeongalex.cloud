"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { ArrowLeft, ArrowRight, Upload } from "lucide-react"
import { useAsyncAction } from "@/hooks/use-async-action"
import { useUserSession } from "@/hooks/use-user-session"
import {
  CHALLENGE_TYPE_LABEL,
  createChallenge,
  type Challenge,
  type ChallengeType,
} from "@/lib/music-challenge-api"
import { UI_ERRORS } from "@/lib/user-facing-error"

const CHALLENGE_TYPES: ChallengeType[] = ["vocal", "instrument", "both"]

export default function NewChallengePage() {
  const user = useUserSession()
  const [mounted, setMounted] = useState(false)
  const [challengeType, setChallengeType] = useState<ChallengeType>("vocal")
  const [created, setCreated] = useState<Challenge | null>(null)
  const { loading, error, run } = useAsyncAction()

  useEffect(() => setMounted(true), [])

  const isAdmin = user?.role === "admin"

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const form = e.currentTarget
    const formData = new FormData(form)
    const title = String(formData.get("title") ?? "").trim()
    const description = String(formData.get("description") ?? "").trim()
    const musicFile = formData.get("music_file")

    if (!title || !description) return
    if (!(musicFile instanceof File) || musicFile.size === 0) return

    setCreated(null)
    const result = await run(
      () => createChallenge({ title, description, challengeType, musicFile }),
      {
        fallbackError: UI_ERRORS.requestFailed,
        onSuccess: (challenge) => setCreated(challenge),
      }
    )
    if (result) form.reset()
  }

  return (
    <main className="min-h-[calc(100vh-4rem)] min-w-0 overflow-x-hidden bg-background text-foreground">
      <div className="mx-auto max-w-3xl px-4 py-10 md:py-14">
        <Link
          href="/music-challenge"
          className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          챌린지 목록
        </Link>

        <h1 className="mt-6 text-3xl font-semibold tracking-tight sm:text-4xl">
          챌린지 등록
        </h1>
        <p className="mt-4 text-base leading-8 text-muted-foreground">
          AI로 만든 음악을 올리면 사용자들이 도전할 수 있는 챌린지가 생성됩니다.
        </p>

        {!mounted && (
          <div
            className="mt-8 h-64 animate-pulse rounded-3xl bg-muted/40"
            role="status"
          >
            <span className="sr-only">권한을 확인하는 중입니다.</span>
          </div>
        )}

        {mounted && !isAdmin && (
          <p
            role="status"
            className="mt-8 rounded-2xl border border-border bg-muted/40 px-5 py-6 text-sm text-muted-foreground"
          >
            챌린지 등록은 운영자만 할 수 있습니다.
          </p>
        )}

        {mounted && isAdmin && (
          <form
            className="mt-8 space-y-6 rounded-3xl border border-border bg-card p-6"
            onSubmit={handleSubmit}
          >
            <div>
              <label htmlFor="title" className="text-sm font-medium">
                제목
              </label>
              <input
                id="title"
                name="title"
                type="text"
                required
                maxLength={100}
                placeholder="예) AI가 만든 발라드 따라부르기"
                className="mt-3 block w-full rounded-xl border border-border bg-background px-4 py-3 text-sm outline-none placeholder:text-muted-foreground focus:border-foreground/40"
              />
            </div>

            <div>
              <label htmlFor="description" className="text-sm font-medium">
                설명
              </label>
              <textarea
                id="description"
                name="description"
                required
                rows={4}
                maxLength={500}
                placeholder="어떤 점에 집중해서 부르면 좋은지 알려주세요."
                className="mt-3 block w-full resize-y rounded-xl border border-border bg-background px-4 py-3 text-sm outline-none placeholder:text-muted-foreground focus:border-foreground/40"
              />
            </div>

            <fieldset>
              <legend className="text-sm font-medium">챌린지 유형</legend>
              <div className="mt-3 flex flex-wrap gap-2">
                {CHALLENGE_TYPES.map((type) => (
                  <button
                    key={type}
                    type="button"
                    aria-pressed={challengeType === type}
                    onClick={() => setChallengeType(type)}
                    className={`rounded-full border px-4 py-2 text-sm transition-colors ${
                      challengeType === type
                        ? "border-neon-pink bg-neon-pink/15 text-white shadow-[0_0_16px_-4px_#ff2e97]"
                        : "border-border bg-background text-muted-foreground hover:bg-accent"
                    }`}
                  >
                    {CHALLENGE_TYPE_LABEL[type]}
                  </button>
                ))}
              </div>
            </fieldset>

            <div>
              <label htmlFor="music_file" className="text-sm font-medium">
                음원 파일
              </label>
              <input
                id="music_file"
                name="music_file"
                type="file"
                required
                accept="audio/*"
                className="mt-3 block w-full cursor-pointer rounded-xl border border-border bg-background px-4 py-3 text-sm text-muted-foreground file:mr-4 file:rounded-full file:border-0 file:bg-primary file:px-4 file:py-2 file:text-sm file:font-medium file:text-primary-foreground"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center justify-center gap-2 rounded-full bg-primary px-6 py-3.5 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-80 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Upload className="h-4 w-4" aria-hidden="true" />
              {loading ? "업로드하는 중…" : "챌린지 등록"}
            </button>

            {error && (
              <p role="status" className="text-sm text-muted-foreground">
                {error}
              </p>
            )}
          </form>
        )}

        {created && (
          <section
            className="mt-6 rounded-3xl border-2 border-foreground/15 bg-secondary p-6"
            role="status"
          >
            <h2 className="text-xl font-semibold">등록 완료</h2>
            <p className="mt-3 text-sm leading-7 text-muted-foreground">
              &ldquo;{created.title}&rdquo; 챌린지가 생성되었습니다. 노래방 화면에 음표와
              가사가 흘러가게 하려면 악보 스튜디오에서 Suno 스템과 가사를 올려 주세요.
            </p>
            <div className="mt-5 flex flex-wrap gap-3">
              <Link
                href={`/music-challenge/${created.id}/studio`}
                className="inline-flex items-center gap-2 rounded-full bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-80"
              >
                악보 스튜디오로
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Link>
              <Link
                href={`/music-challenge/${created.id}`}
                className="inline-flex items-center gap-2 rounded-full border border-border bg-background px-5 py-3 text-sm font-medium transition-colors hover:bg-accent"
              >
                등록한 챌린지 보기
              </Link>
            </div>
          </section>
        )}
      </div>
    </main>
  )
}
