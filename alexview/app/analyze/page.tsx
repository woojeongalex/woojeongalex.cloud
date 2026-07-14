"use client"

import { useCallback, useMemo, useRef, useState } from "react"
import {
  CheckCircle2,
  FileVideo,
  Mic,
  Music4,
  Radio,
  Search,
  Sparkles,
  StopCircle,
  Waves,
} from "lucide-react"
import { VOCAL_DROPZONE_COPY } from "@/components/media-analysis-dropzone"
import { PageBackButton } from "@/components/page-back-button"
import { VocalVideoDropzone } from "@/components/vocal-video-dropzone"
import type { VocalAnalysisResult } from "@/lib/analyze-media"
import { fetchSongMrSearch, type SongMrHit } from "@/lib/song-mr-api"
import { postSingEvaluation } from "@/lib/sing-evaluation-api"
import { UserFacingError, UI_ERRORS } from "@/lib/user-facing-error"

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000"

const ANALYZE_VOCAL_DROPZONE_COPY = {
  ...VOCAL_DROPZONE_COPY,
  idleResetStatus:
    "노래를 검색해 MR을 선택한 뒤 마이크 녹음 또는 영상·음원을 끌어다 놓으세요.",
} as const

type SongFindState = {
  submittedQuery: string
  selectedCatalogSongId: string | null
  hits: SongMrHit[]
}

const EMPTY_SONG_FIND: SongFindState = {
  submittedQuery: "",
  selectedCatalogSongId: null,
  hits: [],
}

