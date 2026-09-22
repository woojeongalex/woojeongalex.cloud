"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { ArrowLeft } from "lucide-react"
import { LoadingBlock, StatusNote } from "@/components/common/status-note"
import { useUserSession } from "@/hooks/use-user-session"
import {
  fetchChallenge,
  fetchChart,
  type Challenge,
  type Chart,
} from "@/lib/music-challenge-api"
import { toUserFacingMessage, UI_ERRORS } from "@/lib/user-facing-error"
import { LyricsSyncPanel } from "./lyrics-sync-panel"
import { StemsPanel } from "./stems-panel"
import { useAudioClock } from "./use-audio-clock"

const POLL_MS = 2000

type ChartStudioProps = {
  challengeId: number
}

/**
 * 관리자용 악보 스튜디오 — 스템을 올려 정답 멜로디를 만들고 가사 타이밍을 찍는다.
 *
 * 화면의 권한 확인은 편의일 뿐이고, 실제 차단은 백엔드 require_admin 이 한다.
 */
export function ChartStudio({ challengeId }: ChartStudioProps) {
  const user = useUserSession()
  const [mounted, setMounted] = useState(false)
  const [challenge, setChallenge] = useState<Challenge | null>(null)
  const [chart, setChart] = useState<Chart | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => setMounted(true), [])

  useEffect(() => {
    let alive = true
    Promise.all([fetchChallenge(challengeId), fetchChart(challengeId)])
      .then(([c, ch]) => {
        if (!alive) return
        setChallenge(c)
        setChart(ch)
      })
      .catch((e) => {
        if (alive) setError(toUserFacingMessage(e, UI_ERRORS.challengeLoadFailed))
      })
    return () => {
      alive = false
    }
  }, [challengeId])

  // 추출은 서버 백그라운드에서 돌므로 끝날 때까지 상태를 확인한다.
  const processing = chart?.status === "processing"
  useEffect(() => {
    if (!processing) return
    const id = setInterval(() => {
      fetchChart(challengeId)
        .then(setChart)
        .catch(() => {
          // 한 번 실패해도 다음 주기에 다시 묻는다.
        })
    }, POLL_MS)
    return () => clearInterval(id)
  }, [processing, challengeId])

  const isAdmin = user?.role === "admin"
  // 플레이어는 권한 확인과 데이터 로딩이 모두 끝나야 그려진다. 그 시점을 키로 넘겨야
  // 세션이 데이터보다 늦게 확인돼도 재생 위치 리스너가 붙는다.
  const playerSrc = mounted && isAdmin && chart ? (challenge?.music_url ?? null) : null
  const { audioRef, time } = useAudioClock(playerSrc)

  return (
    <main className="min-h-[calc(100vh-4rem)] min-w-0 overflow-x-hidden bg-background text-foreground">
      <div className="mx-auto max-w-5xl px-4 py-10 md:py-14">
        <Link
          href={`/music-challenge/${challengeId}`}
          className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          챌린지로 돌아가기
        </Link>

        <p className="mt-6 text-sm font-medium text-muted-foreground">악보 스튜디오</p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight sm:text-4xl">
          {challenge?.title ?? "불러오는 중…"}
        </h1>
        <p className="mt-3 text-base leading-7 text-muted-foreground">
          도전 화면에 흘러갈 정답 음표와 가사를 준비합니다.
        </p>

        {!mounted && <LoadingBlock label="불러오는 중입니다." className="mt-8 h-40" />}

        {mounted && !isAdmin && (
          <StatusNote className="mt-8">관리자만 사용할 수 있는 화면입니다.</StatusNote>
        )}

        {mounted && isAdmin && error && <StatusNote className="mt-8">{error}</StatusNote>}

        {mounted && isAdmin && !error && (!challenge || !chart) && (
          <LoadingBlock label="악보를 불러오는 중입니다." className="mt-8 h-40" />
        )}

        {mounted && isAdmin && challenge && chart && (
          <div className="mt-8 space-y-6">
            {/* 두 단계가 같은 재생 위치를 쓰므로 플레이어는 위에 하나만 둔다. */}
            <div className="sticky top-20 z-10 rounded-2xl border border-border bg-background/95 p-3 backdrop-blur">
              <p className="mb-2 text-xs text-muted-foreground">원곡 플레이어</p>
              <audio
                ref={audioRef}
                src={challenge.music_url}
                controls
                preload="auto"
                className="w-full"
              />
            </div>

            <StemsPanel
              challengeId={challengeId}
              chart={chart}
              currentTime={time}
              onChartChange={setChart}
            />
            {chart.melody_source === "vocal" ? (
              <LyricsSyncPanel
                challengeId={challengeId}
                savedLines={chart.lyric_lines}
                audioRef={audioRef}
                currentTime={time}
                onChartChange={setChart}
              />
            ) : (
              <StatusNote>
                연주곡이라 가사 단계는 건너뜁니다. 도전 화면에는 음표만 흘러갑니다.
              </StatusNote>
            )}
          </div>
        )}
      </div>
    </main>
  )
}
