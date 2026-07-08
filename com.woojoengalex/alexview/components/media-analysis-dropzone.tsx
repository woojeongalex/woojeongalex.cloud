"use client"

import { useCallback, useEffect, useId, useRef, useState } from "react"
import { FileVideo, Loader2, Upload, X } from "lucide-react"
import {
  analyzeMediaFile,
  isAnalyzableMedia,
  type VocalAnalysisResult,
} from "@/lib/analyze-media"
import { UI_ERRORS } from "@/lib/user-facing-error"

type DropPhase = "idle" | "dragover" | "ready" | "analyzing" | "done" | "error"

type DropzoneState = {
  phase: DropPhase
  file: File | null
  previewUrl: string | null
  errorMessage: string | null
}

const INITIAL_DROPZONE: DropzoneState = {
  phase: "idle",
  file: null,
  previewUrl: null,
  errorMessage: null,
}

export type MediaDropzoneCopy = {
  idleResetStatus: string
  fileReady: (fileName: string) => string
  analyzing: string
  done: (fileName: string, durationSec: number) => string
  dropTitle: string
  dropHint: string
  analyzeCta: string
}

export const VOCAL_DROPZONE_COPY: MediaDropzoneCopy = {
  idleResetStatus: "곡을 선택한 뒤 마이크 녹음 또는 영상·음원 파일을 끌어다 놓으세요.",
  fileReady: (name) =>
    `「${name}」이 준비되었습니다. 분석 시작을 누르면 영상·음원에서 보컬을 분석합니다.`,
  analyzing: "영상·음원에서 오디오를 추출해 음정·박자를 분석하는 중입니다…",
  done: (name, sec) =>
    `「${name}」 분석 완료 (${sec}초). 결과 카드가 갱신되었습니다.`,
  dropTitle: "영상·음원 파일을 여기에 끌어다 놓기",
  dropHint: "또는 클릭해 MP4, WebM, MOV, MP3, WAV 선택 (최대 10분)",
  analyzeCta: "이 영상·음원으로 분석하기",
}

export function instrumentDropzoneCopy(instrument: "guitar" | "piano"): MediaDropzoneCopy {
  const label = instrument === "guitar" ? "기타" : "피아노"
  return {
    idleResetStatus:
      instrument === "guitar"
        ? "기타 줄을 튕긴 뒤 마이크 녹음 또는 연주 영상·음원을 올려 주세요."
        : "건반을 누른 뒤 마이크 녹음 또는 연주 영상·음원을 올려 주세요.",
    fileReady: (name) =>
      `「${name}」 준비됨. 분석 시작을 누르면 ${label} 연주 피치를 추출합니다.`,
    analyzing: `${label} 연주 영상·음원에서 피치를 추출해 튜닝·음정을 분석하는 중입니다…`,
    done: (name, sec) =>
      `「${name}」 ${label} 연주 분석 완료 (${sec}초). 튜닝 결과가 갱신되었습니다.`,
    dropTitle: "연주 영상·음원을 여기에 끌어다 놓기",
    dropHint: "커버·연습 녹화 클립, MP3/WAV 등 (최대 10분)",
    analyzeCta: "이 영상·음원으로 연주 분석하기",
  }
}

type MediaAnalysisDropzoneProps = {
  copy: MediaDropzoneCopy
  disabled?: boolean
  onStatusMessage: (message: string) => void
  onAnalysisComplete: (result: VocalAnalysisResult) => void
  onClear?: () => void
}