export default function AnalyzePage() {
  const [songFind, setSongFind] = useState<SongFindState>(EMPTY_SONG_FIND)
  const [searchLoading, setSearchLoading] = useState(false)
  const [recordingState, setRecordingState] = useState<"idle" | "recording" | "done">("idle")
  const [inputSource, setInputSource] = useState<"none" | "mic" | "video">("none")
  const [analysisResult, setAnalysisResult] = useState<VocalAnalysisResult | null>(null)
  const [statusMessage, setStatusMessage] = useState(
    "노래 제목으로 검색해 MR을 선택한 뒤 마이크 녹음 또는 영상·음원을 올려 주세요."
  )
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)

  const selectedSong = useMemo((): SongMrHit | null => {
    if (!songFind.selectedCatalogSongId) return null
    return (
      songFind.hits.find((h) => h.catalog_song_id === songFind.selectedCatalogSongId) ?? null
    )
  }, [songFind.selectedCatalogSongId, songFind.hits])

  const selectedSongRef = useRef<SongMrHit | null>(null)
  selectedSongRef.current = selectedSong

  const persistVocalEvaluationToNeon = useCallback(
    async (analysis: VocalAnalysisResult, source: "mic" | "video") => {
      const song = selectedSongRef.current
      if (!song) return
      try {
        await postSingEvaluation({
          catalogSongId: song.catalog_song_id,
          mrSearchListId: song.id,
          inputSource: source,
          pitchScore: analysis.pitchScore,
          rhythmScore: analysis.rhythmScore,
          vocalGrade: analysis.vocalGrade,
          summary: analysis.summary,
          fileName: analysis.fileName,
          durationSec: analysis.durationSec,
        })
      } catch (e) {
        setStatusMessage(e instanceof UserFacingError ? e.message : UI_ERRORS.requestFailed)
      }
    },
    []
  )

  const handleSongSearch = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const q = String(formData.get("songQuery") ?? "").trim()
    setSongFind({ submittedQuery: q, selectedCatalogSongId: null, hits: [] })
    if (!q) { setStatusMessage("노래 제목을 입력하고 검색해 주세요."); return }
    setSearchLoading(true)
    try {
      const payload = await fetchSongMrSearch(q)
      setSongFind((prev) => ({ ...prev, hits: payload.hits }))
      setStatusMessage(
        payload.count === 0
          ? "일치하는 노래·MR이 없습니다. 다른 제목으로 검색해 주세요."
          : `검색 결과 ${payload.count}건이 저장되었습니다. MR을 사용할 곡을 눌러 선택해 주세요.`
      )
    } catch (err) {
      setStatusMessage(err instanceof UserFacingError ? err.message : UI_ERRORS.requestFailed)
    } finally {
      setSearchLoading(false)
    }
  }

  const pickSong = (hit: SongMrHit) => {
    setSongFind((prev) => ({ ...prev, selectedCatalogSongId: hit.catalog_song_id }))
    setStatusMessage(`「${hit.title}」 MR: ${hit.mr_track_name}`)
  }

  const result = analysisResult ?? {
    pitchScore: 92,
    rhythmScore: 88,
    vocalGrade: "A-",
    summary: selectedSong
      ? "MR을 선택한 뒤 마이크 녹음 또는 영상·음원을 업로드하면 분석 결과가 표시됩니다."
      : "노래 제목으로 검색해 MR을 고른 다음 입력을 진행하면 분석 결과가 표시됩니다.",
    fileName: "",
    durationSec: 0,
  }

  const inputLabel =
    recordingState === "recording"
      ? "녹음 중"
      : inputSource === "video"
        ? "영상·음원 분석 완료"
        : inputSource === "mic" && recordingState === "done"
          ? "마이크 분석 완료"
          : "준비 완료"

  const startRecording = async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      setStatusMessage("이 브라우저는 마이크 녹음을 지원하지 않습니다.")
      return
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      mediaRecorderRef.current = new MediaRecorder(stream)
      mediaRecorderRef.current.start()
      setRecordingState("recording")
      setInputSource("mic")
      setAnalysisResult(null)
      setStatusMessage("녹음 중입니다. 노래를 부른 뒤 정지 버튼을 눌러 주세요.")
    } catch {
      setStatusMessage(UI_ERRORS.micStartFailed)
    }
  }

  const stopRecording = async () => {
    mediaRecorderRef.current?.stop()
    streamRef.current?.getTracks().forEach((track) => track.stop())
    mediaRecorderRef.current = null
    streamRef.current = null
    setRecordingState("done")
    setInputSource("mic")
    const analysis: VocalAnalysisResult = {
      pitchScore: 90,
      rhythmScore: 86,
      vocalGrade: "A-",
      summary: "마이크 녹음이 저장되었습니다. 백엔드 연동 시 선택한 곡과 비교해 음정·박자를 계산합니다.",
      fileName: "마이크 녹음",
      durationSec: 0,
    }
    setAnalysisResult(analysis)
    setStatusMessage("녹음이 종료되었습니다. 분석 결과가 갱신되었습니다.")
    await persistVocalEvaluationToNeon(analysis, "mic")
  }

  const handleVideoAnalysis = async (result: VocalAnalysisResult) => {
    setInputSource("video")
    setRecordingState("done")
    setAnalysisResult(result)
    await persistVocalEvaluationToNeon(result, "video")
  }

  const clearVideoInput = () => {
    if (inputSource === "video") {
      setInputSource("none")
      setRecordingState("idle")
      setAnalysisResult(null)
    }
  }

  return (
    <main className="min-h-[calc(100vh-4rem)] min-w-0 overflow-x-hidden bg-background px-4 py-8 text-foreground sm:py-10">
      <div className="mx-auto flex w-full min-w-0 max-w-6xl flex-col gap-6 sm:gap-8">
        <PageBackButton />

        {/* HERO */}
        <section className="rounded-2xl border border-border bg-card px-4 py-8 sm:rounded-[2rem] sm:px-6 sm:py-10 md:px-10">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-muted px-3 py-1 text-[11px] font-semibold tracking-wide text-muted-foreground">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-foreground" />
            ANALYZE SESSION
          </span>
          <h1 className="mt-4 text-2xl font-semibold leading-snug tracking-tight text-foreground sm:text-4xl lg:text-5xl">
            <span className="block">노래 찾기(MR), 마이크·영상 입력,</span>
            <span className="block">분석 결과를 하나의 화면에서 연결합니다.</span>
          </h1>
          <p className="mt-4 max-w-3xl text-sm leading-7 text-muted-foreground sm:text-base">
            노래 제목으로 MR을 찾아 고르고, 마이크로 부르거나 연습 영상·음원을 올려 AI가 음정과
            박자를 분석한 뒤 코칭 피드백을 받을 수 있습니다.
          </p>
        </section>

        <section className="grid min-w-0 gap-6 lg:grid-cols-2 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
          <div className="space-y-6">
            {/* STEP 1 */}
            <article className="rounded-3xl border border-border bg-secondary p-6">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-border bg-muted">
                  <Music4 className="h-5 w-5 text-foreground" aria-hidden="true" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">1단계</p>
                  <h2 className="text-2xl font-semibold text-foreground">노래 찾기</h2>
                </div>
              </div>

              <form className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-end" onSubmit={handleSongSearch}>
                <div className="min-w-0 flex-1">
                  <label htmlFor="song-query" className="sr-only">노래 제목</label>
                  <input
                    id="song-query"
                    name="songQuery"
                    type="search"
                    placeholder="예: 봄날, 밤편지, Defying Gravity"
                    autoComplete="off"
                    className="w-full rounded-2xl border border-border bg-card px-4 py-3 text-sm text-foreground outline-none"
                  />
                </div>
                <button
                  type="submit"
                  disabled={searchLoading}
                  className="inline-flex shrink-0 items-center justify-center gap-2 rounded-full bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-80 disabled:opacity-50"
                >
                  <Search className="h-4 w-4" aria-hidden="true" />
                  {searchLoading ? "검색 중…" : "MR 검색"}
                </button>
              </form>

              {!songFind.submittedQuery.trim() ? (
                <p className="mt-6 text-sm leading-6 text-muted-foreground" role="status">
                  노래 제목을 입력한 뒤 검색하면 등록된 MR 정보가 있는 곡 목록이 표시됩니다.
                </p>
              ) : searchLoading ? (
                <p className="mt-6 text-sm leading-6 text-muted-foreground" role="status">검색 중입니다…</p>
              ) : songFind.hits.length === 0 ? (
                <p className="mt-6 text-sm leading-6 text-muted-foreground" role="status">
                  &quot;{songFind.submittedQuery}&quot;에 맞는 곡을 찾지 못했습니다.
                </p>
              ) : (
                <div className="mt-6 grid grid-cols-1 gap-4 min-[420px]:grid-cols-2 lg:grid-cols-3">
                  {songFind.hits.map((song) => {
                    const active = songFind.selectedCatalogSongId === song.catalog_song_id
                    return (
                      <button
                        key={`${song.catalog_song_id}-${song.id}`}
                        type="button"
                        onClick={() => pickSong(song)}
                        className={`rounded-2xl border p-4 text-left transition-colors ${
                          active
                            ? "border-foreground bg-muted"
                            : "border-border bg-card hover:border-foreground/40"
                        }`}
                      >
                        <p className="text-base font-semibold text-foreground">{song.title}</p>
                        <p className="mt-1 text-sm text-muted-foreground">{song.artist}</p>
                        <div className="mt-4 space-y-1 text-xs text-muted-foreground">
                          <p>BPM {song.bpm}</p>
                          <p>{song.song_key}</p>
                          <p>{song.range_label}</p>
                          <p className={`pt-2 text-xs font-medium ${active ? "text-foreground" : "text-muted-foreground"}`}>
                            MR · {song.mr_track_name}
                          </p>
                          <p>{song.mr_description}</p>
                        </div>
                      </button>
                    )
                  })}
                </div>
              )}
            </article>

            {/* STEP 2 */}
            <article className="rounded-3xl border border-border bg-secondary p-6">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-border bg-muted">
                  <Mic className="h-5 w-5 text-foreground" aria-hidden="true" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">2단계</p>
                  <h2 className="text-2xl font-semibold text-foreground">마이크 또는 영상·음원</h2>
                </div>
              </div>

              <p className="mt-4 text-sm leading-6 text-muted-foreground">{statusMessage}</p>

              <div className="mt-6 rounded-2xl border border-border bg-card p-5">
                <p className="text-sm font-medium text-foreground">마이크로 직접 부르기</p>
                <div className="mt-4 flex flex-col gap-3 sm:flex-row">
                  <button
                    type="button"
                    onClick={startRecording}
                    disabled={
                      recordingState === "recording" ||
                      (inputSource === "video" && recordingState === "done")
                    }
                    className="inline-flex items-center justify-center gap-2 rounded-full bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-80 disabled:opacity-40"
                  >
                    <Radio className="h-4 w-4" aria-hidden="true" />
                    녹음 시작
                  </button>
                  <button
                    type="button"
                    onClick={stopRecording}
                    disabled={recordingState !== "recording"}
                    className="inline-flex items-center justify-center gap-2 rounded-full border border-border px-5 py-3 text-sm font-medium text-muted-foreground transition-colors disabled:opacity-40"
                  >
                    <StopCircle className="h-4 w-4" aria-hidden="true" />
                    녹음 정지
                  </button>
                </div>
              </div>

              <div className="mt-6 rounded-2xl border border-border p-5">
                <div className="flex items-center gap-2">
                  <FileVideo className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
                  <p className="text-sm font-medium text-foreground">영상·음원 드래그 앤 드롭</p>
                </div>
                <p className="mt-2 text-sm text-muted-foreground">
                  커버 영상, 연습 녹화, MR 없는 클립 등에서 보컬 트랙을 분석합니다.
                </p>
                <VocalVideoDropzone
                  copy={ANALYZE_VOCAL_DROPZONE_COPY}
                  disabled={recordingState === "recording"}
                  onStatusMessage={setStatusMessage}
                  onAnalysisComplete={handleVideoAnalysis}
                  onClear={clearVideoInput}
                />
              </div>
            </article>

            {/* STEP 3 */}
            <article className="rounded-3xl border border-border bg-secondary p-6">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-border bg-muted">
                  <Sparkles className="h-5 w-5 text-foreground" aria-hidden="true" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">3단계</p>
                  <h2 className="text-2xl font-semibold text-foreground">분석 결과</h2>
                </div>
              </div>

              <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
                <ResultCard title="음정 정확도" value={`${result.pitchScore}%`} description="불안정 구간 자동 감지" />
                <ResultCard title="박자 정확도" value={`${result.rhythmScore}%`} description="빠른/느린 구간 시각화" />
                <ResultCard
                  title="AI 피드백"
                  value={result.vocalGrade}
                  description={analysisResult ? result.summary : "호흡과 발성 개선 제안"}
                />
              </div>

              <div className="mt-6 rounded-2xl border border-border bg-card p-5">
                <div className="flex items-center gap-2 text-sm font-medium text-foreground">
                  <Waves className="h-4 w-4" aria-hidden="true" />
                  선택된 곡 기준 분석 준비
                </div>
                <p className="mt-3 text-sm leading-6 text-muted-foreground">
                  <span className="font-semibold text-foreground">
                    {selectedSong?.title ?? "MR 미선택"}
                  </span>
                  {analysisResult?.fileName ? ` · 입력: ${analysisResult.fileName}` : ""}
                  {selectedSong ? `의 원곡 BPM·키를 기준으로 ` : " — MR을 선택하면 "}
                  {inputSource === "video" ? "영상·음원" : "마이크"} 보컬과 비교합니다.
                  {analysisResult ? ` ${result.summary}` : ""}
                </p>
              </div>
            </article>
          </div>

          <aside className="space-y-6">
            {/* 선택된 곡 */}
            <article className="rounded-3xl border border-border bg-secondary p-6">
              <p className="text-sm font-medium text-muted-foreground">현재 선택</p>
              {selectedSong ? (
                <>
                  <h2 className="mt-2 text-2xl font-semibold text-foreground">{selectedSong.title}</h2>
                  <p className="mt-1 text-sm text-muted-foreground">{selectedSong.artist}</p>
                  <div className="mt-6 rounded-2xl border border-border bg-card px-4 py-3">
                    <p className="text-xs font-mono uppercase tracking-wide text-muted-foreground">MR</p>
                    <p className="mt-2 text-sm font-semibold text-foreground">{selectedSong.mr_track_name}</p>
                    <p className="mt-1 text-sm leading-6 text-muted-foreground">{selectedSong.mr_description}</p>
                  </div>
                  <dl className="mt-6 space-y-4 text-sm">
                    {[
                      { label: "DB 기록 id", value: selectedSong.id, mono: true },
                      { label: "BPM", value: selectedSong.bpm },
                      { label: "Key", value: selectedSong.song_key },
                      { label: "상태", value: inputLabel },
                    ].map(({ label, value, mono }) => (
                      <div key={label} className="flex flex-col gap-0.5 sm:flex-row sm:items-center sm:justify-between sm:gap-3">
                        <dt className="text-muted-foreground">{label}</dt>
                        <dd className={`font-medium text-foreground ${mono ? "break-all font-mono text-xs" : ""}`}>{value}</dd>
                      </div>
                    ))}
                  </dl>
                </>
              ) : (
                <p className="mt-3 text-sm leading-6 text-muted-foreground" role="status">
                  검색 결과에서 MR을 사용할 노래 카드를 눌러 선택해 주세요.
                </p>
              )}
            </article>

            {/* API 연결 배너 */}
            <article className="rounded-3xl border-2 border-foreground/15 bg-secondary p-6">
              <div className="flex items-center gap-2 text-sm font-medium text-foreground">
                <CheckCircle2 className="h-4 w-4" aria-hidden="true" />
                백엔드 API 연결 배너
              </div>
              <h2 className="mt-3 text-xl font-semibold text-foreground">
                이 화면은 바로 API와 연결할 수 있게 설계했습니다.
              </h2>
              <div className="mt-6 space-y-3 text-sm">
                <ApiRow label="MR 검색·DB 저장" value={`${apiBaseUrl}/api/songs/search?q=`} />
                <ApiRow label="보컬 분석 결과 저장" value={`${apiBaseUrl}/api/music/sing-evaluation`} />
                <ApiRow label="곡 목록 조회" value={`${apiBaseUrl}/songs`} />
                <ApiRow label="음원 분석 요청" value={`${apiBaseUrl}/analysis/songs/:songId`} />
                <ApiRow label="녹음 업로드" value={`${apiBaseUrl}/analysis/recordings`} />
                <ApiRow label="영상·음원 업로드" value={`${apiBaseUrl}/analysis/media-upload`} />
                <ApiRow label="결과 조회" value={`${apiBaseUrl}/analysis/results/:resultId`} />
              </div>
            </article>

            {/* 추천 배너 */}
            <article className="rounded-3xl border border-border bg-secondary p-6">
              <div className="flex items-center gap-2 text-sm font-medium text-foreground">
                <Sparkles className="h-4 w-4" aria-hidden="true" />
                추천 배너
              </div>
              <h2 className="mt-3 text-xl font-semibold text-foreground">
                분석 결과를 바탕으로 추천 장르와 노래를 제안합니다.
              </h2>
              <p className="mt-4 text-sm leading-6 text-muted-foreground">
                음정 안정성, 박자 정확도, 발성 패턴을 기반으로 잘 맞는 장르와 다음에 도전하면 좋은 추천 곡을 안내합니다.
              </p>
              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                {[
                  { label: "추천 장르", value: "발라드, 뮤지컬 넘버" },
                  { label: "추천 곡", value: "밤편지, Defying Gravity" },
                ].map(({ label, value }) => (
                  <div key={label} className="rounded-2xl border border-border bg-card p-4">
                    <p className="text-xs font-mono uppercase tracking-wide text-muted-foreground">Recommendation</p>
                    <p className="mt-2 text-sm font-semibold text-foreground">{label}</p>
                    <p className="mt-1 text-sm text-muted-foreground">{value}</p>
                  </div>
                ))}
              </div>
            </article>
          </aside>
        </section>
      </div>
    </main>
  )
}

function ResultCard({ title, value, description }: { title: string; value: string; description: string }) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5">
      <p className="text-sm text-muted-foreground">{title}</p>
      <p className="mt-3 break-words text-3xl font-semibold text-foreground">{value}</p>
      <p className="mt-2 text-sm leading-6 text-muted-foreground">{description}</p>
    </div>
  )
}

function ApiRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-background p-3">
      <p className="text-xs font-mono uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className="mt-1 break-all font-mono text-xs font-medium text-foreground">{value}</p>
    </div>
  )
}
