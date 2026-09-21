"use client"

import { useCallback, useRef, useState } from "react"

type RecordingState = "idle" | "recording" | "done"

/**
 * 마이크 녹음 시작/종료 — 악기·스피치·챌린지 공통.
 *
 * onComplete 의 두 번째 인자로 녹음된 오디오를 넘긴다. 기존 호출부는
 * 첫 번째 인자만 받으므로 그대로 동작한다(인자를 덜 받는 함수는 호환된다).
 */
export function useMicRecording() {
  const [recording, setRecording] = useState<RecordingState>("idle")
  const [durationSec, setDurationSec] = useState(0)
  const [audio, setAudio] = useState<Blob | null>(null)
  const recorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const chunksRef = useRef<Blob[]>([])
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
      chunksRef.current = []
      setAudio(null)
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }
      startedAtRef.current = Date.now()
      recorder.start()
      setRecording("recording")
      return true
    } catch {
      return false
    }
  }, [])

  const stop = useCallback(
    async (onComplete: (seconds: number, audio: Blob) => Promise<void>) => {
      const recorder = recorderRef.current
      if (!recorder || recording !== "recording") return

      const sec = Math.max(1, Math.round((Date.now() - startedAtRef.current) / 1000))
      setDurationSec(sec)
      recorder.onstop = async () => {
        const recorded = new Blob(chunksRef.current, {
          type: recorder.mimeType || "audio/webm",
        })
        setAudio(recorded)
        stopStream()
        setRecording("done")
        await onComplete(sec, recorded)
      }
      recorder.stop()
    },
    [recording, stopStream]
  )

  const reset = useCallback(() => {
    setRecording("idle")
    setDurationSec(0)
    setAudio(null)
    chunksRef.current = []
  }, [])

  return { recording, durationSec, audio, start, stop, reset }
}
