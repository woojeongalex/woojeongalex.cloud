"use client"

import { useCallback, useRef, useState } from "react"

type RecordingState = "idle" | "recording" | "done"

/** 마이크 녹음 시작/종료 — 악기·스피치 페이지 공통 */
export function useMicRecording() {
  const [recording, setRecording] = useState<RecordingState>("idle")
  const [durationSec, setDurationSec] = useState(0)
  const recorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const startedAtRef = useRef(0)

  const stopStream = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop())
    streamRef.current = null
  }, [])

  const start = useCallback(async (): Promise<boolean> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      const recorder = new MediaRecorder(stream)
      recorderRef.current = recorder
      startedAtRef.current = Date.now()
      recorder.start()
      setRecording("recording")
      return true
    } catch {
      return false
    }
  }, [])

  const stop = useCallback(
    async (onComplete: (seconds: number) => Promise<void>) => {
      const recorder = recorderRef.current
      if (!recorder || recording !== "recording") return

      const sec = Math.max(1, Math.round((Date.now() - startedAtRef.current) / 1000))
      setDurationSec(sec)
      recorder.onstop = async () => {
        stopStream()
        setRecording("done")
        await onComplete(sec)
      }
      recorder.stop()
    },
    [recording, stopStream]
  )

  const reset = useCallback(() => {
    setRecording("idle")
    setDurationSec(0)
  }, [])

  return { recording, durationSec, start, stop, reset }
}