export function MediaAnalysisDropzone({
  copy,
  disabled = false,
  onStatusMessage,
  onAnalysisComplete,
  onClear,
}: MediaAnalysisDropzoneProps) {
  const fileInputId = useId()
  const inputRef = useRef<HTMLInputElement>(null)
  const [drop, setDrop] = useState<DropzoneState>(INITIAL_DROPZONE)

  const patch = (next: Partial<DropzoneState>) =>
    setDrop((prev) => ({ ...prev, ...next }))

  const revokePreview = useCallback((url: string | null) => {
    if (url?.startsWith("blob:")) URL.revokeObjectURL(url)
  }, [])

  useEffect(() => {
    return () => revokePreview(drop.previewUrl)
  }, [drop.previewUrl, revokePreview])

  const reset = useCallback(() => {
    revokePreview(drop.previewUrl)
    setDrop(INITIAL_DROPZONE)
    onClear?.()
    onStatusMessage(copy.idleResetStatus)
  }, [copy.idleResetStatus, onClear, onStatusMessage, drop.previewUrl, revokePreview])

  const acceptFile = useCallback(
    (next: File) => {
      if (disabled) return
      if (!isAnalyzableMedia(next)) {
        patch({
          errorMessage: "MP4, WebM, MOV, MP3, WAV 등 영상·음원만 올릴 수 있습니다.",
          phase: "error",
        })
        return
      }
      revokePreview(drop.previewUrl)
      patch({
        file: next,
        previewUrl: URL.createObjectURL(next),
        phase: "ready",
        errorMessage: null,
      })
      onStatusMessage(copy.fileReady(next.name))
    },
    [copy, disabled, drop.previewUrl, onStatusMessage, revokePreview]
  )

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      e.stopPropagation()
      if (disabled) return
      const dropped = e.dataTransfer.files[0]
      if (dropped) acceptFile(dropped)
      else patch({ phase: drop.file ? "ready" : "idle" })
    },
    [acceptFile, disabled, drop.file]
  )

  const runAnalysis = async () => {
    if (!drop.file || disabled || drop.phase === "analyzing") return
    patch({ phase: "analyzing", errorMessage: null })
    onStatusMessage(copy.analyzing)

    try {
      const result = await analyzeMediaFile(drop.file)
      patch({ phase: "done" })
      onAnalysisComplete(result)
      onStatusMessage(copy.done(result.fileName, result.durationSec))
    } catch {
      patch({ phase: "error", errorMessage: UI_ERRORS.mediaAnalysisFailed })
      onStatusMessage(UI_ERRORS.mediaAnalysisFailed)
    }
  }

  const isVideo =
    drop.file?.type.startsWith("video/") ||
    Boolean(drop.file?.name.match(/\.(mp4|webm|mov|m4v)$/i))

  return (
    <div className="mt-6 space-y-4">
      <div
        onDragEnter={(e) => {
          e.preventDefault()
          if (!disabled) patch({ phase: "dragover" })
        }}
        onDragOver={(e) => {
          e.preventDefault()
          if (!disabled) patch({ phase: "dragover" })
        }}
        onDragLeave={(e) => {
          e.preventDefault()
          if (!e.currentTarget.contains(e.relatedTarget as Node)) {
            patch({ phase: drop.file ? "ready" : "idle" })
          }
        }}
        onDrop={onDrop}
        className="relative"
      >
        <label
          htmlFor={fileInputId}
          role="button"
          tabIndex={disabled ? -1 : 0}
          onKeyDown={(e) => {
            if (disabled) return
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault()
              inputRef.current?.click()
            }
          }}
          className={`block rounded-2xl border-2 border-dashed p-8 text-center transition-colors ${
            disabled
              ? "cursor-not-allowed border-zinc-200 bg-zinc-100 opacity-60"
              : drop.phase === "dragover"
                ? "cursor-copy border-zinc-950 bg-zinc-100"
                : "cursor-pointer border-zinc-300 bg-white hover:border-zinc-400 hover:bg-zinc-50"
          }`}
        >
          <input
            id={fileInputId}
            ref={inputRef}
            type="file"
            accept="video/*,audio/*,.mp4,.webm,.mov,.m4v,.mp3,.wav,.ogg,.m4a,.aac"
            className="sr-only"
            disabled={disabled}
            onChange={(e) => {
              const picked = e.target.files?.[0]
              if (picked) acceptFile(picked)
              e.target.value = ""
            }}
          />
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-zinc-100">
            {drop.phase === "analyzing" ? (
              <Loader2 className="h-6 w-6 animate-spin text-zinc-700" aria-hidden="true" />
            ) : (
              <Upload className="h-6 w-6 text-zinc-700" aria-hidden="true" />
            )}
          </div>
          <p className="mt-4 text-sm font-medium text-zinc-950">{copy.dropTitle}</p>
          <p className="mt-2 text-sm text-zinc-500">{copy.dropHint}</p>
        </label>
      </div>

      {drop.errorMessage && (
        <p className="text-sm text-red-600" role="status">
          {drop.errorMessage}
        </p>
      )}

      {drop.file && drop.previewUrl && (
        <div className="rounded-2xl border border-zinc-200 bg-zinc-50 p-4">
          <div className="flex items-start justify-between gap-3">
            <div className="flex min-w-0 items-center gap-2">
              <FileVideo className="h-5 w-5 shrink-0 text-zinc-700" aria-hidden="true" />
              <div className="min-w-0 text-left">
                <p className="truncate text-sm font-medium text-zinc-950">{drop.file.name}</p>
                <p className="text-xs text-zinc-500">
                  {(drop.file.size / (1024 * 1024)).toFixed(1)} MB
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                reset()
              }}
              disabled={drop.phase === "analyzing"}
              className="rounded-lg p-1 text-zinc-500 transition-colors hover:bg-zinc-200 hover:text-zinc-950 disabled:opacity-40"
              aria-label="파일 제거"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {isVideo ? (
            <video
              src={drop.previewUrl}
              controls
              className="mt-4 aspect-video w-full rounded-xl bg-black object-contain"
              playsInline
            />
          ) : (
            <audio src={drop.previewUrl} controls className="mt-4 w-full" />
          )}

          <div className="mt-4 flex flex-col gap-3 sm:flex-row">
            <button
              type="button"
              onClick={runAnalysis}
              disabled={disabled || drop.phase === "analyzing"}
              className="inline-flex flex-1 items-center justify-center gap-2 rounded-xl bg-zinc-950 px-5 py-3 text-sm font-medium text-white transition-colors hover:bg-zinc-800 disabled:cursor-not-allowed disabled:bg-zinc-300"
            >
              {drop.phase === "analyzing" ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                  분석 중…
                </>
              ) : (
                copy.analyzeCta
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}